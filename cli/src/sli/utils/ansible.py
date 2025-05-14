import pathlib
import sys
from contextlib import nullcontext

import ansible_runner

from sli.configuration.security.main import get_vault_pwd_file_path
from sli.utils.auxiliary import find_repo_root
from sli.utils.logging import logger
from sli.utils.styling import create_spinner_context_manager


def get_playbook_path(playbook_suffix: str) -> pathlib.Path:
    return find_repo_root() / "playbooks" / playbook_suffix


def run_ansible(
    playbook_suffix: str,
    extravars: dict = {},
    verbosity: int = 1,
    spinner_message: str = "",
) -> ansible_runner.runner.Runner:
    def event_handler(event) -> True:
        if event.get("event") == "runner_on_failed":
            logger.error("\n" + event.get("stdout"))
            sys.exit(1)
        # NOTE: Otherwise the internal event handling gets broken.
        return True

    cmdline = f"--vault-password-file {get_vault_pwd_file_path()}"
    if spinner_message:
        spinner_context = create_spinner_context_manager(message=spinner_message)
    with spinner_context if spinner_message else nullcontext():
        return ansible_runner.run(
            playbook=str(get_playbook_path(playbook_suffix)),
            private_data_dir=str(find_repo_root()),
            cmdline=cmdline,
            verbosity=verbosity,
            extravars=extravars,
            quiet=bool(spinner_message),
            event_handler=event_handler,
        )
