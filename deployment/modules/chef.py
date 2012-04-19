from fabric import colors
from fabric.api import sudo, task, settings, hide, run, cd
from fabric.contrib.project import rsync_project
from utils import show


def install_chef():
    "Installs Chef packages on a server"
    show(colors.blue("Installing Chef"))
    sudo("apt-get update")
    sudo("apt-get install -y rubygems ruby ruby-dev")
    sudo("gem install --no-rdoc --no-ri chef")


def sync_chef():
    show(colors.blue("Syncing Chef cookbooks and config"))
    rsync_project(local_dir="chef/", remote_dir="/tmp/chef")


@task
def provision_chef():
    "Prepares server with Chef cookbooks"
    show(colors.blue("Updating system configuration with Chef"))
    sync_chef()
    # Find Chef binary
    with settings(hide("warnings"), warn_only=True):
        chef_solo = run("which chef_solo")
        if not chef_solo:
            if not run("ls /var/lib/gems/1.8/bin/chef-solo").failed:
                chef_solo = "/var/lib/gems/1.8/bin/chef-solo"
            elif not run("ls /usr/local/bin/chef-solo").failed:
                chef_solo = "/usr/local/bin/chef-solo"

    # Start provisioning
    with cd("/tmp/chef"):
        sudo("%s -j config/node.json -c config/solo.rb" % chef_solo)


@task
def bootstrap():
    "Bootstraps empty server with Chef and its recipes"
    install_chef()
    provision_chef()
