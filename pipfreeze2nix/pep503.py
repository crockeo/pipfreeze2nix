from __future__ import annotations

import os
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional
from urllib.parse import urlsplit
from urllib.parse import urlunsplit

import requests

from pipfreeze2nix.exceptions import Pep503Error


@dataclass(frozen=True)
class Artifact:
    url: str
    name: str
    sha256: Optional[str]

    @property
    def is_wheel(self) -> bool:
        return self.name.endswith(".whl")


def make_url_absolute(package_url: str, url: str) -> str:
    _, netloc, path, query, fragment = urlsplit(url)
    if netloc:
        return url

    package_scheme, package_netloc, package_path, _, _ = urlsplit(package_url)
    package_path = Path(package_path)

    path = Path(path)
    if path.is_absolute():
        result_path = path
    else:
        result_path = package_path / path
    result_path = result_path.resolve()

    return urlunsplit(
        (package_scheme, package_netloc, str(result_path), query, fragment)
    )


class SimpleParser(HTMLParser):
    def __init__(self, package_url: str):
        self.package_url = package_url
        super().__init__()
        self.artifacts = []
        self.last_tag = (
            (""),
            (""),
        )

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.last_tag = (tag, dict(attrs))

    def handle_data(self, data: str) -> None:
        last_tag, last_attrs = self.last_tag
        if not last_tag or not last_attrs:
            return

        if last_tag != "a":
            return

        url = last_attrs["href"]
        if url is None:
            raise Pep503Error("Every anchor must have an associated `href` attribute.")

        url, _, sha256 = url.partition("#")
        if sha256:
            _, _, sha256 = sha256.partition("=")
        else:
            sha256 = None

        self.artifacts.append(
            Artifact(
                url=make_url_absolute(self.package_url, url),
                name=data,
                sha256=sha256,
            ),
        )


def get_index_url() -> str:
    if pip_index := os.environ.get("PIP_INDEX_URL"):
        if not pip_index.endswith("/"):
            pip_index = f"{pip_index}/"
        return pip_index
    return "https://pypi.org/simple/"


def get_artifacts(package: str) -> list[Artifact]:
    package_url = f"{get_index_url()}{package}/"
    res = requests.get(package_url)
    res.raise_for_status()

    parser = SimpleParser(package_url)
    parser.feed(res.text)
    return parser.artifacts
