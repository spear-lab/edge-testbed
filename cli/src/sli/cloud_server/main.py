import ansible_runner
import typer

from sli.utils.auxiliary import find_repo_root, get_playbook_path
from sli.utils.logging import logger
from sli.utils.styling import create_spinner_context_manager
from sli.utils.typer_augmentations import AliasGroup

app = typer.Typer(cls=AliasGroup)


@app.command("url", help="Prints the url to the AWX cluster")
def show_url() -> None:
    spinner_context = create_spinner_context_manager(
        message="Fetching port information from AWX cluster"
    )
    with spinner_context:
        result = ansible_runner.run(
            playbook=str(get_playbook_path("awx/get_url.yml")),
            private_data_dir=str(find_repo_root()),
            quiet=True,
        )
    if result.rc == 0:
        target_host = [k for k in result.stats.get("ok") if k != "localhost"][0]
        facts = result.get_fact_cache(target_host)
        url = facts.get("awx_cluster_vpn_url")
        logger.info("The AWX Cluster URL (VPN Tunneled): \n" + url)
    else:
        logger.error("The ansible playbook failed - Ensure that you are connected to the VPN.")


@app.command("admin-pwd", help="Prints the admin pwd to log into the AWX cluster")
def show_admin_pwd() -> None:
    spinner_context = create_spinner_context_manager(
        message="Fetching port information from AWX cluster"
    )
    with spinner_context:
        result = ansible_runner.run(
            playbook=str(get_playbook_path("awx/get_admin_pwd.yml")),
            private_data_dir=str(find_repo_root()),
            quiet=True,
        )
    if result.rc == 0:
        target_host = [k for k in result.stats.get("ok") if k != "localhost"][0]
        facts = result.get_fact_cache(target_host)
        pwd = facts.get("awx_admin_pwd")
        logger.info("The AWX Cluster Admin PWD (VPN Tunneled): \n" + pwd)
        logger.info("The username is 'admin'")
    else:
        logger.error("The ansible playbook failed - Ensure that you are connected to the VPN.")
