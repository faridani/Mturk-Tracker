from os.path import join as pjoin
from fabric.api import env, sudo, settings
from fabric.colors import yellow

from utils import cget, files_dir, show, upload_template_with_perms


def configure_gunicorn():
    project_dir = cget("project_dir")
    user = cget("user")
    context = dict(env["ctx"])
    runner = pjoin(files_dir("gunicorn"), "runner_script.sh")
    init_script = pjoin(files_dir("gunicorn"), "init_script.sh")

    show(yellow("Uploading Gunicorn configuration."))
    # Runner script.
    runner_dest = pjoin(project_dir, "scripts", "run_gunicorn.sh")
    upload_template_with_perms(runner, runner_dest, context, mode="755",
        user=user, group=user)
    # Init script.
    context["runner"] = runner_dest
    init_dest = pjoin("/etc/init.d", "%s_gunicorn" % cget("project_name"))
    upload_template_with_perms(init_script, init_dest, context, mode="755")


def configure_celeryd():
    context = dict(env["ctx"])
    source = pjoin(files_dir("celery"), "init_script.sh")
    destination = pjoin("/etc/init.d", "%s_celeryd" % cget("project_name"))

    show(yellow("Uploading Celery daemon configuration."))
    upload_template_with_perms(source, destination, context, mode="755")


def configure_celerybeat():
    context = dict(env["ctx"])
    source = pjoin(files_dir("celery"), "init_celerybeat.sh")
    destination = pjoin("/etc/init.d", "%s_celerybeat" % cget("project_name"))

    show(yellow("Uploading CeleryBeat task Scheduler configuration."))
    upload_template_with_perms(source, destination, context, mode="755")


def configure_async_server():
    project_dir = cget("project_dir")
    user = cget("user")
    context = dict(env["ctx"])
    runner = pjoin(files_dir("async"), "runner_script.sh")
    init_script = pjoin(files_dir("async"), "init_script.sh")

    show(yellow("Uploading Async server configuration."))
    # Runner script.
    runner_dest = pjoin(project_dir, "scripts", "run_async.sh")
    upload_template_with_perms(runner, runner_dest, context, mode="755",
        user=user, group=user)
    # Init script.
    context["runner"] = runner_dest
    init_dest = pjoin("/etc/init.d", "%s_async" % cget("project_name"))
    upload_template_with_perms(init_script, init_dest, context, mode="755")


def configure_nginx():
    instance = cget("instance")
    context = dict(env["ctx"])
    source = pjoin(files_dir("nginx"), "site")
    destination = pjoin("/etc/nginx/sites-enabled", cget("project_name"))

    show(yellow("Installing Nginx site configuration, instance: %s."),
        instance)
    upload_template_with_perms(source, destination, context, mode="644")


def configure_logrotate():
    user = cget("user")
    context = dict(env["ctx"])
    source = pjoin(files_dir("logrotate"), "logs-conf")
    destination = pjoin("/etc/logrotate.d/", cget("project_name"))

    show(yellow("Uploading Logrotate daemon configuration."))
    upload_template_with_perms(source, destination, context, mode="644",
        user=user, group=user)


def configure_monit():
    confs = ["async.conf", "celeryd.conf", "gunicorn.conf"]
    monit = files_dir("monit")
    context = dict(env["ctx"])
    dest_dir = "/etc/monit/conf.d"

    show(yellow("Uploading service monitoring configuration."))
    for name in confs:
        source = pjoin(monit, name)
        destination = pjoin(dest_dir, "%s_%s" % (cget("project_name"), name))
        upload_template_with_perms(source, destination, context, mode="644")


def reload_nginx():
    show(yellow("Reloading Nginx"))
    sudo("service nginx reload")


def restart_gunicorn():
    with settings(warn_only=True):
        show(yellow("Restarting Gunicorn"))
        sudo("service %s_gunicorn restart" % cget("project_name"))


def restart_celeryd():
    with settings(warn_only=True):
        show(yellow("Restarting Celery daemon"))
        sudo("service %s_celeryd restart" % cget("project_name"))


def restart_celerybeat():
    with settings(warn_only=True):
        show(yellow("Restarting Celery Task Scheduler"))
        sudo("service %s_celerybeat restart" % cget("project_name"))


def restart_async():
    with settings(warn_only=True):
        show(yellow("Restarting Async server"))
        sudo("service %s_async restart" % cget("project_name"))


def stop_services_for_reload():
    show(yellow("Stopping ALL %s services for reload"), cget("project_name"))
    with settings(warn_only=True):
        sudo("service %s_gunicorn stop" % cget("project_name"))
        sudo("service %s_celeryd stop" % cget("project_name"))
        sudo("service %s_celerybeat stop" % cget("project_name"))
        sudo("service %s_async stop" % cget("project_name"))
