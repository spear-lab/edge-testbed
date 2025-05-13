import typer
from sli.utils.typer_augmentations import AliasGroup

from sli.utils.ansible import run_ansible

app = typer.Typer(cls=AliasGroup)


@app.command("setup", help="Installs fundamental dependencies, such as apt packages, docker, etc.")
def vpn_setup() -> None:
    run_ansible(
        playbook_suffix="local/cloud-server/vpn/setup.yml",
        become_target_host="cloud-server",
    )
