import json
from http.client import HTTPConnection
from threading import Thread
from http.server import HTTPServer
from unittest.mock import patch

from server import WeatherHandler
from weather import CityDashboardData, DailyForecast, LocationData, WeatherData


def _make_server() -> HTTPServer:
    server = HTTPServer(("localhost", 0), WeatherHandler)
    return server


def _request(
    server: HTTPServer, method: str, path: str
) -> tuple[int, dict[str, str], bytes]:
    host, port = server.server_address
    conn = HTTPConnection(str(host), port)
    conn.request(method, path)
    response = conn.getresponse()
    status = response.status
    headers = {k.lower(): v for k, v in response.getheaders()}
    body = response.read()
    conn.close()
    return status, headers, body


MOCK_LOCATION = LocationData(city="Copenhagen", country="Denmark", lat=55.67, lon=12.56)
MOCK_WEATHER = WeatherData(
    temperature=12.5,
    humidity=72.0,
    wind_speed=15.3,
    surface_pressure=1013.5,
    precipitation=0.2,
    condition="Partly cloudy",
    emoji="\u26c5",
)


@patch("server.get_weather", return_value=MOCK_WEATHER)
@patch("server.get_location", return_value=MOCK_LOCATION)
def test_api_weather_success(mock_loc: object, mock_weather: object) -> None:
    server = _make_server()
    thread = Thread(target=server.handle_request)
    thread.start()

    status, headers, body = _request(server, "GET", "/api/weather")
    thread.join()
    server.server_close()

    assert status == 200
    assert "application/json" in headers["content-type"]
    data = json.loads(body)
    assert data["location"]["city"] == "Copenhagen"
    assert data["weather"]["temperature"] == 12.5
    assert data["weather"]["emoji"] == "\u26c5"


@patch("server.get_location", return_value=None)
def test_api_weather_location_failure(mock_loc: object) -> None:
    server = _make_server()
    thread = Thread(target=server.handle_request)
    thread.start()

    status, headers, body = _request(server, "GET", "/api/weather")
    thread.join()
    server.server_close()

    assert status == 502
    data = json.loads(body)
    assert "location" in data["error"].lower()


@patch("server.get_weather", return_value=None)
@patch("server.get_location", return_value=MOCK_LOCATION)
def test_api_weather_weather_failure(mock_loc: object, mock_weather: object) -> None:
    server = _make_server()
    thread = Thread(target=server.handle_request)
    thread.start()

    status, headers, body = _request(server, "GET", "/api/weather")
    thread.join()
    server.server_close()

    assert status == 502
    data = json.loads(body)
    assert "weather" in data["error"].lower()


def test_serve_index_html() -> None:
    server = _make_server()
    thread = Thread(target=server.handle_request)
    thread.start()

    status, headers, body = _request(server, "GET", "/")
    thread.join()
    server.server_close()

    assert status == 200
    assert "text/html" in headers["content-type"]
    assert b"Weather" in body


def test_404_for_unknown_path() -> None:
    server = _make_server()
    thread = Thread(target=server.handle_request)
    thread.start()

    status, headers, body = _request(server, "GET", "/unknown")
    thread.join()
    server.server_close()

    assert status == 404


MOCK_CITIES = [
    LocationData(city="London", country="United Kingdom", lat=51.51, lon=-0.13),
    LocationData(city="Tokyo", country="Japan", lat=35.68, lon=139.69),
]

MOCK_FORECASTS = [
    DailyForecast(
        date="2026-02-28",
        temperature_max=8.2,
        temperature_min=3.1,
        humidity=75.0,
        wind_speed=12.5,
        surface_pressure=1013.5,
        precipitation_sum=0.0,
        condition="Partly cloudy",
        emoji="\u26c5",
    ),
    DailyForecast(
        date="2026-03-01",
        temperature_max=10.1,
        temperature_min=4.2,
        humidity=68.0,
        wind_speed=8.3,
        surface_pressure=1010.2,
        precipitation_sum=1.2,
        condition="Overcast",
        emoji="\u2601\ufe0f",
    ),
    DailyForecast(
        date="2026-03-02",
        temperature_max=7.5,
        temperature_min=2.8,
        humidity=80.0,
        wind_speed=15.7,
        surface_pressure=1008.7,
        precipitation_sum=5.4,
        condition="Slight rain",
        emoji="\U0001f327\ufe0f",
    ),
    DailyForecast(
        date="2026-03-03",
        temperature_max=9.3,
        temperature_min=3.9,
        humidity=72.0,
        wind_speed=10.1,
        surface_pressure=1015.3,
        precipitation_sum=0.0,
        condition="Mainly clear",
        emoji="\U0001f324\ufe0f",
    ),
]


