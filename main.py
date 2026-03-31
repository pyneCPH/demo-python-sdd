import argparse
import sys

from weather import (
    format_forecast,
    format_weather,
    get_forecast,
    get_location,
    get_weather,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Display current weather for your location."
    )
    parser.add_argument(
        "-f",
        "--fahrenheit",
        action="store_true",
        help="display temperature in Fahrenheit instead of Celsius",
    )
    parser.add_argument(
        "--mph",
        action="store_true",
        help="display wind speed in mph instead of km/h",
    )
    parser.add_argument(
        "-F",
        "--forecast",
        action="store_true",
        help="display multi-day forecast instead of current weather",
    )
    args = parser.parse_args()

    location = get_location()
    if location is None:
        print("Could not determine your location.")
        print("Please check your internet connection and try again.")
        sys.exit(1)

    temp_unit = "F" if args.fahrenheit else "C"
    wind_unit = "mph" if args.mph else "kmh"

    if args.forecast:
        forecasts = get_forecast(location["lat"], location["lon"])
        if forecasts is None:
            print("Could not retrieve forecast data.")
            print(
                "The weather service may be temporarily unavailable. Please try again later."
            )
            sys.exit(1)
        print(
            format_forecast(
                location, forecasts, temp_unit=temp_unit, wind_unit=wind_unit
            )
        )
    else:
        weather = get_weather(location["lat"], location["lon"])
        if weather is None:
            print("Could not retrieve weather data.")
            print(
                "The weather service may be temporarily unavailable. Please try again later."
            )
            sys.exit(1)
        print(
            format_weather(location, weather, temp_unit=temp_unit, wind_unit=wind_unit)
        )


if __name__ == "__main__":
    main()
