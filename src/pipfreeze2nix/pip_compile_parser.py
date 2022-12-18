from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

from packaging.requirements import InvalidRequirement, Requirement


@dataclass(frozen=True)
class RequirementTree:
    name: str
    dependencies: set[str] = field(default_factory=set)


def parse_compiled_requirements(requirements_txt: Path) -> dict[str, RequirementTree]:
    # TODO: this is some UGLY code. rewrite?
    requirement_trees = {}
    last_req = None
    for line in requirements_txt.read_text().splitlines():
        contents, _, comment = line.partition("#")
        contents = contents.strip()
        comment = comment.strip()
        if contents and comment:
            raise Exception("oops, only supposed to be one")

        if contents:
            try:
                req = Requirement(contents)
            except InvalidRequirement:
                print(f"warning: invalid requirement {line}", file=sys.stderr)
                continue

            last_req = req.name
            if req.name not in requirement_trees:
                requirement_trees[req.name] = RequirementTree(req.name)

        if comment:
            if not comment.startswith("via "):
                continue
            comment = comment[len("via "):]
            if comment.startswith("-r "):
                continue

            if comment not in requirement_trees:
                requirement_trees[comment] = RequirementTree(comment)
            if last_req is not None:
                requirement_trees[comment].dependencies.add(last_req)

    return requirement_trees
