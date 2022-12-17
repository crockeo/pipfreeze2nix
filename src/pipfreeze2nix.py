import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

import requests
from packaging.requirements import Requirement
from packaging.requirements import InvalidRequirement
from packaging.utils import canonicalize_name


def parse_pinned_version(req: Requirement) -> str:
    for specifier in req.specifier:
        if specifier.operator != "==":
            # TODO: type
            raise Exception("invalid specifier, not pinned")
        return specifier.version
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


@dataclass
class RequirementInfo:
    pname: str
    version: str
    sha256: str


def fetch_requirement_info(req: Requirement) -> RequirementInfo:
    path = fetch_requirement(req)

    sha256 = subprocess.check_output(
        ("sha256sum", path),
        text=True,
    )
    sha256, _, _ = sha256.partition("  ")

    return RequirementInfo(
        pname=req.name,
        version=parse_pinned_version(req),
        sha256=sha256,
    )


FILE_TPL = """\
{{ python, nixpkgs }}:
[
  {package_list}
]
"""


PACKAGE_TPL = """\
(python.pkgs.buildPythonPackage rec {{
  pname = "{pname}";
  version = "{version}";

  src = python.pkgs.fetchPypi {{
    inherit pname version;
    sha256 = "{sha256}";
  }};
}})
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

    req_infos = [
        fetch_requirement_info(req)
        for req in requirements
    ]
    packages = [
        textwrap.indent(
            PACKAGE_TPL.format(
                pname=req_info.pname,
                version=req_info.version,
                sha256=req_info.sha256,
            ),
            prefix="  ",
        )
        for req_info in req_infos
    ]

    out_file.write_text(FILE_TPL.format(package_list="".join(packages)))


def realmain() -> None:
    main(sys.argv)


if __name__ == "__main__":
    realmain()
