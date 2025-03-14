from agents import Agent, ModelSettings, function_tool
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")

@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny"

weather_haiku_agent = Agent(
    name="Weather Haiku Agent",
    instructions="You create haikus about the weather. Use the weather tool to get information.",
    tools=[get_weather],
)

async def main():
    from agents import Runner, set_default_openai_key
    
    set_default_openai_key(openai_api_key)
    
    # Example using the weather haiku agent
    result = await Runner.run(weather_haiku_agent, "Tell me about the weather in Tokyo")
    print("Weather Haiku result:", result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
