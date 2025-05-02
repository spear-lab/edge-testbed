import json
import pathlib

import rich

from itm_cli.utils.logging import logger


def clear_file(file: pathlib.Path) -> None:
    with open(file, "w"):
        return


def pretty_print_json(file_path: pathlib.Path) -> None:
    with open(file_path) as f:
        data = json.load(f)
    logger.info(f"'{file_path}':")
    rich.print_json(data=data)
