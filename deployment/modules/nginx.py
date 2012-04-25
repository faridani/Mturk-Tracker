from fabric.api import sudo, settings
from fabric.colors import yellow
from modules.utils import (PROPER_SUDO_PREFIX as SUDO_PREFIX, show,
    install_without_prompt)


def provision():
    """Add nxginx repository to known repositories and installs it."""
    show(yellow("Installing nginx."))
    with settings(sudo_prefix=SUDO_PREFIX):
        sudo("nginx=stable && add-apt-repository -y ppa:nginx/$nginx")
        sudo("apt-get update")
    install_without_prompt('nginx', 'nginx')
