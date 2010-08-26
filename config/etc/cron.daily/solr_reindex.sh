#!/bin/sh

LOG_FILE="/var/log/mturk/cron.log"

echo "["`date`"] daily-mturk_0_solrimport: Reindexing main" >> $LOG_FILE
curl "http://localhost:8983/solr/en/import_db_hits/?command=full-import"
