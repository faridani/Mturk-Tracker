import os
from django.conf import settings
from south.db import db


def create_mviews():
    """Setups material views according to:
    http://tech.jonathangardner.net/wiki/PostgreSQL/Materialized_Views

    As a result the following functions are created:
        create_matview(name, name)
        drop_matview(name)
        refresh_matview(name)
        incremental_refresh_matview(name)
    and a table:
        matviews
    """
    mviews_sql = os.path.join(
        settings.ROOT_PATH, 'mturk/main/migration_extra/sql/mviews.sql')
    db.execute_many(open(mviews_sql).read())


def drop_mviews():
    """Drops objects created by create_mviews."""
    mviews_drop_sql = os.path.join(
        settings.ROOT_PATH, 'mturk/main/migration_extra/sql/mviews_drop.sql')
    db.execute_many(open(mviews_drop_sql).read())


def create_hits_views():
    """Creates hits view and related material view.
    First query creates basic hits_v, generating schema for hits_mv.
    Next, hits_V is altered to select only the objects that are not yet
    included in hits_mv.
    """
    CREATE_HITS_V = """
    CREATE OR REPLACE VIEW hits_v AS
    SELECT p.id AS status_id,
           q.id AS content_id,
           p.group_id,
           p.crawl_id,
           ( SELECT main_crawl.start_time FROM main_crawl
             WHERE main_crawl.id = p.crawl_id) AS start_time,
           q.requester_id,
           p.hits_available,
           p.page_number,
           p.inpage_position,
           p.hit_expiration_date,
           q.reward,
           q.time_alloted
    FROM main_hitgroupstatus p
    JOIN main_hitgroupcontent q ON q.group_id::text = p.group_id::text AND
                                   p.hit_group_content_id = q.id
    """
    db.execute(CREATE_HITS_V)
    db.execute("""SELECT create_matview('hits_mv', 'hits_v');""")
    db.execute("""drop view hits_v;""")
    CREATE_HITS_V = """
    CREATE OR REPLACE VIEW hits_v AS
    SELECT p.id AS status_id,
           q.id AS content_id,
           p.group_id,
           p.crawl_id,
           ( SELECT main_crawl.start_time FROM main_crawl
             WHERE main_crawl.id = p.crawl_id) AS start_time,
           q.requester_id,
           p.hits_available,
           p.page_number,
           p.inpage_position,
           p.hit_expiration_date,
           q.reward,
           q.time_alloted
    FROM main_hitgroupstatus p
    JOIN main_hitgroupcontent q ON q.group_id::text = p.group_id::text AND
                                   p.hit_group_content_id = q.id
        WHERE NOT (p.crawl_id IN (
            SELECT DISTINCT hits_mv.crawl_id FROM hits_mv
            ORDER BY hits_mv.crawl_id)
        );
    """
    db.execute(CREATE_HITS_V)


def drop_hits_views():
    """Drops objects created by create_hits_view."""
    db.execute("DROP TABLE hits_mv;")
    db.execute("DROP VIEW hits_v;")


def create_indexes():
    db.create_index('hits_mv', ['start_time'])
    db.create_index('hits_mv', ['crawl_id'])
    db.create_index('hits_mv', ['group_id'])
    db.create_index('main_hitgroupcontent', ['group_id'], unique=True)
    db.create_index('main_hitgroupcontent', ['requester_id'])
    db.execute("""
    CREATE INDEX hits_mv_start_time_group_id ON hits_mv
    USING btree (group_id, start_time);
    """)


def drop_indexes():
    db.drop_index('hits_mv', ['start_time'])
    db.drop_index('hits_mv', ['crawl_id'])
    db.drop_index('hits_mv', ['group_id'])
    db.drop_index('main_hitgroupcontent', ['group_id'])
    db.drop_index('main_hitgroupcontent', ['requester_id'])
    db.execute('''DROP INDEX hits_mv_start_time_group_id;''')
