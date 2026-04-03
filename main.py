import argparse
import sys

from quote import format_quote_box, get_daily_quote
from weather import format_weather, get_location, get_weather


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
        "--no-quote",
        action="store_true",
        help="disable the daily motivational quote",
    )
    args = parser.parse_args()

    if not args.no_quote:
        quote = get_daily_quote()
        if quote is not None:
            print(format_quote_box(quote))
            print()

    location = get_location()
    if location is None:
        print("Could not determine your location.")
        print("Please check your internet connection and try again.")
        sys.exit(1)

    weather = get_weather(location["lat"], location["lon"])
    if weather is None:
        print("Could not retrieve weather data.")
        print(
            "The weather service may be temporarily unavailable. Please try again later."
        )
        sys.exit(1)

    temp_unit = "F" if args.fahrenheit else "C"
    wind_unit = "mph" if args.mph else "kmh"
    print(format_weather(location, weather, temp_unit=temp_unit, wind_unit=wind_unit))


if __name__ == "__main__":
    main()
