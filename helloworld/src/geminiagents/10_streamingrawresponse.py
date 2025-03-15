import os
from dotenv import load_dotenv
import asyncio
from openai.types.chat import ChatCompletionChunk
from openai.types.chat.chat_completion_chunk import ChoiceDelta
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
import time

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
    # Create a joke-telling agent
    agent = Agent(
        name="Joker",
        instructions="""
        You are a friendly assistant who specializes in telling jokes.
        When asked for jokes, provide clean, family-friendly humor.
        Make your jokes engaging and suitable for all audiences.
        """,
        model=model
    )

    print("\n--- Streaming Jokes Example ---")
    print("Asking for 5 jokes...\n")
    
    # Run the agent with streaming enabled
    result = Runner.run_streamed(agent, input="Please tell me 5 jokes.", run_config=config)
    
    # Process the streaming events
    print("Response: ", end="", flush=True)
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ChatCompletionChunk):
            # Extract the text delta from the event
            for choice in event.data.choices:
                if choice.delta and choice.delta.content:
                    print(choice.delta.content, end="", flush=True)
                    # Add a small delay to make the streaming more visible
                    await asyncio.sleep(0.01)
    
    print("\n\n--- Streaming Story Example ---")
    print("Asking for a short story...\n")
    
    # Create a storyteller agent
    storyteller = Agent(
        name="Storyteller",
        instructions="""
        You are a creative storyteller who crafts engaging short stories.
        Keep your stories concise but captivating, with interesting characters and plots.
        Your stories should have a clear beginning, middle, and end.
        """,
        model=model
    )
    
    # Run the storyteller agent with streaming enabled
    result = Runner.run_streamed(storyteller, input="Tell me a short story about a robot learning to paint.", run_config=config)
    
    # Process the streaming events with timing information
    start_time = time.time()
    last_update = start_time
    chars_received = 0
    
    print("Response: ", end="", flush=True)
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ChatCompletionChunk):
            for choice in event.data.choices:
                if choice.delta and choice.delta.content:
                    content = choice.delta.content
                    print(content, end="", flush=True)
                    
                    # Update statistics
                    now = time.time()
                    chars_received += len(content)
                    if now - last_update >= 1.0:  # Update stats every second
                        elapsed = now - start_time
                        chars_per_second = chars_received / elapsed
                        last_update = now
    
    # Print final statistics
    total_time = time.time() - start_time
    total_chars = chars_received
    avg_chars_per_second = total_chars / total_time
    
    print(f"\n\nStreaming Statistics:")
    print(f"Total characters: {total_chars}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average speed: {avg_chars_per_second:.2f} characters per second")
    
    # Interactive mode with streaming
    print("\n--- Interactive Streaming Mode ---")
    print("Type 'exit' to quit")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            break
        
        print("Assistant: ", end="", flush=True)
        result = Runner.run_streamed(agent, input=user_input, run_config=config)
        
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ChatCompletionChunk):
                for choice in event.data.choices:
                    if choice.delta and choice.delta.content:
                        print(choice.delta.content, end="", flush=True)
        print()  # Add a newline after the response

if __name__ == "__main__":
    asyncio.run(main()) 