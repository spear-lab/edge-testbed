import ansible_runner
import typer

from itm_cli.cluster.common import Cluster
from itm_cli.configuration.security.main import get_vault_pwd_file_path
from itm_cli.utils.auxiliary import find_it_management_root, get_current_branch_name
from itm_cli.utils.logging import logger
from itm_cli.utils.typer_augmentations import AliasGroup

app = typer.Typer(cls=AliasGroup)


@app.command(
    "sync, s",
    help="Synchronize the AWX instance's project based on the latest it-management branch state",
)
def synchronize_project(
    cluster: Cluster,
    branch: str = typer.Option("", help="The name of the branch that should be synchronized with"),
) -> None:
    if not branch:
        branch = get_current_branch_name()
    logger.info(f"Start synchronizing '{cluster}' AWX project with branch '{branch}'")
    it_management_root_path = find_it_management_root()
    playbook_path = it_management_root_path / "playbooks" / "cluster" / "sync_project.yml"
    result = ansible_runner.run(
        playbook=str(playbook_path),
        extravars={"cluster_name": str(cluster), "branch": branch},
        private_data_dir=str(it_management_root_path),
        verbosity=1,
        cmdline=f"--vault-password-file {get_vault_pwd_file_path()}",
    )
    if result.rc == 0:
        logger.info(
            f"The '{cluster}' AWX project and branch '{branch}' are now successfully synchronized."
        )
    else:
        logger.error(
            f"The synchronization of the '{cluster}' AWX project with branch '{branch}' failed."
        )
