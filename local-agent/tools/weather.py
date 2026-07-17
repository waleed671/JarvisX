from tools.base import Tool
from tools.http_client import get_json


class WeatherTool(Tool):
    name = "weather"
    description = "Get current weather for a city"

    def execute(self, parameters):
        location = parameters.get("location", "").strip()
        if not location:
            return {
                "success": False,
                "message": "Weather location is required.",
            }

        place = self._geocode(location)
        if not place:
            return {
                "success": False,
                "message": f"I could not find weather location: {location}.",
            }

        weather = self._current_weather(place)
        if not weather:
            return {
                "success": False,
                "message": f"I could not fetch live weather for {place['label']}.",
            }

        current = weather["current"]
        units = weather.get("current_units", {})
        description = _weather_description(current.get("weather_code"))
        temperature = _format_number(current.get("temperature_2m"))
        feels_like = _format_number(current.get("apparent_temperature"))
        humidity = _format_number(current.get("relative_humidity_2m"))
        wind = _format_number(current.get("wind_speed_10m"))

        answer = (
            f"{place['label']} weather now: {temperature} {_unit(units.get('temperature_2m'), 'C')}, "
            f"feels like {feels_like} {_unit(units.get('apparent_temperature'), 'C')}, "
            f"{description}, humidity {humidity}{units.get('relative_humidity_2m', '%')}, "
            f"wind {wind} {_unit(units.get('wind_speed_10m'), 'km/h')}."
        )

        return {
            "success": True,
            "message": answer,
            "data": {
                "answer": answer,
                "location": place,
                "weather": current,
            },
        }

    def _geocode(self, location: str):
        response = get_json(
            "https://geocoding-api.open-meteo.com/v1/search",
            {
                "name": location,
                "count": 1,
                "language": "en",
                "format": "json",
            },
        )
        if not response["ok"] or not isinstance(response["body"], dict):
            return None

        results = response["body"].get("results") or []
        if not results:
            return None

        result = results[0]
        parts = [
            result.get("name"),
            result.get("admin1"),
            result.get("country"),
        ]
        label = ", ".join(part for part in parts if part)
        return {
            "label": label,
            "latitude": result["latitude"],
            "longitude": result["longitude"],
        }

    def _current_weather(self, place: dict):
        response = get_json(
            "https://api.open-meteo.com/v1/forecast",
            {
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": ",".join(
                    [
                        "temperature_2m",
                        "relative_humidity_2m",
                        "apparent_temperature",
                        "precipitation",
                        "weather_code",
                        "wind_speed_10m",
                    ]
                ),
                "timezone": "auto",
            },
        )
        if not response["ok"] or not isinstance(response["body"], dict):
            return None
        return response["body"]


def _format_number(value):
    if value is None:
        return "unknown"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _unit(value, fallback):
    if not value:
        return fallback
    return str(value).replace("°", "").strip()


def _weather_description(code):
    descriptions = {
        0: "clear sky",
        1: "mainly clear",
        2: "partly cloudy",
        3: "overcast",
        45: "fog",
        48: "depositing rime fog",
        51: "light drizzle",
        53: "moderate drizzle",
        55: "dense drizzle",
        61: "slight rain",
        63: "moderate rain",
        65: "heavy rain",
        71: "slight snow",
        73: "moderate snow",
        75: "heavy snow",
        80: "slight rain showers",
        81: "moderate rain showers",
        82: "violent rain showers",
        95: "thunderstorm",
        96: "thunderstorm with slight hail",
        99: "thunderstorm with heavy hail",
    }
    return descriptions.get(code, "current conditions available")
