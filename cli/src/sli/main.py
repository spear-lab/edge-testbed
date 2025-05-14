import os
import sys
from importlib.metadata import version

import rich
import rich.traceback
import typer

import sli.awx_cluster.main
import sli.cloud_server.main
import sli.configuration.main
import sli.master_nuc.main
from sli.utils.auxiliary import find_repo_root
from sli.utils.common import run_in_shell
from sli.utils.initial import handle_init_use
from sli.utils.logging import logger
from sli.utils.typer_augmentations import AliasGroup

rich.traceback.install(show_locals=True)
console = rich.console.Console()
app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]}, cls=AliasGroup)

app.add_typer(
    typer_instance=sli.configuration.main.app,
    name="configuration",
    help="Commands to manage and configure the Cartken ITM CLI",
)

app.add_typer(
    typer_instance=sli.cloud_server.main.app,
    name="cloud-server",
    help="Commands to interact with an cloud server",
)

app.add_typer(
    typer_instance=sli.awx_cluster.main.app,
    name="awx-cluster",
    help="Commands to interact with an AWX cluster",
)

app.add_typer(
    typer_instance=sli.master_nuc.main.app,
    name="master-nuc",
    help="Commands to interact with the master NUC",
)


@app.command(
    "version, v", help="Show the version of the currently installed SPEAR Edge-Testbed CLI"
)
def show_version():
    logger.info(f"SPEAR Edge-Testbed CLI version: '{version('spear-edge-testbed-cli')}'")


@app.command(
    "install-local-ansible-dependencies",
    help="Install necessary ansible dependencies on your local host",
)
def install_local_ansible_dependencies():
    # NOTE: The playbooks that SLI calls require ansible-galaxy roles to be installed on the calling machine.
    # Installing these dependencies via a dedicated playbook does not work due to ansible-access right issues.
    repo_root_path = find_repo_root()
    os.chdir(repo_root_path)
    run_in_shell(shell_cmd="make install-ansible-requirements")


def main():
    handle_init_use()
    if len(sys.argv) == 1:
        app(["--help"])
    else:
        app()


if __name__ == "__main__":
    main()
