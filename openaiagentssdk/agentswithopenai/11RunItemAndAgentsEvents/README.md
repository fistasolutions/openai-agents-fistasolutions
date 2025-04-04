# 🔍 Run Item And Agents Events Example

## What This Code Does (Big Picture)
Imagine being able to see exactly what your robot friend is thinking and doing behind the scenes! This code shows how to track all the steps an AI takes when answering your questions, including when it calls tools, what it's thinking, and how it forms its response.

Now, let's go step by step!

## Step 1: Setting Up the Magic Key 🗝️
```python
import asyncio
import random
from agentswithopenai import Agent, ItemHelpers, Runner, function_tool, set_default_openai_key
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")
set_default_openai_key(openai_api_key)
```
The AI assistant needs a magic key (API key) to work properly.

This code finds the magic key hidden in a secret file (.env) and unlocks it.

## Step 2: Creating Tools for the Joke Agent 🛠️
```python
@function_tool
def how_many_jokes() -> int:
    """Randomly decide how many jokes to tell (between 1 and 5)"""
    return random.randint(1, 5)

@function_tool
def get_joke_topic() -> str:
    """Get a random topic for a joke"""
    topics = [
        "programming", "animals", "food", "weather", 
        "office life", "sports", "movies", "technology"
    ]
    return random.choice(topics)
```
These tools help the joke agent:
- Decide how many jokes to tell
- Pick random topics for jokes

## Step 3: Creating a Joke-Telling Agent 🤖
```python
agent = Agent(
    name="Joker",
    instructions="""
    You are a joke-telling assistant. When greeting the user:
    1. First call the `how_many_jokes` tool to determine how many jokes to tell
    2. For each joke, call the `get_joke_topic` tool to get a topic
    3. Tell a joke about that topic
    4. Continue until you've told the requested number of jokes
    
    Keep your jokes clean and family-friendly.
    """,
    tools=[how_many_jokes, get_joke_topic],
)
```
This creates an AI assistant that tells jokes on random topics.

## Step 4: Running the Agent with Event Tracking 🔍
```python
result = Runner.run_streamed(agent, input="Tell me some jokes please!")

# Process the stream events
async for event in result.stream_events():
    if event.type == "run_item_stream_event":
        # This shows each step the agent takes
        print(f"Agent is doing: {event.item.type}")
    elif event.type == "agent_updated_stream_event":
        # This shows when the agent's state changes
        print(f"Agent updated: {event.agent_state}")
    elif event.type == "tool_call_stream_event":
        # This shows when the agent calls a tool
        print(f"Tool called: {event.tool_call.name}")
```
This code:
1. Runs the agent in streaming mode
2. Listens for different types of events
3. Shows what the agent is doing at each step
4. Tracks when tools are called
5. Monitors the agent's internal state

## Step 5: Creating a Multi-Agent Joke System 🤖🤖🤖
```python
# Create specialized agents
joke_agent = Agent(
    name="Joke Generator",
    instructions="You generate a single, original, family-friendly joke.",
)

evaluator_agent = Agent(
    name="Joke Evaluator",
    instructions="You evaluate jokes for humor, originality, and appropriateness.",
)

improver_agent = Agent(
    name="Joke Improver",
    instructions="You improve jokes based on evaluation feedback.",
)
```
This creates a system with three specialized agents:
1. One that generates jokes
2. One that evaluates jokes
3. One that improves jokes based on feedback

## Step 6: Running the Multi-Agent Pipeline 🔄
```python
# Generate a joke
joke_result = Runner.run_streamed(joke_agent, input="Create a joke about programming")
joke_text = ""

print("Tracking joke generation:")
async for event in joke_result.stream_events():
    if event.type == "run_item_stream_event" and event.item.type == "message_output_item":
        joke_text = ItemHelpers.text_message_output(event.item)
        print("-- Joke generated")

# Evaluate the joke
eval_result = Runner.run_streamed(
    evaluator_agent,
    input=f"Please evaluate this joke: {joke_text}",
)

# Improve the joke
improve_result = Runner.run_streamed(
    improver_agent,
    input=f"Please improve this joke: {joke_text}\nThe evaluation was: {evaluation}",
)
```
This creates a pipeline where:
1. The joke agent creates a joke
2. The evaluator agent reviews the joke
3. The improver agent enhances the joke based on feedback

## Final Summary 📌
✅ We created tools for generating random joke parameters
✅ We created a joke-telling agent that uses these tools
✅ We tracked all the events and steps the agent takes
✅ We created a multi-agent system for joke creation and improvement
✅ We monitored the entire process with detailed event tracking

## Try It Yourself! 🚀
1. Install the required packages:
   ```
   uv add openai-agents dotenv
   ```
2. Create a `.env` file with your API key
3. Run the program:
   ```
   uv run runitemandagentsevents.py
   ```
4. Watch the detailed event stream as the agents work!

## What You'll Learn 🧠
- How to track and process agent events
- How to build multi-agent systems
- How to monitor tool usage
- How to create a pipeline of agents that work together

Happy coding! 🎉 