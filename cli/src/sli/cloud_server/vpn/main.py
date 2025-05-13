import typer

from sli.utils.ansible import run_ansible
from sli.utils.logging import logger
from sli.utils.styling import create_spinner_context_manager
from sli.utils.typer_augmentations import AliasGroup

app = typer.Typer(cls=AliasGroup)


@app.command("setup", help="Sets up the VPN Server, PKI, and cloud server VPN client.")
def vpn_setup() -> None:
    run_ansible(
        playbook_suffix="local/cloud-server/vpn/setup.yml",
    )


@app.command(
    "get-client-credentials",
    help="Copies the requested client credentials over into /tmp/vpn-client-credentials/<client-name>",
)
def get_client_credentials(client_common_name: str) -> None:
    spinner_context = create_spinner_context_manager(
        message="Fetching client certificates from the VPN Server"
    )
    with spinner_context:
        res = run_ansible(
            playbook_suffix="local/cloud-server/vpn/get-client-credentials.yml",
            extravars={
                "client_name": client_common_name,
                "copy_over_credentials_to_localhost": True,
            },
            quiet=True,
        )
        if res.rc == 0:
            logger.info(
                f"\nThe certificates can be found at '/tmp/vpn-client-credentials/{client_common_name}'"
            )
