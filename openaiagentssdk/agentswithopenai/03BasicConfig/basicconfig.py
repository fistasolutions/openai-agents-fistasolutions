from agents import Agent, Runner, ModelSettings, function_tool
from dotenv import load_dotenv
from agents import set_default_openai_key
import asyncio
import os

load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")
set_default_openai_key(api_key)

@function_tool
def get_weather(city: str) -> str:
    """Get the current weather in a given city"""
    return f"The weather in {city} is sunny with a temperature of 70 degrees."

weather_haiku_agent = Agent(
    name="Weather Haiku Agent",
    instructions="You create haikus about the weather. Use the weather tool to get information.",
    tools=[get_weather],
)

async def main():
    result = await Runner.run(weather_haiku_agent, "What is the weather in Tokyo?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
    