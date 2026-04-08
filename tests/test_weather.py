import json
from io import BytesIO
from unittest.mock import patch

from weather import (
    CITIES,
    LocationData,
    WeatherData,
    celsius_to_fahrenheit,
    describe_weather,
    format_weather,
    get_cities,
    get_dashboard_data,
    get_forecast,
    get_location,
    get_weather,
    kmh_to_mph,
    weather_emoji,
)


class MockResponse:
    def __init__(self, data: bytes) -> None:
        self._data = BytesIO(data)

    def read(self) -> bytes:
        return self._data.read()

    def __enter__(self) -> "MockResponse":
        return self

    def __exit__(self, *args: object) -> None:
        pass


def test_describe_weather_known_code() -> None:
    assert describe_weather(0) == "Clear sky"
    assert describe_weather(95) == "Thunderstorm"
    assert describe_weather(65) == "Heavy rain"


def test_describe_weather_unknown_code() -> None:
    assert describe_weather(999) == "Unknown"
    assert describe_weather(-1) == "Unknown"


def test_weather_emoji_known_code() -> None:
    assert weather_emoji(0) == "\u2600\ufe0f"
    assert weather_emoji(95) == "\u26c8\ufe0f"
    assert weather_emoji(65) == "\U0001f327\ufe0f"
    assert weather_emoji(2) == "\u26c5"
    assert weather_emoji(71) == "\u2744\ufe0f"


def test_weather_emoji_unknown_code() -> None:
    assert weather_emoji(999) == "\U0001f321\ufe0f"
    assert weather_emoji(-1) == "\U0001f321\ufe0f"


@patch("weather.urllib.request.urlopen")
def test_get_location_success(mock_urlopen: object) -> None:
    response_data = json.dumps(
        {
            "status": "success",
            "city": "Copenhagen",
            "country": "Denmark",
            "lat": 55.67,
            "lon": 12.56,
        }
    ).encode()
    mock_urlopen.return_value = MockResponse(response_data)  # type: ignore[attr-defined]

    result = get_location()

    assert result is not None
    assert result["city"] == "Copenhagen"
    assert result["country"] == "Denmark"
    assert result["lat"] == 55.67
    assert result["lon"] == 12.56


@patch("weather.urllib.request.urlopen")
def test_get_location_failure(mock_urlopen: object) -> None:
    response_data = json.dumps({"status": "fail"}).encode()
    mock_urlopen.return_value = MockResponse(response_data)  # type: ignore[attr-defined]

    result = get_location()
    assert result is None


@patch("weather.urllib.request.urlopen")
def test_get_location_network_error(mock_urlopen: object) -> None:
    mock_urlopen.side_effect = OSError("Network unreachable")  # type: ignore[attr-defined]

    result = get_location()
    assert result is None


@patch("weather.urllib.request.urlopen")
def test_get_weather_success(mock_urlopen: object) -> None:
    response_data = json.dumps(
        {
            "current": {
                "temperature_2m": 12.5,
                "relative_humidity_2m": 72.0,
                "wind_speed_10m": 15.3,
                "surface_pressure": 1013.5,
                "precipitation": 0.2,
                "weather_code": 2,
            }
        }
    ).encode()
    mock_urlopen.return_value = MockResponse(response_data)  # type: ignore[attr-defined]

    result = get_weather(55.67, 12.56)

    assert result is not None
    assert result["temperature"] == 12.5
    assert result["humidity"] == 72.0
    assert result["wind_speed"] == 15.3
    assert result["surface_pressure"] == 1013.5
    assert result["precipitation"] == 0.2
    assert result["condition"] == "Partly cloudy"
    assert result["emoji"] == "\u26c5"


@patch("weather.urllib.request.urlopen")
def test_get_weather_failure(mock_urlopen: object) -> None:
    mock_urlopen.side_effect = OSError("Connection refused")  # type: ignore[attr-defined]

    result = get_weather(55.67, 12.56)
    assert result is None


def test_format_weather() -> None:
    location = LocationData(city="Copenhagen", country="Denmark", lat=55.67, lon=12.56)
    weather = WeatherData(
        temperature=12.5,
        humidity=72.0,
        wind_speed=15.3,
        surface_pressure=1013.5,
        precipitation=0.2,
        condition="Partly cloudy",
        emoji="\u26c5",
    )

    result = format_weather(location, weather)

    assert "Copenhagen" in result
    assert "Denmark" in result
    assert "12.5" in result
    assert "Partly cloudy" in result
    assert "72.0" in result
    assert "15.3" in result
    assert "\u26c5" in result


