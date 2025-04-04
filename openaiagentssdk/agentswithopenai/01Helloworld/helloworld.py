from agentswithopenai import Agent, Runner
from dotenv import load_dotenv
import os

load_dotenv()

# Create an agent using Claude instead of GPT-4o
agent = Agent(
    name="Assistant", 
    instructions="You are a helpful assistant", 
    model="claude-3-5-sonnet-20240620"  # Using Claude model instead of GPT-4o
)

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")

print(result.final_output)