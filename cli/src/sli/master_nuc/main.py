import typer

from sli.utils.ansible import run_ansible
from sli.utils.logging import logger
from sli.utils.typer_augmentations import AliasGroup

app = typer.Typer(cls=AliasGroup)


@app.command(
    "get-vpn-credentials",
    help="Ensures the master NUC has VPN credentials and retrieves them",
)
def get_vpn_credentials(verbose: bool = False) -> None:
    res = run_ansible(
        playbook_suffix="local/cloud-server/vpn/add-master-nuc.yml",
        extravars={
            "copy_over_credentials_to_localhost": True,
        },
        spinner_message="" if verbose else "Retrieving VPN credentials from the VPN server.",
    )
    if res.rc == 0:
        logger.info("The certificates can be found at '/tmp/vpn-client-credentials/master_nuc'")


@app.command(
    "initial-setup", help="Installs fundamental dependencies, such as apt packages, docker, etc."
)
def initial_setup() -> None:
    run_ansible(
        playbook_suffix="local/cloud-server/initial-setup.yml",
    )
