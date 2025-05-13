import typer

from sli.utils.ansible import run_ansible
from sli.utils.auxiliary import get_current_branch_name
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
    result = run_ansible(
        playbook_suffix="cluster/sync_project.yml",
        extravars={"branch": branch},
    )
    if result.rc == 0:
        logger.info(f"The AWX project and branch '{branch}' are now successfully synchronized.")
    else:
        logger.error(f"The synchronization of the AWX project with branch '{branch}' failed.")
