from pipfreeze2nix import pep503


def test_make_url_absolute__already_absolute():
    url = "https://files.pythonhosted.org/path/to/artifact.whl"
    absolute_url = pep503.make_url_absolute(
        "https://packagestore.com/simple/somepackage/", url
    )
    assert absolute_url == url


def test_make_url_absolute__absolute_no_netloc():
    absolute_url = pep503.make_url_absolute(
        "https://packagestore.com/simple/somepackage/",
        "/some/other/path/someartifact.whl",
    )
    assert absolute_url == ("https://packagestore.com/some/other/path/someartifact.whl")


def test_make_url_absolute__relative():
    absolute_url = pep503.make_url_absolute(
        "https://packagestore.com/simple/somepackage/", "./someartifact.whl"
    )
    assert (
        absolute_url == "https://packagestore.com/simple/somepackage/someartifact.whl"
    )


def test_make_url_absolute__relative_parent():
    absolute_url = pep503.make_url_absolute(
        "https://packagestore.com/simple/somepackage/", "../../someartifact.whl"
    )
    assert absolute_url == "https://packagestore.com/someartifact.whl"
