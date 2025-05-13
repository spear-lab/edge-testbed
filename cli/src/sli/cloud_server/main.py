import ansible_runner
import typer
import getpass
from sli.utils.auxiliary import find_repo_root, get_playbook_path
from sli.utils.logging import logger
from sli.utils.styling import create_spinner_context_manager
from sli.utils.typer_augmentations import AliasGroup

from sli.configuration.security.main import get_vault_pwd_file_path

app = typer.Typer(cls=AliasGroup)


@app.command("initial-setup, is", help="Installs fundamental dependencies, such as apt packages, docker, etc.")
def initial_setup() -> None:
    become_password = getpass.getpass("[sudo] cloud-server password: ")
    ansible_runner.run(
        playbook=str(get_playbook_path("local/cloud-server/initial-setup.yml")),
        private_data_dir=str(find_repo_root()),
        cmdline=f"--vault-password-file {get_vault_pwd_file_path()} --ask-become-pass",
        verbosity=1,
        passwords={"^BECOME password.*:\\s*?$": become_password},
    )
