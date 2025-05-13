import typer

import sli.awx_cluster.configuration
import sli.awx_cluster.projects
from sli.utils.ansible import run_ansible
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
def show_url(verbose: bool = False) -> None:
    result = run_ansible(
        playbook_suffix="awx/get_url.yml",
        spinner_message="" if verbose else "Fetching port information from AWX cluster",
    )
    if result.rc == 0:
        target_host = [k for k in result.stats.get("ok") if k != "localhost"][0]
        facts = result.get_fact_cache(target_host)
        url = facts.get("awx_cluster_vpn_url")
        logger.info("The AWX Cluster URL (VPN Tunneled): \n" + url)
    else:
        logger.error("The ansible playbook failed - Ensure that you are connected to the VPN.")


@app.command("admin-pwd", help="Prints the admin pwd to log into the AWX cluster")
def show_admin_pwd(verbose: bool = False) -> None:
    result = run_ansible(
        playbook_suffix="awx/get_admin_pwd.yml",
        spinner_message="" if verbose else "Fetching admin pwd from AWX cluster",
    )
    if result.rc == 0:
        target_host = [k for k in result.stats.get("ok") if k != "localhost"][0]
        facts = result.get_fact_cache(target_host)
        pwd = facts.get("awx_admin_pwd")
        logger.info("The AWX Cluster Admin PWD (VPN Tunneled): \n" + pwd)
        logger.info("The username is 'admin'")
    else:
        logger.error("The ansible playbook failed - Ensure that you are connected to the VPN.")
