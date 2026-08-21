import urllib.request
import json

# Coordinates for Gulf Breeze
LATITUDE = 30.3571
LONGITUDE = -87.1639
USER_AGENT = "Homebase (kanoasawada@gmail.com)"


def _fetch_json(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    })
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read())


def _get_forecast_urls():
    points = _fetch_json(f"https://api.weather.gov/points/{LATITUDE},{LONGITUDE}")
    props = points['properties']
    return props['forecast'], props['forecastHourly']


def _to_celsius(fahrenheit):
    return round((fahrenheit - 32) * 5 / 9)


def _shorten(text, max_length=42):
    if len(text) <= max_length:
        return text
    truncated = text[:max_length].rsplit(' ', 1)[0]
    return truncated + '...'


def _simplify_wind(wind_speed):
    # Daily periods sometimes give a range like "5 to 10 mph" - collapse
    # to just the higher number so it's no longer than the hourly format.
    if ' to ' in wind_speed:
        return wind_speed.split(' to ')[-1]
    return wind_speed


import os


CACHE_PATH = os.path.join(os.path.dirname(__file__), '..', 'cache', 'weather.json')


def _save_cache(data):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, 'w') as f:
        json.dump(data, f)


def _load_cache():
    try:
        with open(CACHE_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _fetch_weather():
    daily_url, hourly_url = _get_forecast_urls()

    daily_periods = _fetch_json(daily_url)['properties']['periods']
    hourly_periods = _fetch_json(hourly_url)['properties']['periods']

    now = hourly_periods[0]
    today = daily_periods[0]
    tonight = daily_periods[1] if len(daily_periods) > 1 else None
    tomorrow_day = daily_periods[2] if len(daily_periods) > 2 else None
    tomorrow_night = daily_periods[3] if len(daily_periods) > 3 else None

    result = {
        'temp': now['temperature'],
        'temp_c': _to_celsius(now['temperature']),
        'condition': _shorten(now['shortForecast']),
        'humidity': now['relativeHumidity']['value'],
        'rain_chance': (now.get('probabilityOfPrecipitation') or {}).get('value') or 0,
        'wind': f"{now['windSpeed']} {now['windDirection']}",
        'high': today['temperature'],
        'low': tonight['temperature'] if tonight else None,
    }

    if tomorrow_day:
        humidity = (tomorrow_day.get('relativeHumidity') or {}).get('value')
        result['tomorrow'] = {
            'high': tomorrow_day['temperature'],
            'low': tomorrow_night['temperature'] if tomorrow_night else None,
            'condition': _shorten(tomorrow_day['shortForecast']),
            'rain_chance': (tomorrow_day.get('probabilityOfPrecipitation') or {}).get('value') or 0,
            'humidity': humidity,
            'wind': f"{_simplify_wind(tomorrow_day['windSpeed'])} {tomorrow_day['windDirection']}",
        }

    return result


def get_weather():
    try:
        data = _fetch_weather()
    except Exception:
        cached = _load_cache()
        if cached is None:
            raise
        cached['from_cache'] = True
        return cached

    data['from_cache'] = False
    _save_cache(data)
    return data