def test_get_cities_returns_all() -> None:
    cities = get_cities()
    assert len(cities) == 8
    city_names = [c["city"] for c in cities]
    assert "London" in city_names
    assert "Paris" in city_names
    assert "Berlin" in city_names
    assert "Amsterdam" in city_names
    assert "Madrid" in city_names
    assert "Rome" in city_names
    assert "Warsaw" in city_names
    assert "Stockholm" in city_names
    for city in cities:
        assert "city" in city
        assert "country" in city
        assert "lat" in city
        assert "lon" in city


def test_get_cities_returns_copy() -> None:
    cities = get_cities()
    cities.pop()
    assert len(get_cities()) == 8
    assert len(CITIES) == 8


@patch("weather.urllib.request.urlopen")
def test_get_forecast_success(mock_urlopen: object) -> None:
    response_data = json.dumps(
        {
            "daily": {
                "time": ["2026-02-28", "2026-03-01", "2026-03-02", "2026-03-03"],
                "temperature_2m_max": [8.2, 10.1, 7.5, 9.3],
                "temperature_2m_min": [3.1, 4.2, 2.8, 3.9],
                "relative_humidity_2m_mean": [75.0, 68.0, 80.0, 72.0],
                "wind_speed_10m_max": [12.5, 8.3, 15.7, 10.1],
                "surface_pressure_mean": [1013.5, 1010.2, 1008.7, 1015.3],
                "precipitation_sum": [0.0, 1.2, 5.4, 0.0],
                "weather_code": [2, 3, 61, 1],
            }
        }
    ).encode()
    mock_urlopen.return_value = MockResponse(response_data)  # type: ignore[attr-defined]

    result = get_forecast(55.67, 12.56)

    assert result is not None
    assert len(result) == 4
    assert result[0]["date"] == "2026-02-28"
    assert result[0]["temperature_max"] == 8.2
    assert result[0]["temperature_min"] == 3.1
    assert result[0]["humidity"] == 75.0
    assert result[0]["wind_speed"] == 12.5
    assert result[0]["surface_pressure"] == 1013.5
    assert result[0]["precipitation_sum"] == 0.0
    assert result[0]["condition"] == "Partly cloudy"
    assert result[0]["emoji"] == "\u26c5"
    assert result[2]["condition"] == "Slight rain"
    assert result[2]["emoji"] == "\U0001f327\ufe0f"
    assert result[3]["condition"] == "Mainly clear"
    assert result[3]["emoji"] == "\U0001f324\ufe0f"


@patch("weather.urllib.request.urlopen")
def test_get_forecast_network_error(mock_urlopen: object) -> None:
    mock_urlopen.side_effect = OSError("Network unreachable")  # type: ignore[attr-defined]

    result = get_forecast(55.67, 12.56)
    assert result is None


@patch("weather.urllib.request.urlopen")
def test_get_forecast_invalid_response(mock_urlopen: object) -> None:
    mock_urlopen.return_value = MockResponse(b"not json")  # type: ignore[attr-defined]

    result = get_forecast(55.67, 12.56)
    assert result is None


def test_celsius_to_fahrenheit() -> None:
    assert celsius_to_fahrenheit(0) == 32.0
    assert celsius_to_fahrenheit(100) == 212.0
    assert celsius_to_fahrenheit(25) == 77.0
    assert celsius_to_fahrenheit(-40) == -40.0


def test_kmh_to_mph() -> None:
    assert kmh_to_mph(100) == 62.1
    assert kmh_to_mph(0) == 0.0
    assert kmh_to_mph(10) == 6.2


def test_format_weather_fahrenheit() -> None:
    location = LocationData(city="Copenhagen", country="Denmark", lat=55.67, lon=12.56)
    weather = WeatherData(
        temperature=12.5,
        humidity=72.0,
        wind_speed=15.3,
        surface_pressure=1013.5,
        precipitation=0.2,
        condition="Partly cloudy",
        emoji="\u26c5",
    )

    result = format_weather(location, weather, temp_unit="F")

    assert "\u00b0F" in result
    assert "54.5" in result  # 12.5°C = 54.5°F
    assert "15.3" in result  # wind unchanged
    assert "km/h" in result


