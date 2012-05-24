import sys
import time
import logging

from utils.sql import query_to_dicts, execute_sql, query_to_tuples
from mturk.main.management.commands.crawler_common import grab_error

log = logging.getLogger('__init__')


def clean_duplicates():

    ids = query_to_dicts("select group_id from main_hitgroupcontent group by group_id having count(*) > 1;")

    for id in ids:
        print "deleting %s" % id['group_id']
        logging.info("deleting %s" % id['group_id'])

        execute_sql("""delete from main_hitgroupstatus where
                        hit_group_content_id  in (
                            select id from main_hitgroupcontent where id !=
                                (select min(id) from main_hitgroupcontent where group_id = '%s')
                        and group_id = '%s');
        """ % (id['group_id'], id['group_id']))

        execute_sql("""delete from main_hitgroupcontent where
                        id != (select min(id) from main_hitgroupcontent where group_id = '%s') and group_id = '%s'
                    """ % (id['group_id'], id['group_id']))

    execute_sql('commit;')


def calculate_first_crawl_id():

    progress = 10
    results = query_to_dicts("select id from main_hitgroupcontent where first_crawl_id is null")
    logging.info('got missing ids results')
    for i, r in enumerate(results):
        logging.info("\tprocessing %s" % r['id'])
        execute_sql("""update main_hitgroupcontent p set first_crawl_id =
            (select min(crawl_id) from main_hitgroupstatus where hit_group_content_id = p.id)
            where
                id = %s
        """ % r['id'])

        if i % progress == 0:
            execute_sql('commit;')
            logging.info("updated %s main_hitgroupcontent rows with first_crawl_id" % i)

    execute_sql('commit;')


def update_mviews():

    missing_crawls = query_to_tuples("""select id, start_time
        from main_crawl p
    where
        p.success = true and
        not exists (select id from main_crawlagregates where crawl_id = p.id ) and
        old_id is null and
        groups_downloaded > 200 and
        has_hits_mv = false
    order by id desc""")

    for row in missing_crawls:

        crawl_id, start_time = row

        logging.info("inserting missing crawl: %s" % crawl_id)

        execute_sql("delete from hits_mv where crawl_id = %s" % crawl_id)

        execute_sql("""INSERT INTO
                hits_mv
            SELECT p.id AS status_id, q.id AS content_id, p.group_id, p.crawl_id,
                TIMESTAMP '%s',
                q.requester_id, p.hits_available, p.page_number, p.inpage_position, p.hit_expiration_date, q.reward, q.time_alloted, null, q.is_spam
            FROM
                main_hitgroupstatus p
            JOIN
                main_hitgroupcontent q ON (q.group_id::text = p.group_id::text AND p.hit_group_content_id = q.id)
            WHERE
                p.crawl_id = %s;
        """ % (start_time, crawl_id))

        execute_sql("update main_crawl set has_hits_mv = true where id = %s" % crawl_id)

        execute_sql('commit;')

    # execute_sql("""
    #     INSERT INTO
    #         hits_mv (crawl_id, status_id, content_id, group_id, start_time,
    #         requester_id, hits_available, page_number, inpage_position,
    #         hit_expiration_date, reward, time_alloted)
    #     SELECT
    #         h.crawl_id + 1, h.status_id, h.content_id, h.group_id, h.start_time,
    #         h.requester_id, h.hits_available, h.page_number, h.inpage_position,
    #         h.hit_expiration_date, h.reward, h.time_alloted
    #     FROM
    #         hits_mv h
    #     WHERE
    #         NOT exists(select group_id from hits_mv where group_id=h.group_id and crawl_id = (h.crawl_id + 1))
    #         AND exists(select group_id from hits_mv where group_id=h.group_id and crawl_id = (h.crawl_id + 2))
    #         AND (hits_available * reward) > 350
    #         AND start_time > now() - interval '2 days'
    #     ;
    # """)
    # execute_sql('commit;')


