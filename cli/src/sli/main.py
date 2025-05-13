import sys
from importlib.metadata import version

import rich
import rich.traceback
import typer

import sli.awx_cluster.main
from sli.utils.common import run_in_shell
from sli.utils.initial import handle_init_use
from sli.utils.logging import logger
from sli.utils.typer_augmentations import AliasGroup

rich.traceback.install(show_locals=True)
console = rich.console.Console()
app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]}, cls=AliasGroup)


ANSIBLE_GALAXY_ROLES = " ".join(("geerlingguy.docker", "gantsign.golang"))


@app.command(
    "version, v", help="Show the version of the currently installed SPEAR Edge-Testbed CLI"
)
def show_version():
    logger.info(f"SPEAR Edge-Testbed CLI version: '{version('spear-edge-testbed-cli')}'")


@app.command(
    "install-local-ansible-dependencies, ilad",
    help="Install necessary ansible dependencies on your local host",
)
def install_local_ansible_dependencies():
    # NOTE: The playbooks that SLI calls require ansible-galaxy roles to be installed on the calling machine.
    # Installing these dependencies via a dedicated playbook does not work due to ansible-access right issues.
    run_in_shell(shell_cmd=f"ansible-galaxy install {ANSIBLE_GALAXY_ROLES}")


app.add_typer(
    typer_instance=sli.awx_cluster.main.app,
    name="awx-cluster, ac",
    help="Commands to interact with an AWX cluster",
)


def main():
    handle_init_use()
    if len(sys.argv) == 1:
        app(["--help"])
    else:
        app()


if __name__ == "__main__":
    main()
