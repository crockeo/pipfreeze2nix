from __future__ import annotations

import bisect
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from packaging.requirements import InvalidRequirement
from packaging.requirements import Requirement

from pipfreeze2nix.exceptions import PipCompileInvariantError


@dataclass(frozen=True)
class RequirementTree:
    req: Requirement
    is_direct: bool
    dependencies: frozenset[str]


@dataclass(frozen=True)
class _InverseRequirementTree:
    req: Requirement
    is_direct: bool
    depended_on_by: set[str]


def segment_compiled_requirements(lines: list[str]) -> list[list[str]]:
    segments = []
    current_segment = []
    for i, line in enumerate(lines):
        contents, _, comment = line.partition("#")
        contents, comment = (contents.strip(), comment.strip())
        if contents and comment:
            raise PipCompileInvariantError(
                f"Comment and non-comment contents on the same line ({i}): {line}",
            )

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


def parse_segment(segment: list[str]) -> _InverseRequirementTree:
    if not len(segment) >= 2:
        raise PipCompileInvariantError(
            "Each segment (requirement and `via` comments) "
            "must be at least 2 elements long, "
            f"not {len(segment)}: {segment}",
        )

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

    return _InverseRequirementTree(
        req=req,
        is_direct=is_direct,
        depended_on_by=set(depended_on_by),
    )


def parse_compiled_requirements(requirements_txt: Path) -> list[RequirementTree]:
    lines = requirements_txt.read_text().splitlines()
    segments = segment_compiled_requirements(lines)
    inverse_trees = [parse_segment(segment) for segment in segments]

    dependencies: dict[str, set[str]] = defaultdict(set)
    for inverse_tree in inverse_trees:
        for depender in inverse_tree.depended_on_by:
            dependencies[depender].add(inverse_tree.req.name)

    return [
        RequirementTree(
            req=inverse_tree.req,
            is_direct=inverse_tree.is_direct,
            dependencies=frozenset(dependencies[inverse_tree.req.name]),
        )
        for inverse_tree in inverse_trees
    ]


class _RequirementTreeGraph:
    def __init__(self, requirement_trees: Iterable[RequirementTree]):
        self.table = {}
        self.graph = defaultdict(set)
        self.inverse_graph = defaultdict(set)
        for requirement_tree in requirement_trees:
            self.table[requirement_tree.req.name] = requirement_tree
            self.graph[requirement_tree.req.name] = set(requirement_tree.dependencies)

            if requirement_tree.req.name not in self.inverse_graph:
                self.inverse_graph[requirement_tree.req.name] = set()

            for dependency in requirement_tree.dependencies:
                self.inverse_graph[dependency].add(requirement_tree.req.name)

        self.no_incoming_nodes = []
        for node, parents in self.inverse_graph.items():
            if not parents:
                bisect.insort(self.no_incoming_nodes, node)

    def get_requirement_tree(self, name: str) -> RequirementTree:
        return self.table[name]

    def next_node(self) -> str | None:
        if not self.no_incoming_nodes:
            return None
        node = self.no_incoming_nodes.pop()

        dependencies = self.graph[node]
        for dependency in dependencies:
            self.inverse_graph[dependency].remove(node)
            if not self.inverse_graph[dependency]:
                bisect.insort(self.no_incoming_nodes, dependency)

        del self.graph[node]
        del self.inverse_graph[node]

        return node


def sorted_reverse_topological(
    requirement_trees: Iterable[RequirementTree],
) -> list[RequirementTree]:
    """\
    Returns the provided RequirementTrees sorted by:

    - PRIMARY: Reverse topological order.
    - SECONDARY: Lexicographic order.
    """

    sorted_requirement_trees = []
    graph = _RequirementTreeGraph(requirement_trees)
    while (node := graph.next_node()) is not None:
        sorted_requirement_trees.append(graph.get_requirement_tree(node))
    sorted_requirement_trees.reverse()
    return sorted_requirement_trees
