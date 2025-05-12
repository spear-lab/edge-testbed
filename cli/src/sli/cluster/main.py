import ansible_runner
import typer
from sli.utils.styling import create_spinner_context_manager
import sli.cluster.projects
from sli.configuration.security.main import get_vault_pwd_file_path
from sli.utils.auxiliary import find_repo_root, get_current_branch_name
from sli.utils.logging import logger
from sli.utils.typer_augmentations import AliasGroup
from icecream import ic
import json
from sli.utils.consts import ANSIBLE_FACT_CACHE_PATH

app = typer.Typer(cls=AliasGroup)

app.add_typer(
    typer_instance=sli.cluster.projects.app,
    name="projects, p",
    help="Manage Projects",
)


@app.command("show-link, l", help="Prints the link to the AWX cluster")
def show_link() -> None:
    repo_root_path = find_repo_root()
    playbook_path = repo_root_path / "playbooks" / "awx" / "get_url.yml"
    spinner_context = create_spinner_context_manager(message="Fetching port information from AWX cluster")
    with spinner_context:
        result = ansible_runner.run(
            playbook=str(playbook_path),
            private_data_dir=str(repo_root_path),
            quiet=True,
        )
    if result.rc == 0:
        target_host = [k for k in result.stats.get('ok') if k != 'localhost'][0]

        facts = result.get_fact_cache(target_host)
        url = facts.get("awx_cluster_vpn_url")
        logger.info("The AWX Cluster URL (VPN Tunneled): \n" + url)
    else:
        logger.error(result.stderr)

@app.command("apply-configuration, ac", help="Run the cluster configuration playbook")
def apply_configuration(
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
            f"Are you sure that you want to apply the configuration from the '{branch}' to the AWX instance?"
        ):
            raise typer.Abort()

    logger.info(
        f"The branch '{branch}' will be used when applying the configuration to the AWX instance."
    )

    it_management_root_path = find_repo_root()
    playbook_path = it_management_root_path / "playbooks" / "cluster" / "configure_cluster.yml"
    result = ansible_runner.run(
        playbook=str(playbook_path),
        extravars={
            "branch": branch,
            "only_update_playbook_related": only_update_playbook_related,
        },
        private_data_dir=str(it_management_root_path),
        verbosity=1,
        cmdline=f"--vault-password-file {get_vault_pwd_file_path()}",
    )
    if result.rc == 0:
        logger.info(f"The AWX instance was successfully configured using the '{branch}' branch.")
    else:
        logger.error(f"The AWX instance configuration failed using the '{branch}' branch.")


@app.command(
    "reset-configuration",
    help="Resets the cluster to its default settings without any custom SPEAR changes",
)
def reset_configuration(
    skip_confirmation: bool = typer.Option(False, "-y", help="Skip confirmation prompt"),
) -> None:
    if not skip_confirmation:
        if not typer.confirm(
            "Are you certain that you want to RESET the configuration of the cluster?"
        ):
            raise typer.Abort()

    it_management_root_path = find_repo_root()
    playbook_path = it_management_root_path / "playbooks" / "cluster" / "configure_cluster.yml"
    result = ansible_runner.run(
        playbook=str(playbook_path),
        extravars={"branch": "master", "reset_configuration": True},
        private_data_dir=str(it_management_root_path),
        verbosity=1,
        cmdline=f"--vault-password-file {get_vault_pwd_file_path()}",
    )
    if result.rc == 0:
        logger.info("The AWX cluster configuration was successfully reset")
    else:
        logger.error("Resetting the AWX cluster configuration failed")


@app.command(
    "backup-users",
    help="Exports AWX cluster users as a JSON file (overwrite) in the configure cluster role",
)
def backup_configuration() -> None:
    it_management_root_path = find_repo_root()
    playbook_path = it_management_root_path / "playbooks" / "cluster" / "backup_users.yml"
    result = ansible_runner.run(
        playbook=str(playbook_path),
        extravars={"branch": "master"},
        private_data_dir=str(it_management_root_path),
        verbosity=0,
        cmdline=f"--vault-password-file {get_vault_pwd_file_path()}",
    )
    if result.rc == 0:
        logger.info("The AWX cluster assets were successfully exported")
    else:
        logger.error("Exporting the AWX cluster assets failed")
