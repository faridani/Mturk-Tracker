Deployment module directory structure:

deployment
    - modules
        python modules used by fabfile
    - files
        - ssh
            ssh_key1.ssh
            ssh_key2.ssh
        - supervisor
        #TODO: add all
    - requirements
        requirements_file1.txt
        requirements_file2.txt
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
    - logs/old
    - misc
    - virtualenv
    - media
    - static
    - scripts
        run_service1.sh
        run_service2.sh
