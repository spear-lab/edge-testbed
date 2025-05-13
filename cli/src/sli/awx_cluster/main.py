import ansible_runner
import sli.awx_cluster.configuration
import typer
from sli.utils.styling import create_spinner_context_manager
import sli.awx_cluster.projects
import sli.awx_cluster.configuration
from sli.utils.auxiliary import find_repo_root
from sli.utils.logging import logger
from sli.utils.typer_augmentations import AliasGroup

app = typer.Typer(cls=AliasGroup)

app.add_typer(
    typer_instance=sli.awx_cluster.projects.app,
    name="projects, p",
    help="Manage Projects",
)

app.add_typer(
    typer_instance=sli.awx_cluster.configuration.app,
    name="configuration, c",
    help="Configure the AWX cluster",
)


@app.command("url", help="Prints the url to the AWX cluster")
def show_url() -> None:
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
        logger.error("The ansible playbook failed - Ensure that you are connected to the VPN.")

@app.command("admin-pwd", help="Prints the admin pwd to log into the AWX cluster")
def show_admin_pwd() -> None:
    repo_root_path = find_repo_root()
    playbook_path = repo_root_path / "playbooks" / "awx" / "get_admin_pwd.yml"
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
        pwd = facts.get("awx_admin_pwd")
        logger.info("The AWX Cluster Admin PWD (VPN Tunneled): \n" + pwd)
        logger.info("The username is 'admin'")
    else:
        logger.error("The ansible playbook failed - Ensure that you are connected to the VPN.")
