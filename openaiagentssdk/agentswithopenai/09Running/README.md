# 🏃‍♀️ Running Example

## What This Code Does (Big Picture)
Imagine having a conversation with your robot friend where it remembers what you talked about earlier! This code shows how to have multi-turn conversations with an AI assistant and how to keep track of the conversation history.

Now, let's go step by step!

## Step 1: Setting Up the Magic Key 🗝️
```python
from agentswithopenai import Agent, ModelSettings, function_tool, trace
from dotenv import load_dotenv
import asyncio
import os
import uuid
from agentswithopenai import Runner, set_default_openai_key

load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")
set_default_openai_key(openai_api_key)
```
The AI assistant needs a magic key (API key) to work properly.

This code finds the magic key hidden in a secret file (.env) and unlocks it.

## Step 2: Creating a Concise AI Assistant 🤖
```python
agent = Agent(
    name="Assistant",
    instructions="Reply very concisely. Provide accurate but brief answers."
)
```
This creates an AI assistant that gives short, to-the-point answers.

## Step 3: Creating a Conversation ID 🏷️
```python
thread_id = str(uuid.uuid4())
```
This creates a unique ID for our conversation, like putting a label on a specific chat thread.

## Step 4: Starting a Traced Conversation 🔍
```python
with trace(workflow_name="Conversation", group_id=thread_id):
    # First turn
    result = await Runner.run(agent, "What city is the Golden Gate Bridge in?")
    print(f"Assistant: {result.final_output}")
    
    # Second turn - using the conversation history
    new_input = result.to_input_list() + [{"role": "user", "content": "What state is it in?"}]
    result = await Runner.run(agent, new_input)
    print(f"Assistant: {result.final_output}")
    
    # Third turn - continuing the conversation
    new_input = result.to_input_list() + [{"role": "user", "content": "When was it built?"}]
    result = await Runner.run(agent, new_input)
```
This creates a three-turn conversation where:
1. We ask about the Golden Gate Bridge's city
2. We ask what state it's in (without mentioning the bridge again)
3. We ask when it was built (again without mentioning the bridge)

The AI remembers the context from previous turns, so it knows we're still talking about the Golden Gate Bridge.

## Step 5: Starting a New Conversation 🆕
```python
new_thread_id = str(uuid.uuid4())

with trace(workflow_name="New Conversation", group_id=new_thread_id):
    # First turn of new conversation
    result = await Runner.run(agent, "Tell me about the Eiffel Tower")
    
    # Second turn of new conversation
    new_input = result.to_input_list() + [{"role": "user", "content": "How tall is it?"}]
    result = await Runner.run(agent, new_input)
```
This starts a completely new conversation about the Eiffel Tower, separate from our bridge conversation.

## Step 6: Creating an Interactive Mode 💬
```python
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
            continue
        
        if conversation_history is None:
            # First message in conversation
            result = await Runner.run(agent, user_input)
        else:
            # Continuing conversation
            new_input = conversation_history.to_input_list() + [{"role": "user", "content": user_input}]
            result = await Runner.run(agent, new_input)
        
        print(f"Assistant: {result.final_output}")
        conversation_history = result
```
This creates an interactive chat where:
- You can type messages and get responses
- The AI remembers the conversation context
- You can type "new" to start a fresh conversation
- You can type "exit" to quit

## Final Summary 📌
✅ We created an AI assistant that gives concise answers
✅ We had a multi-turn conversation where the AI remembered context
✅ We used tracing to monitor and organize conversations
✅ We created an interactive chat mode with memory
✅ We learned how to start new conversations when needed

## Try It Yourself! 🚀
1. Install the required packages:
   ```
   uv add openai-agents dotenv
   ```
2. Create a `.env` file with your API key
3. Run the program:
   ```
   uv run running.py
   ```
4. Try having multi-turn conversations about different topics!

## What You'll Learn 🧠
- How to maintain conversation history
- How to use tracing to monitor conversations
- How to start new conversations
- How to build an interactive chat interface

Happy coding! 🎉 