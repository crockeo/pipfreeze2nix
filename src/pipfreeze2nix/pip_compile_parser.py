from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from packaging.requirements import InvalidRequirement
from packaging.requirements import Requirement


@dataclass(frozen=True)
class RequirementTree:
    req: Requirement
    is_direct: bool
    dependencies: set[str]


@dataclass(frozen=True)
class InverseRequirementTree:
    req: Requirement
    is_direct: bool
    depended_on_by: set[str]


def segment_compiled_requirements(lines: list[str]) -> list[list[str]]:
    segments = []
    current_segment = []
    for line in lines:
        contents, _, comment = line.partition("#")
        contents, comment = (contents.strip(), comment.strip())
        if contents and comment:
            raise Exception("oops, only supposed to be one in normal output?")

        if contents:
            try:
                Requirement(contents)
            except InvalidRequirement:
                continue

            if current_segment:
                segments.append(current_segment)
                current_segment = []
            current_segment.append(contents)

        if comment and current_segment:
            current_segment.append(comment)

    if current_segment:
        segments.append(current_segment)

    return segments


def parse_segment(segment: list[str]) -> InverseRequirementTree:
    if not len(segment) >= 2:
        # TODO: exc
        raise Exception("invalid asf brother")

    req = Requirement(segment[0])
    depended_on_by = segment[1:]
    if depended_on_by[0] == "via":
        depended_on_by = depended_on_by[1:]
    for i, name in enumerate(depended_on_by):
        if name.startswith("via "):
            depended_on_by[i] = name[len("via ") :]

    to_remove = []
    is_direct = False
    for i, name in enumerate(depended_on_by):
        if name.startswith("-r "):
            is_direct = True
            to_remove.append(i)

    for i in reversed(to_remove):
        depended_on_by.pop(i)

    return InverseRequirementTree(
        req=req,
        is_direct=is_direct,
        depended_on_by=set(depended_on_by),
    )


def parse_compiled_requirements(requirements_txt: Path) -> dict[str, RequirementTree]:
    lines = requirements_txt.read_text().splitlines()
    segments = segment_compiled_requirements(lines)
    inverse_trees = [parse_segment(segment) for segment in segments]

    requirement_trees = {}
    for inverse_tree in sorted(
        inverse_trees,
        key=lambda inverse_tree: len(inverse_tree.depended_on_by),
    ):
        requirement_trees[inverse_tree.req.name] = RequirementTree(
            req=inverse_tree.req,
            is_direct=inverse_tree.is_direct,
            dependencies=set(),
        )
        for dependent in inverse_tree.depended_on_by:
            requirement_trees[dependent].dependencies.add(inverse_tree.req.name)
    return requirement_trees
