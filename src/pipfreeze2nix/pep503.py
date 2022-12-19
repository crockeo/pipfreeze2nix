from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Optional

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


class SimpleParser(HTMLParser):
    def __init__(self):
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
                url=url,
                name=data,
                sha256=sha256,
            ),
        )


def get_artifacts(package: str) -> list[Artifact]:
    res = requests.get(f"https://pypi.org/simple/{package}")
    res.raise_for_status()

    parser = SimpleParser()
    parser.feed(res.text)
    return parser.artifacts
