Deployment module directory structure:

deployment
    - modules
        python modules used by fabfile
    - files
        - django
            - settings
                local.py
            settings_template.py  # imported settings module
        - ssh
            config
            ssh_key1.ssh
            ssh_key2.ssh
        - supervisor
            supervisord.conf  # supervisor and supervisorctl configuration
            service1.conf
            service2.conf
        - requirements
            requirements_file1.txt
            requirements_file2.txt
            system_requirements1.txt
            system_requirements2.txt
    - target_defs
        defaults.json (defaults for the project inherited by all other defs)
        target_def1.json
        target_def2.json
    fabfile.py
    readme.txt (this file)


Output directory structure on target machine:

project_dir/{default_prefix}-{instance}
    - code
    - logs
        - supervisor
            - service1
            - service2
            - child_auto  # for unconfigured loggers
            supervisor.log
    - misc
    - virtualenv
    - media
    - static  # output of collectstatic
    - scripts
        run_service1.sh
        run_service2.sh

on clean environment use:
fab deploy:conf_file="target_defs/testing.json",skip_global=False -H 192.168.56.103 -u mturk

deploying without setup:
fab deploy:conf_file="target_defs/testing.json",requirements=False -H 192.168.56.103 -u mturk
