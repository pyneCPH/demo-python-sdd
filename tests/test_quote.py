import json
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from quote import QuoteData, fetch_quote, format_quote_box, get_daily_quote


class MockResponse:
    def __init__(self, data: bytes) -> None:
        self._data = BytesIO(data)

    def read(self) -> bytes:
        return self._data.read()

    def __enter__(self) -> "MockResponse":
        return self

    def __exit__(self, *args: object) -> None:
        pass


# --- fetch_quote tests ---


@patch("quote.urllib.request.urlopen")
def test_fetch_quote_success(mock_urlopen: object) -> None:
    response_data = json.dumps(
        [{"q": "Be the change.", "a": "Gandhi", "h": "<p>Be the change.</p>"}]
    ).encode()
    mock_urlopen.return_value = MockResponse(response_data)  # type: ignore[attr-defined]

    result = fetch_quote()

    assert result is not None
    assert result["text"] == "Be the change."
    assert result["author"] == "Gandhi"


@patch("quote.urllib.request.urlopen")
def test_fetch_quote_network_failure(mock_urlopen: object) -> None:
    mock_urlopen.side_effect = OSError("Network unreachable")  # type: ignore[attr-defined]

    result = fetch_quote()
    assert result is None


@patch("quote.urllib.request.urlopen")
def test_fetch_quote_malformed_json(mock_urlopen: object) -> None:
    mock_urlopen.return_value = MockResponse(b"not json")  # type: ignore[attr-defined]

    result = fetch_quote()
    assert result is None


# --- get_daily_quote tests ---


@patch("quote.fetch_quote")
def test_get_daily_quote_cache_hit(mock_fetch: object, tmp_path: Path) -> None:
    import datetime

    cache_file = tmp_path / "quote_cache.json"
    today = datetime.date.today().isoformat()
    cache_file.write_text(
        json.dumps({"date": today, "text": "Cached quote.", "author": "Author"})
    )

    with patch("quote.CACHE_PATH", cache_file):
        result = get_daily_quote()

    assert result is not None
    assert result["text"] == "Cached quote."
    assert result["author"] == "Author"
    mock_fetch.assert_not_called()  # type: ignore[attr-defined]


@patch("quote.fetch_quote")
def test_get_daily_quote_cache_miss(mock_fetch: object, tmp_path: Path) -> None:
    cache_file = tmp_path / "subdir" / "quote_cache.json"
    mock_fetch.return_value = QuoteData(text="Fresh quote.", author="New Author")  # type: ignore[attr-defined]

    with patch("quote.CACHE_PATH", cache_file):
        result = get_daily_quote()

    assert result is not None
    assert result["text"] == "Fresh quote."
    assert result["author"] == "New Author"
    assert cache_file.exists()
    cached = json.loads(cache_file.read_text())
    assert cached["text"] == "Fresh quote."


@patch("quote.fetch_quote")
def test_get_daily_quote_cache_stale(mock_fetch: object, tmp_path: Path) -> None:
    cache_file = tmp_path / "quote_cache.json"
    cache_file.write_text(
        json.dumps({"date": "2020-01-01", "text": "Old quote.", "author": "Old"})
    )
    mock_fetch.return_value = QuoteData(text="New quote.", author="New")  # type: ignore[attr-defined]

    with patch("quote.CACHE_PATH", cache_file):
        result = get_daily_quote()

    assert result is not None
    assert result["text"] == "New quote."
    mock_fetch.assert_called_once()  # type: ignore[attr-defined]


@patch("quote.fetch_quote")
def test_get_daily_quote_api_failure_no_cache(
    mock_fetch: object, tmp_path: Path
) -> None:
    cache_file = tmp_path / "quote_cache.json"
    mock_fetch.return_value = None  # type: ignore[attr-defined]

    with patch("quote.CACHE_PATH", cache_file):
        result = get_daily_quote()

    assert result is None


@patch("quote.fetch_quote")
def test_get_daily_quote_api_failure_stale_cache(
    mock_fetch: object, tmp_path: Path
) -> None:
    cache_file = tmp_path / "quote_cache.json"
    cache_file.write_text(
        json.dumps({"date": "2020-01-01", "text": "Old quote.", "author": "Old"})
    )
    mock_fetch.return_value = None  # type: ignore[attr-defined]

    with patch("quote.CACHE_PATH", cache_file):
        result = get_daily_quote()

    assert result is None


# --- format_quote_box tests ---


def test_format_quote_box_short_quote() -> None:
    quote = QuoteData(text="Be the change.", author="Gandhi")
    result = format_quote_box(quote)

    assert "\u250c" in result  # ┌
    assert "\u2510" in result  # ┐
    assert "\u2514" in result  # └
    assert "\u2518" in result  # ┘
    assert "\u2502" in result  # │
    assert "Be the change." in result
    assert "Gandhi" in result
    assert "\u2014" in result  # em dash


def test_format_quote_box_long_quote() -> None:
    quote = QuoteData(
        text="This is a very long motivational quote that should definitely wrap across multiple lines when rendered inside the box",
        author="A Wise Person",
    )
    result = format_quote_box(quote, max_width=40)
    lines = result.split("\n")

    # Should have more than 4 lines (top + at least 2 text + author + bottom)
    assert len(lines) > 4
    # All middle lines should be the same width
    widths = {len(line) for line in lines}
    assert len(widths) == 1  # all lines same width


def test_format_quote_box_structure() -> None:
    quote = QuoteData(text="Hello.", author="World")
    result = format_quote_box(quote)
    lines = result.split("\n")

    assert lines[0].startswith("\u250c")
    assert lines[0].endswith("\u2510")
    assert lines[-1].startswith("\u2514")
    assert lines[-1].endswith("\u2518")
    for line in lines[1:-1]:
        assert line.startswith("\u2502")
        assert line.endswith("\u2502")
