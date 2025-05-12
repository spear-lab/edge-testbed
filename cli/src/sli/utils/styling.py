import rich
from typing import ContextManager

# Reference: https://rich.readthedocs.io/en/latest/appendix/colors.html
GREEN = "light_green"

def create_spinner_context_manager(message: str, style: str = GREEN) -> ContextManager:
    return rich.console.Console().status(f"[{style}]{message}")

