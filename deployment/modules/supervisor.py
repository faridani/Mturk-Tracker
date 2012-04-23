from os.path import join as pjoin
from fabric.api import env, sudo, settings
from fabric.colors import yellow
from utils import cget, local_files_dir, show, upload_template_with_perms


def configure_supervisor():
    """Supervisor should be installed from requirements."""
    confs = ["async.conf", "celeryd.conf", "gunicorn.conf"]
    monit = local_files_dir("configuration")
    context = dict(env["ctx"])
    dest_dir = "/etc/monit/conf.d"

    show(yellow("Uploading service monitoring configuration."))
    for name in confs:
        source = pjoin(monit, name)
        destination = pjoin(dest_dir, "%s_%s" % (cget("project_name"), name))
        upload_template_with_perms(source, destination, context, mode="644")
