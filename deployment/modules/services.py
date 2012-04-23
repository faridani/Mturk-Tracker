from os.path import join as pjoin
from fabric.api import env, sudo, settings
from fabric.colors import yellow

from utils import cget, local_files_dir, show, upload_template_with_perms


def configure_nginx():
    instance = cget("instance")
    context = dict(env["ctx"])
    source = pjoin(local_files_dir("nginx"), "site")
    destination = pjoin("/etc/nginx/sites-enabled", cget("project_name"))

    show(yellow("Installing Nginx site configuration, instance: %s."),
        instance)
    upload_template_with_perms(source, destination, context, mode="644")


def reload_nginx():
    show(yellow("Reloading Nginx"))
    sudo("service nginx reload")
