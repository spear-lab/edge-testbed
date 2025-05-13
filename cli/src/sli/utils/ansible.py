import pathlib

import ansible_runner

from sli.configuration.security.main import get_vault_pwd_file_path
from sli.utils.auxiliary import find_repo_root
from sli.utils.common import ask_for_target_host_become_pwd


def get_playbook_path(playbook_suffix: str) -> pathlib.Path:
    return find_repo_root() / "playbooks" / playbook_suffix


def run_ansible(
    playbook_suffix: str,
    become_target_host: str = "",
    extravars: dict = {},
    verbosity: int = 1,
    quiet: bool = False,
) -> ansible_runner.runner.Runner:
    """This is a custom wrapper for ansible_runner.run() \n
    Input parameters explained:
        ask_become_pwd: str
            - If set will ask the user to provide the sudo password for the target host.
            - This parameter takes a "descriptive" name of the target host to help queried users to type the correct pwd.
    """

    cmdline = f"--vault-password-file {get_vault_pwd_file_path()}"
    passwords = {}

    if become_target_host:
        cmdline += " --ask-become-pass"
        passwords = {"^BECOME password.*:\\s*?$": ask_for_target_host_become_pwd(become_target_host)}
        
    return ansible_runner.run(
        playbook=str(get_playbook_path(playbook_suffix)),
        private_data_dir=str(find_repo_root()),
        cmdline=cmdline,
        verbosity=verbosity,
        passwords=passwords,
        extravars=extravars,
        quiet=quiet,
    )
