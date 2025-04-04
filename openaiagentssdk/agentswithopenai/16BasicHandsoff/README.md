# 🔄 Customizing Handoffs Example

## What This Code Does (Big Picture)
Imagine having a team of robot helpers where you can control exactly when and how they pass tasks to each other! This code shows how to create custom rules for when one AI assistant should hand off a conversation to another specialist AI.

Now, let's go step by step!

## Step 1: Setting Up the Magic Key 🗝️
```python
from agentswithopenai import Agent, Runner, function_tool, set_default_openai_key
from dotenv import load_dotenv
import asyncio
import os
import re

load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")
set_default_openai_key(openai_api_key)
```
The AI assistants need a magic key (API key) to work properly.

This code finds the magic key hidden in a secret file (.env) and unlocks it.

## Step 2: Creating Specialist Agents 👨‍🔧👩‍🍳
```python
tech_support_agent = Agent(
    name="Tech Support",
    handoff_description="Specialist for technical problems with computers, phones, and other devices",
    instructions="""
    You are a technical support specialist. Help users troubleshoot problems with:
    - Computers and laptops
    - Smartphones and tablets
    - Internet connectivity
    - Software installation and configuration
    
    Provide step-by-step instructions and ask clarifying questions when needed.
    """,
)

cooking_agent = Agent(
    name="Cooking Assistant",
    handoff_description="Specialist for cooking advice, recipes, and food preparation",
    instructions="""
    You are a cooking expert. Help users with:
    - Finding and adapting recipes
    - Cooking techniques and methods
    - Ingredient substitutions
    - Meal planning and preparation
    
    Be friendly and encouraging, and consider dietary restrictions when mentioned.
    """,
)
```
This creates two specialist AIs:
- A tech support expert who helps with device problems
- A cooking expert who helps with recipes and food preparation

## Step 3: Creating a Custom Handoff Function 🔀
```python
def should_handoff_to_cooking(message: str) -> bool:
    """Determine if a message should be handed off to the cooking agent"""
    # Look for cooking-related keywords
    cooking_keywords = [
        "recipe", "cook", "food", "meal", "ingredient", "bake", "kitchen",
        "dinner", "lunch", "breakfast", "dish", "cuisine"
    ]
    
    message_lower = message.lower()
    
    # Check for cooking keywords
    for keyword in cooking_keywords:
        if keyword in message_lower:
            return True
    
    # Check for specific patterns like "how to make X"
    if re.search(r"how to (make|prepare|cook)", message_lower):
        return True
    
    return False
```
This function:
- Takes a message as input
- Checks if it contains cooking-related keywords
- Looks for patterns like "how to make X"
- Returns True if the message should go to the cooking expert

## Step 4: Creating a Main Assistant with Custom Handoff Logic 🤖
```python
main_agent = Agent(
    name="General Assistant",
    instructions="""
    You are a helpful general assistant. You can answer a wide range of questions,
    but for specialized topics, you'll hand off to the appropriate specialist.
    
    For technical support questions, hand off to the Tech Support agent.
    For cooking-related questions, the system will automatically detect and hand off to the Cooking Assistant.
    """,
    handoffs=[tech_support_agent, cooking_agent],
    handoff_handlers={
        cooking_agent.name: should_handoff_to_cooking
    }
)
```
This creates a main AI assistant that:
- Handles general questions itself
- Can hand off to tech support when needed
- Uses our custom function to decide when to hand off cooking questions

## Step 5: Running the Program with Different Questions 🏃‍♂️
```python
async def main():
    # Test with different types of queries
    general_query = "What's the capital of France?"
    tech_query = "My computer won't turn on. What should I do?"
    cooking_query = "How do I make chocolate chip cookies?"
    
    # Run the main agent with each query
    print("\n--- General Query ---")
    result = await Runner.run(main_agent, general_query)
    print(f"Handled by: {result.agent_name}")
    print(result.final_output)
    
    print("\n--- Tech Support Query ---")
    result = await Runner.run(main_agent, tech_query)
    print(f"Handled by: {result.agent_name}")
    print(result.final_output)
    
    print("\n--- Cooking Query ---")
    result = await Runner.run(main_agent, cooking_query)
    print(f"Handled by: {result.agent_name}")
    print(result.final_output)
```
This tests the system with different types of questions:
1. A general question (should be handled by the main agent)
2. A tech support question (should be handed off to tech support)
3. A cooking question (should be automatically detected and handed off)

## Step 6: Creating an Interactive Mode 💬
```python
print("\n--- Interactive Mode ---")
print("Type 'exit' to quit")

while True:
    user_input = input("\nYou: ")
    if user_input.lower() == 'exit':
        break
    
    result = await Runner.run(main_agent, user_input)
    print(f"\nResponse from {result.agent_name}:")
    print(result.final_output)
```
This creates an interactive mode where:
- You can ask any type of question
- The system automatically decides which agent should handle it
- You can see which agent responded to your question
- You can type "exit" to quit

## Final Summary 📌
✅ We created specialist agents for tech support and cooking
✅ We created a custom function to detect cooking-related questions
✅ We created a main agent that uses this function for handoffs
✅ We tested the system with different types of questions
✅ We created an interactive mode that shows which agent responds

## Try It Yourself! 🚀
1. Install the required packages:
   ```
   uv add openai-agents dotenv
   ```
2. Create a `.env` file with your API key
3. Run the program:
   ```
   uv run customizinghandsoff.py
   ```
4. Try asking different types of questions to see which agent handles them!

## What You'll Learn 🧠
- How to create custom handoff logic
- How to use pattern matching for message classification
- How to create a system of specialized agents
- How to track which agent handles each request

Happy coding! 🎉 