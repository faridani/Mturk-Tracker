from fabric.api import sudo, settings
from fabric.colors import yellow
from modules.utils import (PROPER_SUDO_PREFIX as SUDO_PREFIX, show)


def provision():
    """Add nxginx repository to known repositories and installs it."""
    show(yellow("Installing nginx."))
    with settings(sudo_prefix=SUDO_PREFIX):
        sudo("nginx=stable")
        sudo("add-apt-repository ppa:nginx/$nginx")
        sudo("apt-get update")
        sudo("apt-get install nginx")
