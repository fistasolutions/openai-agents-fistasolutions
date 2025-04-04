# 🧬 Basic Cloning Example

## What This Code Does (Big Picture)
Imagine creating different versions of your robot friend - one that talks like a pirate, another that speaks like a robot, and a third that writes poetry! This code shows how to create variations of an AI assistant with different personalities and abilities.

Now, let's go step by step!

## Step 1: Setting Up the Magic Key 🗝️
```python
from agentswithopenai import Agent,Runner, ModelSettings, function_tool
from dotenv import load_dotenv
import asyncio
import os
from agentswithopenai import set_default_openai_key

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
set_default_openai_key(api_key)
```
The AI assistants need a magic key (API key) to work properly.

This code finds the magic key hidden in a secret file (.env) and unlocks it.

## Step 2: Creating an Emoji Translation Tool 🔧
```python
@function_tool
def translate_to_emoji(text: str) -> str:
    """Translate text to emoji (mock implementation)"""
    emoji_map = {
        "happy": "😊",
        "sad": "😢",
        "love": "❤️",
        "cool": "😎",
        "food": "🍔",
        # ... more emoji mappings
    }
    
    result = []
    for word in text.lower().split():
        # Remove punctuation
        word = word.strip(".,!?;:")
        if word in emoji_map:
            result.append(emoji_map[word])
        else:
            result.append(word)
    
    return " ".join(result)
```
This tool converts certain words to emoji symbols, which we'll use for one of our special agents.

## Step 3: Creating the Base Agent 🤖
```python
base_agent = Agent(
    name="Base Agent",
    instructions="You are a helpful assistant that responds to user queries in a professional manner.",
    model="gpt-3.5-turbo",  # You can change this to any model you have access to
)
```
This creates our standard, professional AI assistant that will be the starting point for all our variations.

## Step 4: Creating a Pirate-Speaking Agent 🏴‍☠️
```python
pirate_agent = base_agent.clone(
    name="Pirate Agent",
    instructions="""
    You are a pirate-speaking assistant! Always respond in pirate speak.
    Use phrases like "Arr!", "Ahoy matey!", "Shiver me timbers!", and "Yo ho ho!".
    Refer to yourself as a salty sea dog and the user as a landlubber.
    """,
)
```
This creates a copy of our base agent but changes its instructions to make it talk like a pirate.

## Step 5: Creating a Robot-Speaking Agent 🤖
```python
robot_agent = base_agent.clone(
    name="Robot Agent",
    instructions="""
    You are a robot assistant. Respond in a robotic, mechanical manner.
    Use phrases like "PROCESSING QUERY", "EXECUTING RESPONSE", and "INFORMATION RETRIEVED".
    """,
)
```
This creates another copy of our base agent but makes it talk like a robot.

## Step 6: Creating a Poetic Agent 📝
```python
poet_agent = base_agent.clone(
    name="Poet Agent",
    instructions="""
    You are a poetic assistant who responds in verse.
    Use beautiful, flowery language and metaphors.
    Structure your responses as short poems when possible.
    """,
)
```
This creates a third copy that responds with poetic language.

## Step 7: Creating an Emoji Pirate Agent 🏴‍☠️😊
```python
emoji_pirate_agent = pirate_agent.clone(
    name="Emoji Pirate Agent",
    instructions="You are a pirate-speaking assistant who loves emojis! Use emoji translations when possible.",
    tools=[translate_to_emoji],
)
```
This creates a special agent that:
- Is based on the pirate agent (not the base agent)
- Adds the emoji translation tool
- Combines pirate speech with emoji usage

## Step 8: Running the Program with Different Agents 🏃‍♂️
```python
async def main():
    test_query = "Tell me about the weather today"
    
    # Test each agent with the same query
    result = await runner.run(base_agent, test_query)
    result = await runner.run(pirate_agent, test_query)
    result = await runner.run(robot_agent, test_query)
    result = await runner.run(poet_agent, test_query)
    result = await runner.run(emoji_pirate_agent, test_query)
```
This tests all our different agents with the same question to see how they respond differently.

## Final Summary 📌
✅ We created a base agent with professional behavior
✅ We cloned it to create agents with different personalities
✅ We created a special tool for emoji translation
✅ We created an agent that combines pirate speech with emoji usage
✅ We tested all agents with the same question to see their different styles

## Try It Yourself! 🚀
1. Install the required packages:
   ```
   uv add openai-agents dotenv
   ```
2. Create a `.env` file with your API key
3. Run the program:
   ```
   uv run basiccloning.py
   ```
4. Try creating your own agent personalities!

## What You'll Learn 🧠
- How to clone agents to create variations
- How to give agents different personalities
- How to add tools to cloned agents
- How to build on existing agents to create new ones

Happy coding! 🎉 