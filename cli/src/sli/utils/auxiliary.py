import pathlib

from git import Repo


def get_current_branch_name() -> str:
    repo = Repo(search_parent_directories=True)
    return repo.active_branch.name


def find_repo_root(
    path: pathlib.Path = pathlib.Path(__file__).resolve(),
) -> pathlib.Path:
    git_root = path / ".git"
    if git_root.exists():
        return path
    parent = path.parent
    if parent == path:
        raise FileNotFoundError("The edge-testbed repository root was not found.")
    return find_repo_root(parent)

def get_playbook_path(playbook_suffix: str) -> pathlib.Path:
    return find_repo_root() / "playbooks" / playbook_suffix
