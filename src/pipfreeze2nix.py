from __future__ import annotation

import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

import requests
from packaging.requirements import Requirement
from packaging.requirements import InvalidRequirement
from packaging.utils import canonicalize_name
from packaging.utils import parse_wheel_filename
from packaging.version import Version


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


@dataclass
class NixSystem:
    architecture: str
    # TODO: rename this to be operating system when i have my LSP up and running again
    platform: str

    @property
    def python_architecture(self) -> str:
        if self.architecture == "aarch64":
            return "arm64"
        return self.architecture

    @staticmethod
    def parse(raw_nix_system: str) -> NixSystem:
        architecture, _, platform = raw_nix_system.partition("-")
        return NixSystem(
            architecture=architecture,
            platform=platform,
        )


@dataclass
class WheelInfo:
    dist: str
    python: str
    abi: str
    platform: str

    def compatible_with_nix_system(self, nix_system: NixSystem) -> bool:
        operating_system, architecture = self.split_platform()
        if nix_system.platform == "darwin":
            if not operating_system.startswith("macosx"):
                return False
        elif nix_system.platform == "linux":
            if (
                not operating_system.startswith("linux")
                and not operating_system.startswith("manylinux")
            ):
                return False
        else:
            # TODO: exception type
            raise Exception(f"unknown platform: {nix_system.platform}")

        if "architecture" != "any" and nix_system.python_architecture != architecture:
            return False

        return True

    def split_platform(self) -> tuple[str, str]:
        if self.platform == "any":
            return ("any", "any")

        if self.platform.endswith("x86_64"):
            # `x86_64` is the only architecture which includes a `_`
            # so we can't use a sane `rpartition("_")` strategy on it
            # so we special case it instead!
            operating_system = self.platform[:-len("x86_64")]
            architecture = "x86_64"
        else:
            operating_system, _, architecture = self.platform.rpartition("_")

        return operating_system, architecture

    def render(self) -> str:
        template = """\
        format = "wheel";
        dist = "{dist}";
        python = "{python}";
        abi = "{abi}";
        platform = "{platform}";
        """
        template = textwrap.dedent(template)
        return template.format(
            dist=self.dist,
            python=self.python,
            abi=self.abi,
            platform=self.platform,
        )


@dataclass
class PythonPackage:
    name: str
    version: Version
    sha256: str
    wheel_info: WheelInfo | None = None

    def render(self) -> str:
        template = """\
        (python.pkgs.buildPythonPackage rec {{
          pname = "{name}";
          version = "{version}";

          src = python.pkgs.fetchPypi {{
            inherit pname version;
            sha256 = "{sha256}";
            {format_info}
          }};
        }})
        """
        template = textwrap.dedent(template)

        if self.wheel_info is None:
            format_info = "format = \"setuptools\";"
        else:
            format_info = textwrap.indent(wheel_info.render(), prefix="    ")

        return template.format(
            name=self.name,
            version=self.version,
            sha256=self.sha256,
            format_info=format_info,
        )


def parse_pinned_version(req: Requirement) -> Version:
    for specifier in req.specifier:
        if specifier.operator != "==":
            # TODO: type
            raise Exception("invalid specifier, not pinned")
        return Version(specifier.version)
    # TODO: type
    raise Exception("no specifiers")


def get_requirement_mirror_suffix(req: Requirement) -> str:
    first_letter = req.name[0].lower()
    name = canonicalize_name(req.name)
    version = parse_pinned_version(req)
    return f"{first_letter}/{name}/{name}-{version}.tar.gz"


def get_requirement_mirror_url(req: Requirement) -> str:
    return f"https://files.pythonhosted.org/packages/source/{get_requirement_mirror_suffix(req)}"


def get_requirement_cache_path(req: Requirement) -> Path:
    cache_dir = Path.home() / ".cache" / "pipfreeze2nix"
    filename = f"{req.name}-{parse_pinned_version(req)}.tar.gz"
    return cache_dir / filename


def fetch_requirement(req: Requirement) -> Path:
    req_cache_path = get_requirement_cache_path(req)
    if not req_cache_path.exists():
        req_cache_path.parent.mkdir(exist_ok=True, parents=True)

        mirror_url = get_requirement_mirror_url(req)

        with requests.get(mirror_url, stream=True) as stream:
            stream.raise_for_status()
            with open(req_cache_path, "wb") as f:
                for chunk in stream.iter_content(chunk_size=8192):
                    f.write(chunk)
    return req_cache_path


def fetch_python_package(req: Requirement) -> PythonPackage:
    path = fetch_requirement(req)

    # TODO: don't shell out to sha256sum for this,
    # do it in-process instead!
    sha256 = subprocess.check_output(
        ("sha256sum", path),
        text=True,
    )
    sha256, _, _ = sha256.partition("  ")

    return PythonPackage(
        name=req.name,
        version=parse_pinned_version(req),
        sha256=sha256,
    )


FILE_TPL = """\
{{ python, nixpkgs }}:
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

    requirements = []
    for line in in_file.read_text().splitlines():
        line = line.strip()
        line, _, _, = line.partition("#")
        if not line:
            continue

        try:
            req = Requirement(line)
        except InvalidRequirement:
            print(f"warning: invalid requirement {line}", file=sys.stderr)
            continue

        requirements.append(req)

    python_packages = [
        fetch_python_package(req)
        for req in requirements
    ]
    packages = [
        textwrap.indent(python_package.render(), "  ")
        for python_package in python_packages
    ]

    out_file.write_text(FILE_TPL.format(package_list="".join(packages)))


def realmain() -> None:
    main(sys.argv)


if __name__ == "__main__":
    realmain()
