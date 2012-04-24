from os.path import join as pjoin
from fabric.api import env, run, prefix, settings
from fabric.colors import yellow, red
from utils import (cget, local_files_dir, show, upload_template_with_perms,
    cset, create_target_directories)


def configure_supervisor():
    """Upload supervisor configuration files."""
    user = cget('user')
    # settings directories
    sdir = cset('supervisor_dir', pjoin(cget('project_dir'), 'supervisor'))
    slogdir = cset('supervisor_log_dir', pjoin(cget('log_dir'), 'supervisor'))
    cset("supervisor_process_base", cget('project_name').replace('-', '_'))
    cset("supervisor_process_id",
        '%s%s' % (cget('supervisor_process_base'), '_supervisor'))
    # create all dirs and log dirs
    dirs = ['', 'config']
    dirs = [pjoin(sdir, l) for l in dirs]
    log_dirs = ['', cget('project_name'), 'child_auto']
    log_dirs = [pjoin(slogdir, l) for l in log_dirs]
    create_target_directories(dirs + log_dirs, "700", user)

    context = dict(env["ctx"])
    local_dir = local_files_dir("supervisor")
    dest_dir = pjoin(sdir, 'config')

    confs = cget("supervisor_files")
    show(yellow("Uploading service configuration files: %s." % confs))
    for name in confs:
        source = pjoin(local_dir, name)
        destination = pjoin(dest_dir, name)
        upload_template_with_perms(source, destination, context, mode="644")


def run_supevisordctl(command):
    """Start supervisor process."""
    conf = pjoin(cget('project_dir'), 'supervisor', 'config',
        'supervisord.conf')
    show(yellow("Running supervisorctrl: %s." % command))
    return run('supervisorctl --configuration="%s" %s' % (conf, command))


def start_supervisor():
    """Start supervisor process."""
    conf = pjoin(cget('project_dir'), 'supervisor', 'config',
        'supervisord.conf')
    pname = cget('supervisor_process_name')
    show(yellow("Starting supervisor with process name: %s." % pname))
    return run('supervisord --configuration="%s"' % conf)


def reload_supervisor():
    """Start supervisor process."""
    ve_dir = cget("virtualenv_dir")
    activate = pjoin(ve_dir, "bin", "activate")
    show(yellow("Reloading supervisor."))
    with prefix("source %s" % activate):
        with settings(warn_only=True):
            res = run_supevisordctl('reload')
            if res.return_code == 2:
                show(yellow("Supervisor unavailable, starting new process."))
                res = start_supervisor()
                if res.return_code != 0:
                    show(red("Error starting supervisor!."))
