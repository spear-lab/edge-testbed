from importlib.metadata import version

import rich
import rich.traceback
import typer

import itm_cli.cluster.main
import itm_cli.configuration.main
from itm_cli.utils.initial import handle_init_use
from itm_cli.utils.logging import logger
from itm_cli.utils.typer_augmentations import AliasGroup

rich.traceback.install(show_locals=True)
console = rich.console.Console()
app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]}, cls=AliasGroup)


@app.command("version, v", help="Show the version of the currently installed Cartken-ITM-CLI")
def show_version():
    logger.info(f"Cartken-ITM-CLI version: '{version('itm-cli')}'")


app.add_typer(
    typer_instance=itm_cli.configuration.main.app,
    name="configuration, conf",
    help="Commands to manage and configure the Cartken ITM CLI",
)
app.add_typer(
    typer_instance=itm_cli.cluster.main.app,
    name="cluster, c",
    help="Commands to interact with an AWX cluster",
)


def main():
    handle_init_use()
    app()


if __name__ == "__main__":
    main()
