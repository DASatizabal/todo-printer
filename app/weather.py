"""
Weather fetcher for the morning briefing ticket.
Uses Open-Meteo API (free, no key needed).
Default location: Florida City, FL.
"""

import os
import httpx

# Florida City, FL coordinates (override with env vars)
LATITUDE = os.environ.get("WEATHER_LAT", "25.4480")
LONGITUDE = os.environ.get("WEATHER_LON", "-80.4788")
TIMEOUT = 10

# WMO weather codes to descriptions
WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Fog (rime)",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow",
    80: "Light showers", 81: "Showers", 82: "Heavy showers",
    85: "Light snow showers", 86: "Snow showers",
    95: "Thunderstorm", 96: "Thunderstorm + hail", 99: "Severe thunderstorm",
}


def fetch_weather() -> dict | None:
    """Fetch current weather and daily forecast for the configured location."""
    try:
        response = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": LATITUDE,
                "longitude": LONGITUDE,
                "current": "temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "forecast_days": "1",
                "timezone": "America/New_York",
            },
            timeout=TIMEOUT,
        )
        if response.status_code != 200:
            return None

        data = response.json()
        current = data.get("current", {})
        daily = data.get("daily", {})

        weather_code = current.get("weather_code", 0)

        return {
            "temp": round(current.get("temperature_2m", 0)),
            "condition": WMO_CODES.get(weather_code, f"Code {weather_code}"),
            "humidity": current.get("relative_humidity_2m", 0),
            "wind": round(current.get("wind_speed_10m", 0)),
            "high": round(daily.get("temperature_2m_max", [0])[0]),
            "low": round(daily.get("temperature_2m_min", [0])[0]),
            "rain_chance": daily.get("precipitation_probability_max", [0])[0],
        }
    except Exception:
        return None


def format_weather_lines(weather: dict) -> list[str]:
    """Format weather data for receipt printing."""
    if not weather:
        return ["Weather: unavailable"]

    lines = [
        f"Florida City, FL",
        f"{weather['condition']}, {weather['temp']}F",
        f"High {weather['high']}F / Low {weather['low']}F",
        f"Humidity {weather['humidity']}% | Wind {weather['wind']}mph",
    ]
    if weather["rain_chance"] > 0:
        lines.append(f"Rain chance: {weather['rain_chance']}%")
    return lines