def update_diffs(limit=100):
    start_time = time.time()
    execute_sql("""
        UPDATE hits_mv
            SET hits_diff = diffs.hits_diff
        FROM
            (SELECT
                group_id, crawl_id,
                    hits_available -
                    COALESCE(lag(hits_available) over (partition BY group_id ORDER BY crawl_id), 0)
                    AS hits_diff
            FROM hits_mv
            WHERE
                hits_diff is NULL
            AND crawl_id in
                (SELECT DISTINCT crawl_id
                FROM hits_mv
                WHERE hits_diff is NULL
                ORDER BY crawl_id DESC LIMIT %s)

            ) AS diffs

        WHERE (diffs.group_id = hits_mv.group_id) AND (diffs.crawl_id = hits_mv.crawl_id);""",
        (int(limit), ))
    execute_sql('commit;')

    log.debug('Updated diffs for %s crawls in %s\n%s', limit, (time.time() - start_time))


def update_first_occured_agregates():

    missing_crawls = query_to_tuples("""select id from main_crawl p where p.success = true and not exists (select crawl_id from main_hitgroupfirstoccurences where crawl_id = p.id );""")

    for row in missing_crawls:

        crawl_id = row[0]
        logging.info("inserting missing crawl into main_hitgroupfirstoccurences: %s" % crawl_id)

        execute_sql("""INSERT INTO
                main_hitgroupfirstoccurences (reward, group_content_id,
                    crawl_id, requester_name, group_status_id, occurrence_date,
                    requester_id, group_id, hits_available, id)
                    select
                        p.reward,
                        p.id,
                        q.crawl_id,
                        p.requester_name,
                        q.id,
                        p.occurrence_date,
                        p.requester_id,
                        p.group_id,
                        q.hits_available,
                        nextval('main_hitgroupfirstoccurences_id_seq'::regclass)
                    from main_hitgroupcontent p join main_hitgroupstatus q
                        on( p.first_crawl_id = q.crawl_id and q.hit_group_content_id = p.id )
                        where q.crawl_id = %s;""" % crawl_id)

        execute_sql('commit;')


def update_crawl_agregates(commit_threshold=10, only_new=True):

    results = None

    if only_new:
        results = query_to_dicts("select id from main_crawl p where old_id is null and not exists(select id from main_crawlagregates where crawl_id = p.id)")
    else:
        results = query_to_dicts("select id from main_crawl p where not exists(select id from main_crawlagregates where crawl_id = p.id)")

    logging.info("got results")

    for i, row in enumerate(results):
        try:

            execute_sql("""
            INSERT INTO
                main_crawlagregates (hits, start_time, reward, crawl_id, id,
                    projects, spam_projects)
            SELECT
                sum(hits_available) as "hits",
                start_time,
                sum(reward * hits_available) as "reward",
                crawl_id,
                nextval('main_crawlagregates_id_seq'),
                count(*) as "count",
                0
            FROM
                (SELECT DISTINCT ON (group_id) * FROM hits_mv WHERE crawl_id = %s) AS p
            GROUP BY
                crawl_id, start_time
            """, row['id'])

            execute_sql("""UPDATE main_crawlagregates
                set spam_projects =
                    ( select count(*) from hits_mv where crawl_id = %s and is_spam = true )
                where crawl_id = %s""" % (row['id'], row['id']))

            print """UPDATE main_crawlagregates
                set spam_projects =
                    ( select count(*) from hits_mv where crawl_id = %s and is_spam = true )
                where crawl_id = %s"""

            logging.info("update agregates for %s" % row['id'])

            if i % commit_threshold == 0:
                logging.info('commited after %s crawls' % i)
                execute_sql('commit;')

        except:
            error_info = grab_error(sys.exc_info())
            logging.error('an error occured at crawl_id: %s, %s %s' % (row['id'], error_info['type'], error_info['value']))
            execute_sql('rollback;')

    # delete dummy data
    execute_sql("DELETE FROM main_crawlagregates WHERE projects < 200;")
    execute_sql("COMMIT;")

