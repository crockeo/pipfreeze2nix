from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import requests
from packaging.requirements import Requirement
from packaging.requirements import InvalidRequirement
from packaging.tags import sys_tags
from packaging.utils import parse_wheel_filename
from packaging.version import Version

from pipfreeze2nix import pep503
from pipfreeze2nix.pip_compile_parser import parse_compiled_requirements
from pipfreeze2nix.pip_compile_parser import RequirementTree


# (done) step 0) get it working with sdists
# step 1) get it working with wheels on current platform
# step 2) get it working with wheels across multiple platforms


# ok...trying to make this work with wheels is going to be fun :)
#
# 1. assume that the python used to build requirements.nix
#    is the same python that will be used to run the project
#
# 2. need to implement PEP <whatever> simple server parsing
#    and then find all available wheels for a pinned version of a thing
#
# 3. need to map from wheel name to nix system name
#    e.g.

# aarch64-darwin maps onto macosx_<number>_<number>-arm64.whl
#  - zope.interface-5.4.0-cp38-cp38-macosx_10_14_arm64.whl (217 kB)
#  - zope.interface-5.4.0-cp38-cp38-macosx_10_14_x86_64.whl (208 kB)
#
# arm64 -> aarch64
# x86_64 -> x86_64


def parse_pinned_version(req: Requirement) -> Version:
    for specifier in req.specifier:
        if specifier.operator != "==":
            # TODO: type
            raise Exception("invalid specifier, not pinned")
        return Version(specifier.version)
    # TODO: type
    raise Exception("no specifiers")


def fetch_artifact(url: str, cache_path: Path) -> None:
    with requests.get(url, stream=True) as stream:
        stream.raise_for_status()
        with open(cache_path, "wb") as f:
            for chunk in stream.iter_content(chunk_size=8192):
                f.write(chunk)


def get_artifact_sha256(artifact: pep503.Artifact) -> str:
    if artifact.sha256 is not None:
        return artifact.sha256

    cache_path = Path.home() / ".cache" / "pipfreeze2nix" / artifact.name.lower()
    if not cache_path.exists():
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        fetch_artifact(artifact.url, cache_path)

    sha256 = subprocess.check_output(
        ("sha256sum", cache_path),
        text=True,
    )
    sha256, _, _ = sha256.partition("  ")
    return sha256


def choose_wheel(artifacts: list[pep503.Artifact], name: str, pinned_version: Version) -> pep503.Artifact | None:
    wheels = [
        artifact
        for artifact in artifacts
        if artifact.name.endswith(".whl")
    ]
    compatible_tags = set(sys_tags())
    compatible_wheels = []
    for wheel in wheels:
        _, version, _, tags = parse_wheel_filename(wheel.name)
        if version != pinned_version:
            continue

        for tag in tags:
            break
        else:
            # TODO: exc type
            raise Exception("must have at least 1 tag...")

        if tag not in compatible_tags:
            continue

        compatible_wheels.append(wheel)

    if not compatible_wheels:
        return None

    return compatible_wheels[0]


def choose_sdist(artifacts: list[pep503.Artifact], name: str, pinned_version: Version) -> pep503.Artifact | None:
    # TODO: implement
    pass


def choose_artifact(req: Requirement) -> pep503.Artifact:
    pinned_version = parse_pinned_version(req)
    artifacts = pep503.get_artifacts(req.name)

    if (wheel_package := choose_wheel(artifacts, req.name, pinned_version)) is not None:
        return wheel_package

    if (sdist_package := choose_sdist(artifacts, req.name, pinned_version)) is not None:
        return sdist_package

    # TODO: type
    raise Exception(
        f"cannot find package for {req}"
    )


def generate_build_python_package(requirement_tree: RequirementTree) -> str:
    req = requirement_tree.req

    # TODO: support other formats like pyproject
    artifact = choose_artifact(req)
    artifact_format = "wheel" if artifact.is_wheel else "setuptools"

    dependencies = textwrap.indent("\n".join(requirement_tree.dependencies), prefix="    ")

    template = f"""\
    {req.name} = (python.pkgs.buildPythonPackage rec {{
      pname = "{req.name}";
      version = "{parse_pinned_version(req)}";
      format = "{artifact_format}";

      doCheck = false;

      propagatedBuildInputs = [
    {dependencies}
      ];

      src = builtins.fetchurl {{
        url = "{artifact.url}";
        sha256 = "{get_artifact_sha256(artifact)}";
      }};
    }});
    """
    template = textwrap.dedent(template)
    return template


FILE_TPL = """\
{{ python, nixpkgs }}:
let
{let_list}\
in
[
{package_list}\
]
"""


def main(args: list[str]) -> None:
    args = args[1:]
    if len(args) != 1:
        # TODO: error
        raise SystemExit("something")

    in_file = Path(args[0])
    if not in_file.is_absolute():
        in_file = Path.cwd() / in_file

    in_file_name = in_file.name
    in_file_name, _, _ = in_file_name.rpartition(".")
    out_file_name = f"{in_file_name}.nix"
    out_file = in_file.parent / out_file_name

    requirement_trees = sorted(
        list(parse_compiled_requirements(in_file).values()),
        key=lambda requirement_tree: len(requirement_tree.dependencies),
    )

    let_list = [
        textwrap.indent(generate_build_python_package(requirement_tree), prefix="  ")
        for requirement_tree in requirement_trees
    ]
    package_list = [
        requirement_tree.req.name
        for requirement_tree in requirement_trees
        if requirement_tree.is_direct
    ]

    out_file.write_text(
        FILE_TPL.format(
            let_list="".join(let_list),
            package_list="\n".join(package_list),
        ),
    )


def realmain() -> None:
    main(sys.argv)


if __name__ == "__main__":
    realmain()
