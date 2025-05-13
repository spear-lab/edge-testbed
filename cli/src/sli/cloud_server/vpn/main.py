import typer

from sli.utils.ansible import run_ansible
from sli.utils.logging import logger
from sli.utils.typer_augmentations import AliasGroup

app = typer.Typer(cls=AliasGroup)


@app.command("setup", help="Sets up the VPN Server, PKI, and cloud server VPN client.")
def vpn_setup() -> None:
    run_ansible(
        playbook_suffix="local/cloud-server/vpn/setup.yml",
    )


@app.command(
    "add-client",
    help="Adds a new client to the VPN (PKI)",
)
def add_vpn_client(
    client_common_name: str, get_client_credentials: bool = True, verbose: bool = False
) -> None:
    res = run_ansible(
        playbook_suffix="local/cloud-server/vpn/add-clients.yml",
        extravars={
            "client_names": [client_common_name],
            "copy_over_credentials_to_localhost": get_client_credentials,
        },
        spinner_message=f"Adding new client '{client_common_name}' to the VPN" if verbose else "",
    )
    if res.rc == 0:
        logger.info(f"The new client '{client_common_name}' was successfully added.")
        if get_client_credentials:
            logger.info(
                f"\nThe certificates can be found at '/tmp/vpn-client-credentials/{client_common_name}'"
            )


@app.command(
    "get-client-credentials",
    help="Copies the requested client credentials over into /tmp/vpn-client-credentials/<client-name>",
)
def get_client_credentials(client_common_name: str) -> None:
    res = run_ansible(
        playbook_suffix="local/cloud-server/vpn/get-client-credentials.yml",
        extravars={
            "client_name": client_common_name,
            "copy_over_credentials_to_localhost": True,
        },
        spinner_message="Fetching client certificates from the VPN Server",
    )
    if res.rc == 0:
        logger.info(
            f"\nThe certificates can be found at '/tmp/vpn-client-credentials/{client_common_name}'"
        )