def test_format_weather_mph() -> None:
    location = LocationData(city="Copenhagen", country="Denmark", lat=55.67, lon=12.56)
    weather = WeatherData(
        temperature=12.5,
        humidity=72.0,
        wind_speed=15.3,
        surface_pressure=1013.5,
        precipitation=0.2,
        condition="Partly cloudy",
        emoji="\u26c5",
    )

    result = format_weather(location, weather, wind_unit="mph")

    assert "mph" in result
    assert "9.5" in result  # 15.3 km/h = 9.5 mph
    assert "12.5" in result  # temp unchanged
    assert "\u00b0C" in result


def test_format_weather_defaults_unchanged() -> None:
    location = LocationData(city="Copenhagen", country="Denmark", lat=55.67, lon=12.56)
    weather = WeatherData(
        temperature=12.5,
        humidity=72.0,
        wind_speed=15.3,
        surface_pressure=1013.5,
        precipitation=0.2,
        condition="Partly cloudy",
        emoji="\u26c5",
    )

    result = format_weather(location, weather)

    assert "\u00b0C" in result
    assert "km/h" in result
    assert "12.5" in result
    assert "15.3" in result


def _make_dashboard_response() -> bytes:
    return json.dumps(
        {
            "current": {
                "temperature_2m": 14.0,
                "relative_humidity_2m": 65.0,
                "wind_speed_10m": 20.0,
                "surface_pressure": 1012.0,
                "precipitation": 0.0,
                "weather_code": 1,
            },
            "daily": {
                "time": [
                    "2026-04-05",
                    "2026-04-06",
                    "2026-04-07",  # history (0-2)
                    "2026-04-08",  # today (3)
                    "2026-04-09",
                    "2026-04-10",
                    "2026-04-11",  # forecast (4-6)
                ],
                "temperature_2m_max": [10.0, 11.0, 12.0, 14.0, 15.0, 13.0, 12.5],
                "temperature_2m_min": [5.0, 6.0, 7.0, 8.0, 9.0, 7.0, 6.5],
                "relative_humidity_2m_mean": [70.0, 72.0, 68.0, 65.0, 60.0, 67.0, 71.0],
                "wind_speed_10m_max": [15.0, 18.0, 12.0, 20.0, 22.0, 17.0, 14.0],
                "surface_pressure_mean": [
                    1010.0,
                    1011.0,
                    1012.0,
                    1012.0,
                    1013.0,
                    1014.0,
                    1011.0,
                ],
                "precipitation_sum": [2.0, 0.5, 0.0, 0.0, 1.0, 3.0, 0.2],
                "weather_code": [61, 2, 1, 1, 63, 61, 2],
            },
        }
    ).encode()


@patch("weather.urllib.request.urlopen")
def test_get_dashboard_data_success(mock_urlopen: object) -> None:
    mock_urlopen.return_value = MockResponse(_make_dashboard_response())  # type: ignore[attr-defined]

    result = get_dashboard_data(51.51, -0.13)

    assert result is not None
    assert result["current"] is not None
    assert result["current"]["temperature"] == 14.0
    assert result["current"]["surface_pressure"] == 1012.0
    assert result["current"]["precipitation"] == 0.0

    assert len(result["history"]) == 3
    assert result["history"][0]["date"] == "2026-04-05"
    assert result["history"][2]["date"] == "2026-04-07"
    assert result["history"][0]["temperature_max"] == 10.0
    assert result["history"][0]["surface_pressure"] == 1010.0
    assert result["history"][0]["precipitation_sum"] == 2.0

    assert len(result["forecast"]) == 3
    assert result["forecast"][0]["date"] == "2026-04-09"
    assert result["forecast"][2]["date"] == "2026-04-11"
    assert result["forecast"][0]["temperature_max"] == 15.0


@patch("weather.urllib.request.urlopen")
def test_get_dashboard_data_network_error(mock_urlopen: object) -> None:
    mock_urlopen.side_effect = OSError("Network unreachable")  # type: ignore[attr-defined]

    result = get_dashboard_data(51.51, -0.13)
    assert result is None


@patch("weather.urllib.request.urlopen")
def test_get_dashboard_data_invalid_response(mock_urlopen: object) -> None:
    mock_urlopen.return_value = MockResponse(b"not json")  # type: ignore[attr-defined]

    result = get_dashboard_data(51.51, -0.13)
    assert result is None
