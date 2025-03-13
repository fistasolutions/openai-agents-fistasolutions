import os
import asyncio
from agents import Agent, Runner, set_default_openai_key

# Load environment variables from .env file manually
def load_env_from_file():
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                key, value = line.split('=', 1)
                os.environ[key] = value
    except FileNotFoundError:
        print("Warning: .env file not found")

# Load environment variables
load_env_from_file()

# Get OpenAI API key from environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

# Set the OpenAI API key
set_default_openai_key(OPENAI_API_KEY)

# Create a basic agent
agent = Agent(
    name="Helpful Assistant",
    instructions="You are a helpful assistant. Answer user questions clearly and concisely.",
    model=OPENAI_MODEL
)

async def run_agent(user_input):
    """Run the agent with the given user input."""
    result = await Runner.run(agent, user_input)
    return result.final_output

async def interactive_session():
    """Run an interactive session with the agent."""
    print("Welcome to the Basic OpenAI Agent!")
    print("Type 'exit' to quit the session.")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        print("\nThinking...")
        response = await run_agent(user_input)
        print(f"\nAssistant: {response}")

if __name__ == "__main__":
    asyncio.run(interactive_session()) 