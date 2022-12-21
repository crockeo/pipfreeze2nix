from __future__ import annotations


class PipFreeze2NixError(Exception):
    pass


class Pep503Error(PipFreeze2NixError):
    """\
    Raised when we fail to parse some part of PEP503:
    https://peps.python.org/pep-0503/
    """

    pass


class PipCompileInvariantError(PipFreeze2NixError):
    """\
    Raised when an invariant of pip-compile output is violated.
    """

    pass


class MissingArtifactError(PipFreeze2NixError):
    """\
    Raised when we cannot find an artifact to satisfy a requirement.
    """

    pass
