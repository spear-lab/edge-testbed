from __future__ import annotations

import configparser
import sys

from itm_cli.configuration.consts import ITM_CLI_CONFIG_PATH, ITM_CLI_USER_FOLDER_PATH
from itm_cli.configuration.keys.enums import ConfigKey, InternalConfigKey
from itm_cli.utils.logging import logger

_CONFIG_VERSION = "1"


def _check_local_config_valid() -> bool:
    if not ITM_CLI_CONFIG_PATH.is_file():
        return False
    config = open_local_config()
    if len(config.sections()) == 0:
        return False
    all_config_key_value_pairs = config.items(InternalConfigKey.CONFIG_MAIN_KEY.value)
    all_config_elements = [elem for sublist in all_config_key_value_pairs for elem in sublist]
    if InternalConfigKey.CONFIG_VERSION.value not in all_config_elements:
        return False
    local_config_version = get_config_value(InternalConfigKey.CONFIG_VERSION)
    return local_config_version == _CONFIG_VERSION


def open_local_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(ITM_CLI_CONFIG_PATH)
    return config


def update_config_value(key: ConfigKey, value: str) -> None:
    """NOTE: The config only supports strings."""
    config = open_local_config()
    config[InternalConfigKey.CONFIG_MAIN_KEY.value][key.value] = value  # type: ignore
    _update_config(config)


def get_config_value(key: ConfigKey, terminate_if_key_is_missing_from_conf: bool = True) -> str:
    config = open_local_config()[InternalConfigKey.CONFIG_MAIN_KEY.value]
    value_from_config = config.get(key.value, "")  # type: ignore
    if not value_from_config and terminate_if_key_is_missing_from_conf:
        _handle_missing_key_access_attempt(key)
    return value_from_config


def _update_config(config: configparser.ConfigParser) -> None:
    with open(ITM_CLI_CONFIG_PATH, "w") as config_file:
        config.write(config_file)


def _create_initial_unconfigured_config_file() -> None:
    if not ITM_CLI_CONFIG_PATH.exists():
        ITM_CLI_CONFIG_PATH.touch()
    config = configparser.ConfigParser()
    config[InternalConfigKey.CONFIG_MAIN_KEY.value] = {}
    _update_config(config=config)
    update_config_value(key=InternalConfigKey.CONFIG_VERSION, value=_CONFIG_VERSION)
    logger.info(
        "\n".join(
            (
                "New initial un-configured config file created for the Carkten ITM-CLI.",
                "It uses a minimal initial configuration.",
                "It can be displayed via 'itm configuration show-config'.",
                f"The config can be found at: '{ITM_CLI_CONFIG_PATH}'",
            )
        )
    )


def _check_user_itm_cli_folder_and_content() -> None:
    if not ITM_CLI_USER_FOLDER_PATH.is_dir():
        ITM_CLI_USER_FOLDER_PATH.mkdir(exist_ok=True)


def check_and_handle_config_file() -> None:
    _check_user_itm_cli_folder_and_content()
    if _check_local_config_valid():
        return
    logger.info("No config file found. Creating a new empty un-configured config file.")
    _create_initial_unconfigured_config_file()


def _handle_missing_key_access_attempt(key: ConfigKey) -> None:
    missing_key = key.value  # type: ignore
    logger.error(
        "\n".join(
            (
                f"The '{missing_key}' was not found in your Cartken ITM-CLI config.",
                "Please first configure it by running the matching Cartken ITM-CLI configuration cmd.",
                f"> itm configuration key-vars configure {missing_key}",
            )
        )
    )
    sys.exit(1)
