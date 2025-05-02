from itm_cli.configuration.common import check_and_handle_config_file
from itm_cli.configuration.consts import ITM_CLI_USER_FOLDER_PATH

_INIT_FILE_PATH = ITM_CLI_USER_FOLDER_PATH / ".init_flag"


def handle_init_use() -> None:
    if not _is_init_use():
        return

    check_and_handle_config_file()
    _INIT_FILE_PATH.touch()


def _is_init_use() -> bool:
    return not _INIT_FILE_PATH.exists()
