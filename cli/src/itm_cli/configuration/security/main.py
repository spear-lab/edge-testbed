import pathlib

import typer

from itm_cli.configuration.consts import ITM_CLI_USER_FOLDER_PATH

VAULT_PWD_FILE = ITM_CLI_USER_FOLDER_PATH / ".vault_pwd"


def get_vault_pwd_file_path() -> pathlib.Path:
    check_vault_pwd_file()
    return VAULT_PWD_FILE


def check_vault_pwd_file() -> None:
    if VAULT_PWD_FILE.is_file() and VAULT_PWD_FILE.stat().st_size > 0:
        return

    typed_pwd = typer.prompt("Please provide the Vault password", hide_input=True)
    VAULT_PWD_FILE.write_text(typed_pwd)