@patch("server.get_cities", return_value=MOCK_CITIES)
@patch("server.get_location", return_value=MOCK_LOCATION)
def test_api_cities_success(mock_loc: object, mock_cities: object) -> None:
    server = _make_server()
    thread = Thread(target=server.handle_request)
    thread.start()

    status, headers, body = _request(server, "GET", "/api/cities")
    thread.join()
    server.server_close()

    assert status == 200
    assert "application/json" in headers["content-type"]
    data = json.loads(body)
    assert len(data["cities"]) == 2
    assert data["detected"]["city"] == "Copenhagen"


@patch("server.get_cities", return_value=MOCK_CITIES)
@patch("server.get_location", return_value=None)
def test_api_cities_no_detection(mock_loc: object, mock_cities: object) -> None:
    server = _make_server()
    thread = Thread(target=server.handle_request)
    thread.start()

    status, headers, body = _request(server, "GET", "/api/cities")
    thread.join()
    server.server_close()

    assert status == 200
    data = json.loads(body)
    assert data["detected"] is None
    assert len(data["cities"]) == 2


@patch("server.get_forecast", return_value=MOCK_FORECASTS)
def test_api_forecast_success(mock_forecast: object) -> None:
    server = _make_server()
    thread = Thread(target=server.handle_request)
    thread.start()

    status, headers, body = _request(server, "GET", "/api/forecast?lat=55.67&lon=12.56")
    thread.join()
    server.server_close()

    assert status == 200
    assert "application/json" in headers["content-type"]
    data = json.loads(body)
    assert len(data["forecasts"]) == 4
    assert data["forecasts"][0]["date"] == "2026-02-28"
    assert data["forecasts"][0]["emoji"] == "\u26c5"


def test_api_forecast_missing_params() -> None:
    server = _make_server()
    thread = Thread(target=server.handle_request)
    thread.start()

    status, headers, body = _request(server, "GET", "/api/forecast")
    thread.join()
    server.server_close()

    assert status == 400
    data = json.loads(body)
    assert "error" in data


@patch("server.get_forecast", return_value=None)
def test_api_forecast_service_failure(mock_forecast: object) -> None:
    server = _make_server()
    thread = Thread(target=server.handle_request)
    thread.start()

    status, headers, body = _request(server, "GET", "/api/forecast?lat=55.67&lon=12.56")
    thread.join()
    server.server_close()

    assert status == 502
    data = json.loads(body)
    assert "error" in data


MOCK_DASHBOARD_CITY = CityDashboardData(
    current=MOCK_WEATHER,
    history=MOCK_FORECASTS[:3],
    forecast=MOCK_FORECASTS[1:4],
)


@patch("server.get_dashboard_data", return_value=MOCK_DASHBOARD_CITY)
def test_api_dashboard_success(mock_dash: object) -> None:
    server = _make_server()
    thread = Thread(target=server.handle_request)
    thread.start()

    status, headers, body = _request(server, "GET", "/api/dashboard")
    thread.join()
    server.server_close()

    assert status == 200
    assert "application/json" in headers["content-type"]
    data = json.loads(body)
    assert "cities" in data
    assert len(data["cities"]) == 8
    # All cities should have current data since mock returns valid data
    for entry in data["cities"]:
        assert "city" in entry
        assert "current" in entry
        assert "history" in entry
        assert "forecast" in entry


def test_api_dashboard_partial_failure() -> None:
    # First city returns None, rest return valid data
    call_count = 0

    def side_effect(lat: float, lon: float) -> CityDashboardData | None:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return None
        return MOCK_DASHBOARD_CITY

    with patch("server.get_dashboard_data", side_effect=side_effect):
        server = _make_server()
        thread = Thread(target=server.handle_request)
        thread.start()

        status, headers, body = _request(server, "GET", "/api/dashboard")
        thread.join()
        server.server_close()

    assert status == 200
    data = json.loads(body)
    assert len(data["cities"]) == 8
    # First city should have null current and empty arrays
    assert data["cities"][0]["current"] is None
    assert data["cities"][0]["history"] == []
    assert data["cities"][0]["forecast"] == []
    # Other cities should have data
    assert data["cities"][1]["current"] is not None
