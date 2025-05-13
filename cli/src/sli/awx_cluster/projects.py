import ansible_runner
import typer

from sli.configuration.security.main import get_vault_pwd_file_path
from sli.utils.auxiliary import find_repo_root, get_current_branch_name, get_playbook_path
from sli.utils.logging import logger
from sli.utils.typer_augmentations import AliasGroup

app = typer.Typer(cls=AliasGroup)


@app.command(
    "sync, s",
    help="Synchronize the AWX instance's project based on the latest it-management branch state",
)
def synchronize_project(
    branch: str = typer.Option("", help="The name of the branch that should be synchronized with"),
) -> None:
    if not branch:
        branch = get_current_branch_name()
    logger.info(f"Start synchronizing AWX project with branch '{branch}'")
    result = ansible_runner.run(
        playbook=str(get_playbook_path("cluster/sync_project.yml")),
        extravars={"branch": branch},
        private_data_dir=str(find_repo_root()),
        verbosity=1,
        cmdline=f"--vault-password-file {get_vault_pwd_file_path()}",
    )
    if result.rc == 0:
        logger.info(f"The AWX project and branch '{branch}' are now successfully synchronized.")
    else:
        logger.error(f"The synchronization of the AWX project with branch '{branch}' failed.")
