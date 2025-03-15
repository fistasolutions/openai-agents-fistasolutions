import os
from dotenv import load_dotenv
from agents import Agent, function_tool, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
import asyncio

# Load the environment variables from the .env file
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# Check if the API key is present; if not, raise an error
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

# Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny"

weather_haiku_agent = Agent(
    name="Weather Haiku Agent",
    instructions="You create haikus about the weather. Use the weather tool to get information.",
    tools=[get_weather],
    model=model
)

async def main():
    # Example using the weather haiku agent
    result = await Runner.run(weather_haiku_agent, "Tell me about the weather in Tokyo", run_config=config)
    print("Weather Haiku result:", result.final_output)

if __name__ == "__main__":
    asyncio.run(main()) 