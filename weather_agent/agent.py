from dotenv import load_dotenv
import requests
from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

load_dotenv()


def get_weather(city: str) -> dict:
    """Get current weather for a city using Open-Meteo API.

    Args:
        city: The name of the city to get weather for.

    Returns:
        A dictionary with weather data or an error message.
    """
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {"name": city, "count": 1, "language": "en"}

    try:
        geo_response = requests.get(geocoding_url, params=geo_params, timeout=10)
        geo_data = geo_response.json()

        if "results" not in geo_data or len(geo_data["results"]) == 0:
            return {"status": "error", "error_message": f"City '{city}' not found."}

        location = geo_data["results"][0]
        latitude = location["latitude"]
        longitude = location["longitude"]
        city_name = location["name"]
        country = location.get("country", "Unknown")

        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,wind_speed_10m,relative_humidity_2m,weather_code",
            "timezone": "auto",
        }

        weather_response = requests.get(weather_url, params=weather_params, timeout=10)
        weather_data = weather_response.json()
        current = weather_data["current"]

        return {
            "status": "success",
            "report": {
                "city": city_name,
                "country": country,
                "temperature_celsius": current["temperature_2m"],
                "wind_speed_kmh": current["wind_speed_10m"],
                "humidity_percent": current["relative_humidity_2m"],
                "weather_code": current["weather_code"],
            },
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}

weather_agent = Agent(
    model="gemini-2.5-flash",
    name="weather_agent",
    description="An agent that provides current weather information for any city worldwide.",
    instruction="""You are a weather assistant. When a user asks about the weather
    in a city, use the get_weather tool to fetch real-time weather data.
    Present the results clearly with temperature, wind speed, and humidity.
    If the city is not found, let the user know politely.""",
    tools=[get_weather],
)

a2a_app = to_a2a(weather_agent, port=8001)
