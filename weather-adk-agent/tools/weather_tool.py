from google.adk.tools import BaseTool
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

class WeatherTool(BaseTool):
    def __init__(self):
        # We must call the parent constructor with the name and description
        super().__init__(
            name="WeatherTool",
            description="Gets current weather information for a location"
        )
    
    # Using a dictionary for parameters as ToolParameter wasn't found in your tools dir
    parameters = {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city and country/state"
            }
        },
        "required": ["location"]
    }

    async def execute(self, location: str):
        """
        Retrieves the current weather for a given city.
        Args:
            location: The name of the city (e.g., 'London', 'Tokyo').
        """
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key:
            return {"error": "Weather API key not found in .env file"}
        # Use a real weather API (replace with your preferred provider)
        url = f"https://api.weatherapi.com/v1/current.json?key={api_key}&q={location}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    weather_data = {
                        "location": data["location"]["name"],
                        "region": data["location"]["region"],
                        "country": data["location"]["country"],
                        "temperature": f"{data['current']['temp_c']}°C / {data['current']['temp_f']}°F",
                        "condition": data["current"]["condition"]["text"],
                        "humidity": f"{data['current']['humidity']}%",
                        "wind": f"{data['current']['wind_mph']} mph {data['current']['wind_dir']}"
                    }
                    
                    return weather_data
                else:
                    return {"error": f"Failed to get weather data: {response.status}"}