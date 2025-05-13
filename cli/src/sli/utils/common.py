import enum
import json
import pathlib
import shlex
import subprocess
import getpass

import rich

from sli.utils.logging import logger


class CaptureOutputType(enum.Enum):
    TO_PYTHON_VAR = "to_python_var"
    TO_STDOUT = "to_stdout"
    HIDE_OUTPUT = "hide_output"


def clear_file(file: pathlib.Path) -> None:
    with open(file, "w"):
        return


def pretty_print_json(file_path: pathlib.Path) -> None:
    with open(file_path) as f:
        data = json.load(f)
    logger.info(f"'{file_path}':")
    rich.print_json(data=data)


def run_in_shell(
    shell_cmd: str,
    capture_output_type: CaptureOutputType = CaptureOutputType.TO_PYTHON_VAR,
    check: bool = True,
    text: bool = False,
    # NOTE: subprocess.run usually expects an array of strings as the cmd.
    # It is not able to handle pipes ("|"), etc.
    # If shell=True is enabled then it expects a single string as cmd and can handle pipes, etc.
    pure_shell: bool = False,
) -> subprocess.CompletedProcess[bytes]:
    pipe_to_use = None
    if capture_output_type == CaptureOutputType.HIDE_OUTPUT:
        pipe_to_use = subprocess.DEVNULL

    return subprocess.run(
        shell_cmd if pure_shell else shlex.split(shell_cmd),
        capture_output=(capture_output_type == CaptureOutputType.TO_PYTHON_VAR),
        stdout=pipe_to_use,
        stderr=pipe_to_use,
        check=check,
        text=text,
        shell=pure_shell,
    )

def ask_for_target_host_become_pwd(target_host: str) -> str:
    return getpass.getpass(f"[sudo] '{target_host}' password: ")
