from dotenv import load_dotenv
import os
from agents import Agent, Runner

# Load environment variables from .env file
load_dotenv()

# Retrieve API key (optional, just to check it's loaded)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Missing OPENAI_API_KEY. Please set it in .env or export it.")

# Initialize agent
agent = Agent(name="Assistant", instructions="You are a helpful assistant")

# Run agent
result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)
