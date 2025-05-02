"""Implementation of input-var-naming rule."""

from __future__ import annotations

from ansiblelint.errors import MatchError
from ansiblelint.file_utils import Lintable
from ansiblelint.rules import AnsibleLintRule
from ansiblelint.utils import parse_yaml_from_file


class InputVariableNamingRule(AnsibleLintRule):
    """Cartken input variable naming rules."""

    id = "input-var-naming"

    def matchyaml(self, file: Lintable) -> list[MatchError]:
        """Return matches for variables defined in argument_specs files."""
        results: list[MatchError] = []

        if str(file.kind) == "role-arg-spec" and file.data:
            specs = parse_yaml_from_file(str(file.path))
            options = specs.get("argument_specs", {}).get("main", {}).get("options", {})

            for option in options:
                if not str(option).startswith("_rin__"):
                    match_error = MatchError(
                        tag=f"{self.id}[role]",
                        message=f"Role input variable names must start with '_rin__'. ({option})",
                        rule=self,
                    )

                    # NOTE: Some properties cannot be set via constructor
                    match_error.filename = str(file.path)
                    match_error.lineno = option.ansible_pos[1]

                    results.append(match_error)
        else:
            results.extend(super().matchyaml(file))

        return results
