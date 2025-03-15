import os
from dotenv import load_dotenv
from agents import Agent, trace, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
import asyncio
import uuid

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

async def main():
    # Create a simple agent with concise instructions
    agent = Agent(
        name="Assistant",
        instructions="Reply very concisely. Provide accurate but brief answers.",
        model=model
    )
    
    # Generate a unique thread ID for this conversation
    thread_id = str(uuid.uuid4())
    
    # Start a traced conversation
    with trace(workflow_name="Conversation", group_id=thread_id):
        print("\n--- First Turn ---")
        # First turn
        result = await Runner.run(agent, "What city is the Golden Gate Bridge in?", run_config=config)
        print("User: What city is the Golden Gate Bridge in?")
        print(f"Assistant: {result.final_output}")
        
        print("\n--- Second Turn ---")
        # Second turn - using the conversation history
        new_input = result.to_input_list() + [{"role": "user", "content": "What state is it in?"}]
        result = await Runner.run(agent, new_input, run_config=config)
        print("User: What state is it in?")
        print(f"Assistant: {result.final_output}")
        
        print("\n--- Third Turn ---")
        # Third turn - continuing the conversation
        new_input = result.to_input_list() + [{"role": "user", "content": "When was it built?"}]
        result = await Runner.run(agent, new_input, run_config=config)
        print("User: When was it built?")
        print(f"Assistant: {result.final_output}")
    
    # Start a new conversation with the same agent but a different thread ID
    new_thread_id = str(uuid.uuid4())
    
    with trace(workflow_name="New Conversation", group_id=new_thread_id):
        print("\n--- New Conversation ---")
        # First turn of new conversation
        result = await Runner.run(agent, "Tell me about the Eiffel Tower", run_config=config)
        print("User: Tell me about the Eiffel Tower")
        print(f"Assistant: {result.final_output}")
        
        # Second turn of new conversation
        new_input = result.to_input_list() + [{"role": "user", "content": "How tall is it?"}]
        result = await Runner.run(agent, new_input, run_config=config)
        print("User: How tall is it?")
        print(f"Assistant: {result.final_output}")
    
    # Interactive mode with conversation history
    print("\n--- Interactive Mode ---")
    print("Type 'exit' to quit or 'new' to start a new conversation")
    
    interactive_thread_id = str(uuid.uuid4())
    conversation_history = None
    
    with trace(workflow_name="Interactive Conversation", group_id=interactive_thread_id):
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'new':
                print("Starting a new conversation")
                conversation_history = None
                interactive_thread_id = str(uuid.uuid4())
                continue
            
            if conversation_history is None:
                # First message in conversation
                result = await Runner.run(agent, user_input, run_config=config)
            else:
                # Continuing conversation
                new_input = conversation_history.to_input_list() + [{"role": "user", "content": user_input}]
                result = await Runner.run(agent, new_input, run_config=config)
            
            print(f"Assistant: {result.final_output}")
            conversation_history = result

if __name__ == "__main__":
    asyncio.run(main()) 