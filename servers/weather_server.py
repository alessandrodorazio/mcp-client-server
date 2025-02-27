from mcp.server.fastmcp import FastMCP

# Create a FastMCP server instance
mcp = FastMCP("Weather Service")

@mcp.tool()
async def get_weather(location: str, unit: str = "celsius") -> str:
    """Get the current weather for a location.
    
    Args:
        location: City name or location
        unit: Temperature unit (celsius or fahrenheit)
    
    Returns:
        Weather information as a string
    """
    # In a real implementation, this would call a weather API
    # This is a mock implementation for demonstration
    weather_data = {
        "new york": {"temp": 22, "condition": "Sunny", "humidity": 60},
        "london": {"temp": 18, "condition": "Cloudy", "humidity": 75},
        "tokyo": {"temp": 28, "condition": "Rainy", "humidity": 80},
        "sydney": {"temp": 25, "condition": "Clear", "humidity": 65},
    }
    
    location = location.lower()
    if location not in weather_data:
        return f"Weather data for {location} not available."
    
    data = weather_data[location]
    temp = data["temp"]
    if unit.lower() == "fahrenheit":
        temp = (temp * 9/5) + 32
    
    return f"Weather in {location.title()}: {data['condition']}, {temp}°{'F' if unit == 'fahrenheit' else 'C'}, Humidity: {data['humidity']}%"

@mcp.tool()
async def get_forecast(location: str, days: int = 3) -> str:
    """Get a weather forecast for the next few days.
    
    Args:
        location: City name or location
        days: Number of days to forecast (1-7)
    
    Returns:
        Forecast information as a string
    """
    if days < 1 or days > 7:
        return "Forecast days must be between 1 and 7."
    
    # Mock forecast data
    conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy", "Stormy", "Clear", "Windy"]
    import random
    
    location = location.title()
    forecast = f"Weather forecast for {location}:\n"
    
    for i in range(days):
        day = ["Today", "Tomorrow", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"][i]
        condition = random.choice(conditions)
        temp = random.randint(15, 30)
        forecast += f"- {day}: {condition}, {temp}°C\n"
    
    return forecast

# Run the server when the script is executed directly
if __name__ == "__main__":
    mcp.run() 