# 🌊 Streaming Raw Response Example

## What This Code Does (Big Picture)
Imagine watching your robot friend think out loud, seeing its answers appear letter by letter in real-time! This code shows how to get AI responses as they're being generated, instead of waiting for the complete answer.

Now, let's go step by step!

## Step 1: Setting Up the Magic Key 🗝️
```python
import asyncio
from openai.types.chat import ChatCompletionChunk
from openai.types.chat.chat_completion_chunk import ChoiceDelta
from agentswithopenai import Agent, Runner, set_default_openai_key
from dotenv import load_dotenv
import os
import time

load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")
set_default_openai_key(openai_api_key)
```
The AI assistant needs a magic key (API key) to work properly.

This code finds the magic key hidden in a secret file (.env) and unlocks it.

## Step 2: Creating a Joke-Telling AI 🤖
```python
agent = Agent(
    name="Joker",
    instructions="""
    You are a friendly assistant who specializes in telling jokes.
    When asked for jokes, provide clean, family-friendly humor.
    Make your jokes engaging and suitable for all audiences.
    """,
)
```
This creates an AI assistant that specializes in telling jokes.

## Step 3: Running the Agent with Streaming Enabled 🌊
```python
result = Runner.run_streamed(agent, input="Please tell me 5 jokes.")
```
This runs the agent in streaming mode, which means we'll get the response piece by piece as it's generated.

## Step 4: Processing the Streaming Events 📊
```python
print("Response: ", end="", flush=True)
async for event in result.stream_events():
    if event.type == "raw_response_event" and isinstance(event.data, ChatCompletionChunk):
        # Extract the text delta from the event
        for choice in event.data.choices:
            if choice.delta and choice.delta.content:
                print(choice.delta.content, end="", flush=True)
                # Add a small delay to make the streaming more visible
                await asyncio.sleep(0.01)
```
This code:
1. Listens for streaming events from the AI
2. Checks if the event contains new text
3. Prints each piece of text as it arrives
4. Uses `flush=True` to make sure it appears immediately
5. Adds a tiny delay to make the streaming more visible

## Step 5: Measuring Streaming Speed ⏱️
```python
# Set up statistics tracking
start_time = time.time()
chars_received = 0
last_update = start_time

# Process the streaming events with statistics
async for event in result.stream_events():
    if event.type == "raw_response_event" and isinstance(event.data, ChatCompletionChunk):
        for choice in event.data.choices:
            if choice.delta and choice.delta.content:
                content = choice.delta.content
                print(content, end="", flush=True)
                
                # Update statistics
                chars_received += len(content)
```
This code tracks:
- When the streaming started
- How many characters we've received
- How fast the characters are coming in

## Step 6: Creating an Interactive Streaming Chat 💬
```python
print("\n--- Interactive Streaming Mode ---")
print("Type 'exit' to quit")

while True:
    user_input = input("\nYou: ")
    if user_input.lower() == 'exit':
        break
    
    print("Assistant: ", end="", flush=True)
    result = Runner.run_streamed(agent, input=user_input)
    
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ChatCompletionChunk):
            for choice in event.data.choices:
                if choice.delta and choice.delta.content:
                    print(choice.delta.content, end="", flush=True)
```
This creates an interactive chat where:
- You can type messages and get streaming responses
- You see the AI's answers appear character by character
- You can type "exit" to quit

## Final Summary 📌
✅ We created a joke-telling AI assistant
✅ We enabled streaming to see responses in real-time
✅ We processed streaming events to display text as it arrives
✅ We measured how fast the streaming responses come in
✅ We created an interactive streaming chat interface

## Try It Yourself! 🚀
1. Install the required packages:
   ```
   uv add openai-agents dotenv
   ```
2. Create a `.env` file with your API key
3. Run the program:
   ```
   uv run streamingrawresponse.py
   ```
4. Watch as the jokes appear character by character!

## What You'll Learn 🧠
- How to enable streaming for AI responses
- How to process streaming events
- How to display text in real-time
- How to measure response speed
- How to create an interactive streaming chat

Happy coding! 🎉 