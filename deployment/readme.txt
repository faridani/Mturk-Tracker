Deployment module directory structure
=====================================

TODO: update


on clean environment use:
fab deploy:conf_file="target_defs/testing.json",setup_environment=True -H 192.168.56.103 -u mturk

deploying without setup:
fab deploy:conf_file="target_defs/testing.json",requirements=False -H 192.168.56.103 -u mturk
