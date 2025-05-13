import pathlib

import ansible_runner

from sli.configuration.security.main import get_vault_pwd_file_path
from sli.utils.auxiliary import find_repo_root


def get_playbook_path(playbook_suffix: str) -> pathlib.Path:
    return find_repo_root() / "playbooks" / playbook_suffix


def run_ansible(
    playbook_suffix: str,
    extravars: dict = {},
    verbosity: int = 1,
    quiet: bool = False,
) -> ansible_runner.runner.Runner:
    cmdline = f"--vault-password-file {get_vault_pwd_file_path()}"
    return ansible_runner.run(
        playbook=str(get_playbook_path(playbook_suffix)),
        private_data_dir=str(find_repo_root()),
        cmdline=cmdline,
        verbosity=verbosity,
        extravars=extravars,
        quiet=quiet,
    )
