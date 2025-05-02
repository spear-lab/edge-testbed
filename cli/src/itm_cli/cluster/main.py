import ansible_runner
import typer

import itm_cli.cluster.projects
from itm_cli.cluster.common import Cluster
from itm_cli.configuration.security.main import get_vault_pwd_file_path
from itm_cli.utils.auxiliary import find_it_management_root, get_current_branch_name
from itm_cli.utils.logging import logger
from itm_cli.utils.typer_augmentations import AliasGroup

app = typer.Typer(cls=AliasGroup)

app.add_typer(
    typer_instance=itm_cli.cluster.projects.app,
    name="projects, p",
    help="Manage Projects",
)


@app.command("show-link, l", help="Prints the link to the AWX cluster")
def show_link(cluster: Cluster) -> None:
    match cluster:
        case Cluster.PRODUCTION:
            url = "https://infrastructure.cartken.com/"
        case Cluster.STAGING:
            url = "https://staging-infrastructure.cartken.com/"

    logger.info(url)


@app.command("apply-configuration, ac", help="Run the cluster configuration playbook")
def apply_configuration(
    cluster: Cluster,
    skip_confirmation: bool = typer.Option(False, "-y", help="Skip confirmation prompt"),
    branch: str = typer.Option("", help="The name of the branch that should be synchronized with"),
    only_update_playbook_related: bool = typer.Option(
        False,
        "--only-playbook-related",
        help="Only configure templates, and roles",
    ),
) -> None:
    if not branch:
        branch = get_current_branch_name()

    if not skip_confirmation:
        if not typer.confirm(
            f"Are you sure that you want to apply the configuration from the '{branch}' to the '{cluster}' AWX instance?"
        ):
            raise typer.Abort()

    logger.info(
        f"The branch '{branch}' will be used when applying the configuration to the '{cluster}' AWX instance."
    )

    it_management_root_path = find_it_management_root()
    playbook_path = it_management_root_path / "playbooks" / "cluster" / "configure_cluster.yml"
    result = ansible_runner.run(
        playbook=str(playbook_path),
        extravars={
            "cluster_name": str(cluster),
            "branch": branch,
            "only_update_playbook_related": only_update_playbook_related,
        },
        private_data_dir=str(it_management_root_path),
        verbosity=1,
        cmdline=f"--vault-password-file {get_vault_pwd_file_path()}",
    )
    if result.rc == 0:
        logger.info(
            f"The '{cluster}' AWX instance was successfully configured using the '{branch}' branch."
        )
    else:
        logger.error(
            f"The '{cluster}' AWX instance configuration failed using the '{branch}' branch."
        )


@app.command(
    "reset-configuration",
    help="Resets the cluster to its default settings without any Cartken changes",
)
def reset_configuration(
    cluster: Cluster,
    skip_confirmation: bool = typer.Option(False, "-y", help="Skip confirmation prompt"),
) -> None:
    if not skip_confirmation:
        if not typer.confirm(
            f"Are you certain that you want to RESET the configuration of the '{cluster}' cluster?"
        ):
            raise typer.Abort()

    it_management_root_path = find_it_management_root()
    playbook_path = it_management_root_path / "playbooks" / "cluster" / "configure_cluster.yml"
    result = ansible_runner.run(
        playbook=str(playbook_path),
        extravars={"cluster_name": str(cluster), "branch": "master", "reset_configuration": True},
        private_data_dir=str(it_management_root_path),
        verbosity=1,
        cmdline=f"--vault-password-file {get_vault_pwd_file_path()}",
    )
    if result.rc == 0:
        logger.info(f"The '{cluster}' AWX cluster configuration was successfully reset")
    else:
        logger.error(f"Resetting the '{cluster}' AWX cluster configuration failed")


@app.command(
    "backup-users",
    help="Exports AWX cluster users as a JSON file (overwrite) in the configure cluster role",
)
def backup_configuration(
    cluster: Cluster,
) -> None:
    it_management_root_path = find_it_management_root()
    playbook_path = it_management_root_path / "playbooks" / "cluster" / "backup_users.yml"
    result = ansible_runner.run(
        playbook=str(playbook_path),
        extravars={"cluster_name": str(cluster), "branch": "master"},
        private_data_dir=str(it_management_root_path),
        verbosity=0,
        cmdline=f"--vault-password-file {get_vault_pwd_file_path()}",
    )
    if result.rc == 0:
        logger.info(f"The '{cluster}' AWX cluster assets were successfully exported")
    else:
        logger.error(f"Exporting the '{cluster}' AWX cluster assets failed")
