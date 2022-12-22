from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import requests
from packaging.requirements import Requirement
from packaging.tags import sys_tags
from packaging.utils import parse_sdist_filename
from packaging.utils import parse_wheel_filename
from packaging.version import InvalidVersion
from packaging.version import Version

from pipfreeze2nix import pep503
from pipfreeze2nix.exceptions import MissingArtifactError
from pipfreeze2nix.pip_compile_parser import parse_compiled_requirements
from pipfreeze2nix.pip_compile_parser import RequirementTree
from pipfreeze2nix.pip_compile_parser import sorted_reverse_topological


# (done) step 0) get it working with sdists
# (done) step 1) get it working with wheels on current platform
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
    if len(req.specifier) != 1:
        raise ValueError(f"Requirement `{req}` has more than one specifier.")

    for specifier in req.specifier:
        if specifier.operator != "==":
            raise ValueError(f"Requirement `{req}` has a non-pinned specifier.")
        return Version(specifier.version)

    raise SystemExit(
        "Unexpected control flow in `parse_pinned_version` "
        f"when parsing requirement `{req}`. "
        "This should not be able to happen."
    )


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


def choose_wheel(
    artifacts: list[pep503.Artifact], name: str, pinned_version: Version
) -> pep503.Artifact | None:
    wheels = [artifact for artifact in artifacts if artifact.name.endswith(".whl")]
    compatible_tags = set(sys_tags())
    compatible_wheels = []
    for wheel in wheels:
        try:
            _, version, _, tags = parse_wheel_filename(wheel.name)
        except InvalidVersion:
            continue

        if version != pinned_version:
            continue

        for tag in tags:
            if tag in compatible_tags:
                compatible_wheels.append(wheel)
                break

    if not compatible_wheels:
        return None

    return compatible_wheels[0]


def choose_sdist(
    artifacts: list[pep503.Artifact], name: str, pinned_version: Version
) -> pep503.Artifact | None:
    compatible_sdists = []
    for artifact in artifacts:
        if not artifact.name.endswith(".tar.gz") or artifact.name.endswith(".zip"):
            continue

        try:
            _, version = parse_sdist_filename(artifact.name)
        except InvalidVersion:
            continue

        if version != pinned_version:
            continue

        compatible_sdists.append(artifact)

    if not compatible_sdists:
        return None

    return compatible_sdists[0]


def choose_artifact(req: Requirement) -> pep503.Artifact:
    pinned_version = parse_pinned_version(req)
    artifacts = pep503.get_artifacts(req.name)

    if (wheel_package := choose_wheel(artifacts, req.name, pinned_version)) is not None:
        return wheel_package

    if (sdist_package := choose_sdist(artifacts, req.name, pinned_version)) is not None:
        return sdist_package

    raise MissingArtifactError(f"Cannot find artifact for package {req}.")


def generate_build_python_package(requirement_tree: RequirementTree) -> str:
    req = requirement_tree.req

    # TODO: support other formats like pyproject
    artifact = choose_artifact(req)
    artifact_format = "wheel" if artifact.is_wheel else "setuptools"

    dependencies = textwrap.indent(
        "\n".join(sorted(requirement_tree.dependencies)),
        prefix="    ",
    )

    template = """\
    {name} = (python.pkgs.buildPythonPackage rec {{
      pname = "{name}";
      version = "{version}";
      format = "{artifact_format}";

      doCheck = false;

      propagatedBuildInputs = [
    {dependencies}
      ];

      src = builtins.fetchurl {{
        url = "{url}";
        sha256 = "{sha256}";
      }};
    }});
    """
    template = textwrap.dedent(template)
    return template.format(
        name=req.name,
        version=parse_pinned_version(req),
        artifact_format=artifact_format,
        dependencies=dependencies,
        url=artifact.url,
        sha256=get_artifact_sha256(artifact),
    )


FILE_TPL = """\
{{ python, nixpkgs }}:
let
{let_list}\
in
[
{package_list}
]
"""


def main(args: list[str]) -> None:
    args = args[1:]
    if len(args) != 1:
        raise SystemExit(
            textwrap.dedent(
                """\
                Proper usage:
                  pipfreeze2nix <path/to/requirements.txt>
                """,
            )
        )

    in_file = Path(args[0])
    if not in_file.is_absolute():
        in_file = Path.cwd() / in_file

    in_file_name = in_file.name
    in_file_name, _, _ = in_file_name.rpartition(".")
    out_file_name = f"{in_file_name}.nix"
    out_file = in_file.parent / out_file_name

    let_list = []
    package_list = []

    requirement_trees = parse_compiled_requirements(in_file)
    for i, requirement_tree in enumerate(sorted_reverse_topological(requirement_trees)):
        msg = (
            f"Processing {i + 1}/{len(requirement_trees)} "
            f"({(i + 1) / len(requirement_trees):.2%}) "
            f"{requirement_tree.req.name}"
        )
        print(msg, file=sys.stderr)

        let_list.append(
            textwrap.indent(
                generate_build_python_package(requirement_tree), prefix="  "
            )
        )
        if requirement_tree.is_direct:
            package_list.append(requirement_tree.req.name)

    out_file.write_text(
        FILE_TPL.format(
            let_list="".join(let_list),
            package_list=textwrap.indent("\n".join(sorted(package_list)), prefix="  "),
        ),
    )


def realmain() -> None:
    main(sys.argv)


if __name__ == "__main__":
    realmain()
