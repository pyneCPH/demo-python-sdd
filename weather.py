import json
import urllib.request
from typing import TypedDict


class LocationData(TypedDict):
    city: str
    country: str
    lat: float
    lon: float


class WeatherData(TypedDict):
    temperature: float
    humidity: float
    wind_speed: float
    condition: str
    emoji: str
    sunrise: str
    sunset: str


class DailyForecast(TypedDict):
    date: str
    temperature_max: float
    temperature_min: float
    humidity: float
    wind_speed: float
    condition: str
    emoji: str


WEATHER_CODES: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


WEATHER_EMOJIS: dict[int, str] = {
    0: "\u2600\ufe0f",  # Clear sky
    1: "\U0001f324\ufe0f",  # Mainly clear
    2: "\u26c5",  # Partly cloudy
    3: "\u2601\ufe0f",  # Overcast
    45: "\U0001f32b\ufe0f",  # Foggy
    48: "\U0001f32b\ufe0f",  # Depositing rime fog
    51: "\U0001f326\ufe0f",  # Light drizzle
    53: "\U0001f326\ufe0f",  # Moderate drizzle
    55: "\U0001f326\ufe0f",  # Dense drizzle
    61: "\U0001f327\ufe0f",  # Slight rain
    63: "\U0001f327\ufe0f",  # Moderate rain
    65: "\U0001f327\ufe0f",  # Heavy rain
    66: "\U0001f9ca",  # Light freezing rain
    67: "\U0001f9ca",  # Heavy freezing rain
    71: "\u2744\ufe0f",  # Slight snowfall
    73: "\u2744\ufe0f",  # Moderate snowfall
    75: "\u2744\ufe0f",  # Heavy snowfall
    77: "\u2744\ufe0f",  # Snow grains
    80: "\U0001f327\ufe0f",  # Slight rain showers
    81: "\U0001f327\ufe0f",  # Moderate rain showers
    82: "\U0001f327\ufe0f",  # Violent rain showers
    85: "\U0001f328\ufe0f",  # Slight snow showers
    86: "\U0001f328\ufe0f",  # Heavy snow showers
    95: "\u26c8\ufe0f",  # Thunderstorm
    96: "\u26c8\ufe0f",  # Thunderstorm with slight hail
    99: "\u26c8\ufe0f",  # Thunderstorm with heavy hail
}


CITIES: list[LocationData] = [
    LocationData(city="London", country="United Kingdom", lat=51.51, lon=-0.13),
    LocationData(city="New York", country="United States", lat=40.71, lon=-74.01),
    LocationData(city="Tokyo", country="Japan", lat=35.68, lon=139.69),
    LocationData(city="Sydney", country="Australia", lat=-33.87, lon=151.21),
    LocationData(city="Paris", country="France", lat=48.86, lon=2.35),
    LocationData(city="São Paulo", country="Brazil", lat=-23.55, lon=-46.63),
    LocationData(city="Dubai", country="United Arab Emirates", lat=25.20, lon=55.27),
    LocationData(city="Copenhagen", country="Denmark", lat=55.67, lon=12.56),
]


def get_cities() -> list[LocationData]:
    return list(CITIES)


def celsius_to_fahrenheit(celsius: float) -> float:
    return round(celsius * 9 / 5 + 32, 1)


def kmh_to_mph(kmh: float) -> float:
    return round(kmh * 0.621371, 1)


def describe_weather(code: int) -> str:
    return WEATHER_CODES.get(code, "Unknown")


def weather_emoji(code: int) -> str:
    return WEATHER_EMOJIS.get(code, "\U0001f321\ufe0f")


def get_location() -> LocationData | None:
    try:
        req = urllib.request.Request("http://ip-api.com/json/")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
        if data.get("status") != "success":
            return None
        return LocationData(
            city=data["city"],
            country=data["country"],
            lat=data["lat"],
            lon=data["lon"],
        )
    except Exception:
        return None


def _extract_time(iso_datetime: str) -> str:
    """Extract the HH:MM time portion from an ISO 8601 datetime string."""
    if "T" in iso_datetime:
        return iso_datetime.split("T")[1][:5]
    return iso_datetime


def get_weather(lat: float, lon: float) -> WeatherData | None:
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"
            f"&daily=sunrise,sunset"
            f"&wind_speed_unit=kmh&forecast_days=1"
        )
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
        current = data["current"]
        daily = data["daily"]
        code = current["weather_code"]
        return WeatherData(
            temperature=current["temperature_2m"],
            humidity=current["relative_humidity_2m"],
            wind_speed=current["wind_speed_10m"],
            condition=describe_weather(code),
            emoji=weather_emoji(code),
            sunrise=_extract_time(daily["sunrise"][0]),
            sunset=_extract_time(daily["sunset"][0]),
        )
    except Exception:
        return None


def get_forecast(lat: float, lon: float) -> list[DailyForecast] | None:
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&daily=temperature_2m_max,temperature_2m_min"
            f",relative_humidity_2m_mean,wind_speed_10m_max,weather_code"
            f"&wind_speed_unit=kmh&forecast_days=4"
        )
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
        daily = data["daily"]
        forecasts: list[DailyForecast] = []
        for i in range(len(daily["time"])):
            code = daily["weather_code"][i]
            forecasts.append(
                DailyForecast(
                    date=daily["time"][i],
                    temperature_max=daily["temperature_2m_max"][i],
                    temperature_min=daily["temperature_2m_min"][i],
                    humidity=daily["relative_humidity_2m_mean"][i],
                    wind_speed=daily["wind_speed_10m_max"][i],
                    condition=describe_weather(code),
                    emoji=weather_emoji(code),
                )
            )
        return forecasts
    except Exception:
        return None


def format_weather(
    location: LocationData,
    weather: WeatherData,
    temp_unit: str = "C",
    wind_unit: str = "kmh",
) -> str:
    temp = weather["temperature"]
    temp_label = "\u00b0C"
    if temp_unit == "F":
        temp = celsius_to_fahrenheit(temp)
        temp_label = "\u00b0F"

    wind = weather["wind_speed"]
    wind_label = "km/h"
    if wind_unit == "mph":
        wind = kmh_to_mph(wind)
        wind_label = "mph"

    return (
        f"Weather for {location['city']}, {location['country']}\n"
        f"\n"
        f"  Temperature:  {temp}{temp_label}\n"
        f"  Condition:    {weather['emoji']} {weather['condition']}\n"
        f"  Humidity:     {weather['humidity']}%\n"
        f"  Wind Speed:   {wind} {wind_label}\n"
        f"  Sunrise:      {weather['sunrise']}\n"
        f"  Sunset:       {weather['sunset']}"
    )
