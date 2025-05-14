import typer
from icecream import ic

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
        playbook_suffix="local/cloud-server/vpn/add-user.yml",
        extravars={
            "client_name": client_common_name,
            "copy_over_credentials_to_localhost": get_client_credentials,
        },
        spinner_message="" if verbose else f"Adding new client '{client_common_name}' to the VPN",
    )
    if res.rc == 0:
        logger.info(f"The new client '{client_common_name}' was successfully added.")
        if get_client_credentials:
            logger.info(
                f"The certificates can be found at '/tmp/vpn-client-credentials/{client_common_name}'"
            )


@app.command(
    "get-client-credentials",
    help="Copies the requested client credentials over into /tmp/vpn-client-credentials/<client-name>",
)
def get_client_credentials(client_common_name: str, verbose: bool = False) -> None:
    res = run_ansible(
        playbook_suffix="local/cloud-server/vpn/get-client-credentials.yml",
        extravars={
            "client_name": client_common_name,
            "copy_over_credentials_to_localhost": True,
        },
        spinner_message="" if verbose else "Fetching client certificates from the VPN Server",
    )
    if res.rc == 0:
        logger.info(
            f"The certificates can be found at '/tmp/vpn-client-credentials/{client_common_name}'"
        )


@app.command(
    "list-clients",
    help="List all VPN clients",
)
def list_client(verbose: bool = False) -> None:
    res = run_ansible(
        playbook_suffix="local/cloud-server/vpn/list-clients.yml",
        spinner_message="" if verbose else "Inspecting all clients from the VPN Server",
    )
    if res.rc == 0:
        target_host = [k for k in res.stats.get("ok") if k != "localhost"][0]
        facts = res.get_fact_cache(target_host)
        clients = facts.get("vpn_client_list")
        ic.configureOutput(prefix="")
        ic(clients)
