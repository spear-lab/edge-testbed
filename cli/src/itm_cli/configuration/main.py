import rich
import typer

from itm_cli.configuration.common import check_and_handle_config_file, open_local_config
from itm_cli.configuration.consts import ITM_CLI_CONFIG_PATH
from itm_cli.configuration.security.main import get_vault_pwd_file_path
from itm_cli.utils.common import clear_file
from itm_cli.utils.logging import logger
from itm_cli.utils.typer_augmentations import AliasGroup

app = typer.Typer(cls=AliasGroup)


@app.command("show-config, s", help="Show the current Cartken ITM-CLI configuration")
def show_config():
    check_and_handle_config_file()
    config = open_local_config()
    logger.info(f"'{ITM_CLI_CONFIG_PATH}':")
    for section in config.sections():
        rich.print_json(data=dict(config.items(section)))


@app.command(
    "reset-config", help="Reset the current Cartken ITM-CLI configuration to its initial state"
)
def reset_config():
    clear_file(ITM_CLI_CONFIG_PATH)
    check_and_handle_config_file()


@app.command("reset-vault-pwd", help="Reset the locally stored vault password")
def reset_vault_pwd():
    clear_file(get_vault_pwd_file_path())
    get_vault_pwd_file_path()
