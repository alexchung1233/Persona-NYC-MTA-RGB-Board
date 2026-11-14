import time

import requests

# Open-Meteo: free, open-source, no API key. https://open-meteo.com
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"

# Sunnyside, Queens (40 St-Lowery St station)
LATITUDE = 40.7437
LONGITUDE = -73.9240

CACHE_SECONDS = 10 * 60  # Open-Meteo updates current conditions every 15 min
RETRY_SECONDS = 60  # wait this long after a failed fetch before trying again

_cache = {"data": None, "fetched_at": 0.0, "failed_at": None}


def _condition(weather_code):
    """Map a WMO weather code to one of: sunny, cloudy, rainy, snow."""
    if weather_code in (0, 1):
        return "sunny"
    if 71 <= weather_code <= 77 or weather_code in (85, 86):
        return "snow"
    if 51 <= weather_code <= 67 or 80 <= weather_code <= 82 or weather_code >= 95:
        return "rainy"
    return "cloudy"  # 2-3 partly cloudy/overcast, 45/48 fog


def get_weather():
    """Return {"current", "high", "low", "condition"} in whole degrees F.

    Results are cached for CACHE_SECONDS. On a failed fetch, the last good
    reading is returned (or None if there has never been one).
    """
    if _cache["data"] is not None and time.monotonic() - _cache["fetched_at"] < CACHE_SECONDS:
        return _cache["data"]
    if _cache["failed_at"] is not None and time.monotonic() - _cache["failed_at"] < RETRY_SECONDS:
        return _cache["data"]

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min",
        "temperature_unit": "fahrenheit",
        "timezone": "America/New_York",
        "forecast_days": 1,
    }

    try:
        response = requests.get(WEATHER_API_URL, params=params, timeout=10)
        response.raise_for_status()
        body = response.json()
        data = {
            "current": round(body["current"]["temperature_2m"]),
            "high": round(body["daily"]["temperature_2m_max"][0]),
            "low": round(body["daily"]["temperature_2m_min"][0]),
            "condition": _condition(body["current"]["weather_code"]),
        }
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as e:
        print(f"weather fetch failed: {e}")
        _cache["failed_at"] = time.monotonic()
        return _cache["data"]

    _cache["data"] = data
    _cache["fetched_at"] = time.monotonic()
    _cache["failed_at"] = None
    return data
