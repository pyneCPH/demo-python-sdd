import datetime
import json
import textwrap
import urllib.request
from pathlib import Path
from typing import TypedDict


class QuoteData(TypedDict):
    text: str
    author: str


CACHE_PATH = Path.home() / ".cache" / "weather-cli" / "quote_cache.json"
API_URL = "https://zenquotes.io/api/today"


def fetch_quote() -> QuoteData | None:
    try:
        with urllib.request.urlopen(API_URL, timeout=5) as response:
            data = json.loads(response.read().decode())
        return QuoteData(text=data[0]["q"], author=data[0]["a"])
    except Exception:
        return None


def get_daily_quote() -> QuoteData | None:
    today = datetime.date.today().isoformat()
    stale_quote: QuoteData | None = None

    try:
        cache_data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        if cache_data.get("date") == today:
            return QuoteData(text=cache_data["text"], author=cache_data["author"])
        stale_quote = QuoteData(text=cache_data["text"], author=cache_data["author"])
    except Exception:
        pass

    quote = fetch_quote()
    if quote is None:
        return stale_quote

    try:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(
            json.dumps({"date": today, **quote}),
            encoding="utf-8",
        )
    except Exception:
        pass

    return quote


def format_quote_box(quote: QuoteData, max_width: int = 60) -> str:
    inner_width = max_width - 4  # 2 for "│ " and " │"
    quoted_text = f'"{quote["text"]}"'
    wrapped_lines = textwrap.wrap(quoted_text, width=inner_width)
    author_line = f"\u2014 {quote['author']}"
    wrapped_author = textwrap.wrap(author_line, width=inner_width)

    content_width = inner_width

    top = f"\u250c\u2500{'\u2500' * content_width}\u2500\u2510"
    bottom = f"\u2514\u2500{'\u2500' * content_width}\u2500\u2518"

    rows = (
        [top]
        + [f"\u2502 {line:<{content_width}} \u2502" for line in wrapped_lines]
        + [f"\u2502 {line:>{content_width}} \u2502" for line in wrapped_author]
        + [bottom]
    )

    return "\n".join(rows)
