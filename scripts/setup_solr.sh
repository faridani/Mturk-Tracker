#!/bin/sh

MTURK_HOME="/var/www/mturk"
SOLR_VERSION="1.4.1"

wget "ftp://mirror.nyi.net/apache/lucene/solr/1.4.1/apache-solr-$SOLR_VERSION.tgz" -O "/tmp/solr.tgz"
tar -C "/tmp" --overwrite -xvzf "/tmp/solr.tgz"
cp -rf "/tmp/apache-solr-$SOLR_VERSION/example/lib" "$MTURK_HOME/solr"
cp "/tmp/apache-solr-$SOLR_VERSION/example/start.jar" "$MTURK_HOME/solr"
cp -rf "/tmp/apache-solr-$SOLR_VERSION/example/webapps" "$MTURK_HOME/solr"