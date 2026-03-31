import pathlib
import re


TEMPLATE = pathlib.Path(__file__).parent.parent / "templates" / "index.html"


def _stylesheet() -> str:
    html = TEMPLATE.read_text()
    start = html.index("<style>")
    end = html.index("</style>") + len("</style>")
    return html[start:end]


def _body_rule() -> str:
    """Extract the declarations inside the body { ... } rule block."""
    css = _stylesheet()
    match = re.search(r"body\s*\{([^}]*)\}", css)
    assert match, "No body rule found in stylesheet"
    return match.group(1)


def test_font_family_is_verdana() -> None:
    assert "font-family: Verdana" in _body_rule()


def test_body_text_colour_is_blue() -> None:
    assert "color: blue" in _body_rule()


def test_old_font_stack_absent() -> None:
    assert "JetBrains Mono" not in _stylesheet()
