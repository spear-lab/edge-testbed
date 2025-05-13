import typer
from sli.utils.typer_augmentations import AliasGroup
from sli.utils.ansible import run_ansible

import sli.cloud_server.vpn.main

app = typer.Typer(cls=AliasGroup)

app.add_typer(
    typer_instance=sli.cloud_server.vpn.main.app,
    name="vpn",
    help="Commands to manage and configure the VPN",
)


@app.command(
    "initial-setup", help="Installs fundamental dependencies, such as apt packages, docker, etc."
)
def initial_setup() -> None:
    run_ansible(
        playbook_suffix="local/cloud-server/initial-setup.yml",
        become_target_host="cloud-server",
    )
