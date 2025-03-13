import os
from dotenv import load_dotenv
from agents import Agent, Runner

def main() -> None:
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    # Set the API key in the environment for the agent to use
    # Setting it this way ensures it's available for all components including tracers
    os.environ["OPENAI_API_KEY"] = openai_api_key
    
    # Some OpenAI libraries might look for these alternative environment variables
    os.environ["OPENAI_KEY"] = openai_api_key
    
    # Create an agent with simple instructions
    agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant"
    )

    # Run the agent with a prompt about recursion
    result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
    
    # Print the final output
    print(result.final_output)

if __name__ == "__main__":
    main()
