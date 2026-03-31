import pathlib


TEMPLATE = pathlib.Path(__file__).parent.parent / "templates" / "index.html"


def _stylesheet() -> str:
    html = TEMPLATE.read_text()
    start = html.index("<style>")
    end = html.index("</style>") + len("</style>")
    return html[start:end]


def test_font_family_is_verdana() -> None:
    assert "font-family: Verdana" in _stylesheet()


def test_body_text_colour_is_blue() -> None:
    assert "color: blue" in _stylesheet()
