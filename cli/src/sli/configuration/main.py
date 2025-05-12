import rich
import typer

from sli.configuration.common import check_and_handle_config_file, open_local_config
from sli.configuration.consts import SLI_CONFIG_PATH
from sli.configuration.security.main import get_vault_pwd_file_path
from sli.utils.common import clear_file
from sli.utils.logging import logger
from sli.utils.typer_augmentations import AliasGroup

app = typer.Typer(cls=AliasGroup)


@app.command("show-config, s", help="Show the current SPEAR Edge-Testbed CLI configuration")
def show_config():
    check_and_handle_config_file()
    config = open_local_config()
    logger.info(f"'{SLI_CONFIG_PATH}':")
    for section in config.sections():
        rich.print_json(data=dict(config.items(section)))


@app.command(
    "reset-config", help="Reset the current SPEAR Edge-Testbed CLI configuration to its initial state"
)
def reset_config():
    clear_file(SLI_CONFIG_PATH)
    check_and_handle_config_file()


@app.command("reset-vault-pwd", help="Reset the locally stored vault password")
def reset_vault_pwd():
    clear_file(get_vault_pwd_file_path())
    get_vault_pwd_file_path()
