import pathlib

from git import Repo


def get_current_branch_name() -> str:
    repo = Repo(search_parent_directories=True)
    return repo.active_branch.name


def find_it_management_root(
    path: pathlib.Path = pathlib.Path(__file__).resolve(),
) -> pathlib.Path:
    git_root = path / ".git"
    if git_root.exists():
        return path
    parent = path.parent
    if parent == path:
        raise FileNotFoundError("The IT-management repository root was not found.")
    return find_it_management_root(parent)
