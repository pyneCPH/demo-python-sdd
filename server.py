import json
import math
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from weather import get_cities, get_forecast, get_location, get_weather

TEMPLATES_DIR = Path(__file__).parent / "templates"


class RateLimiter:
    _LIMIT = 60  # max requests
    _WINDOW = 60.0  # seconds

    def __init__(self) -> None:
        self._store: dict[str, deque[float]] = {}

    def is_allowed(self, ip: str) -> tuple[bool, int]:
        now = time.monotonic()
        if ip not in self._store:
            self._store[ip] = deque()
        timestamps = self._store[ip]
        # Evict timestamps outside the window
        while timestamps and now - timestamps[0] >= self._WINDOW:
            timestamps.popleft()
        if len(timestamps) >= self._LIMIT:
            retry_after = math.ceil(self._WINDOW - (now - timestamps[0]))
            return False, retry_after
        timestamps.append(now)
        return True, 0


_rate_limiter = RateLimiter()


class WeatherHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/":
            self._serve_index()
        elif self.path == "/api/weather":
            self._serve_weather_api()
        elif self.path == "/api/cities":
            self._serve_cities_api()
        elif self.path.startswith("/api/forecast"):
            self._serve_forecast_api()
        else:
            self._send_not_found()

    def _serve_index(self) -> None:
        index_path = TEMPLATES_DIR / "index.html"
        try:
            content = index_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Template not found")

    def _check_rate_limit(self) -> bool:
        ip = self.client_address[0]
        allowed, retry_after = _rate_limiter.is_allowed(ip)
        if not allowed:
            body = json.dumps(
                {"error": "Rate limit exceeded. Try again later."}
            ).encode()
            self.send_response(429)
            self.send_header("Content-Type", "application/json")
            self.send_header("Retry-After", str(retry_after))
            self.end_headers()
            self.wfile.write(body)
            return False
        return True

    def _serve_weather_api(self) -> None:
        if not self._check_rate_limit():
            return
        location = get_location()
        if location is None:
            self._send_json(
                502,
                {
                    "error": "Could not determine your location. Please check your internet connection and try again."
                },
            )
            return

        weather = get_weather(location["lat"], location["lon"])
        if weather is None:
            self._send_json(
                502,
                {
                    "error": "Could not retrieve weather data. The weather service may be temporarily unavailable."
                },
            )
            return

        self._send_json(200, {"location": dict(location), "weather": dict(weather)})

    def _serve_cities_api(self) -> None:
        if not self._check_rate_limit():
            return
        location = get_location()
        cities = get_cities()
        detected: dict[str, object] | None = dict(location) if location else None
        self._send_json(
            200, {"cities": [dict(c) for c in cities], "detected": detected}
        )

    def _serve_forecast_api(self) -> None:
        if not self._check_rate_limit():
            return
        from urllib.parse import parse_qs, urlparse

        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        lat_values = params.get("lat")
        lon_values = params.get("lon")
        if not lat_values or not lon_values:
            self._send_json(400, {"error": "Missing required parameters: lat and lon"})
            return
        try:
            lat = float(lat_values[0])
            lon = float(lon_values[0])
        except ValueError:
            self._send_json(400, {"error": "lat and lon must be numeric"})
            return

        forecasts = get_forecast(lat, lon)
        if forecasts is None:
            self._send_json(502, {"error": "Could not retrieve forecast data."})
            return

        self._send_json(200, {"forecasts": [dict(f) for f in forecasts]})

    def _send_json(self, status: int, data: dict[str, object]) -> None:
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def _send_not_found(self) -> None:
        self.send_response(404)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Not Found")

    def log_message(self, format: str, *args: object) -> None:
        # Suppress default stderr logging during normal operation
        pass


def main() -> None:
    server = HTTPServer(("localhost", 8000), WeatherHandler)
    print("Weather server running at http://localhost:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
