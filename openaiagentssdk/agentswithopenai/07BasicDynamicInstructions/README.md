# 🔄 Basic Dynamic Instructions Example

## What This Code Does (Big Picture)
Imagine having an AI teacher that changes how it explains things based on whether you're a beginner, intermediate, or expert! This code creates an AI assistant that adjusts its language, detail level, and examples based on who it's talking to.

Now, let's go step by step!

## Step 1: Setting Up the Magic Key 🗝️
```python
from agentswithopenai import Agent,Runner, ModelSettings, function_tool, RunContextWrapper
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List
import asyncio
import os
import random
from agentswithopenai import set_default_openai_key

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
set_default_openai_key(api_key)
```
The AI assistant needs a magic key (API key) to work properly.

This code finds the magic key hidden in a secret file (.env) and unlocks it.

## Step 2: Creating a User Profile Class 👤
```python
@dataclass
class UserContext:
    name: str
    language: str
    interests: List[str]
    experience_level: str  # "beginner", "intermediate", or "expert"
```
This creates a template for storing information about users:
- Their name
- What language they speak
- What topics they're interested in
- Their experience level (beginner, intermediate, or expert)

## Step 3: Creating Dynamic Instructions Function 📝
```python
def dynamic_instructions(
    context: RunContextWrapper[UserContext], agent: Agent[UserContext]
) -> str:
    user = context.context
    
    # Base instructions that apply to everyone
    base_instructions = f"""
    The user's name is {user.name}. They prefer communication in {user.language}.
    Their experience level is: {user.experience_level}.
    Their interests include: {', '.join(user.interests)}.
    
    Tailor your responses to match their experience level and interests.
    """
    
    # Add specific instructions based on experience level
    if user.experience_level == "beginner":
        base_instructions += """
        Use simple explanations and avoid technical jargon.
        Provide step-by-step guidance and offer encouragement.
        """
    elif user.experience_level == "expert":
        base_instructions += """
        You can use technical language freely.
        Focus on advanced techniques and in-depth analysis.
        """
    
    return base_instructions
```
This function:
- Takes user information as input
- Creates custom instructions based on that user
- Adds different instructions for beginners vs. experts
- Returns personalized instructions for the AI

## Step 4: Creating a Recommendation Tool 🛠️
```python
@function_tool
def get_recommendation(topic: str, experience_level: str) -> str:
    """Get a personalized recommendation on a specific topic based on experience level"""
    recommendations = {
        "programming": {
            "beginner": "Try starting with Python - it's beginner-friendly and versatile.",
            "expert": "Explore advanced topics like concurrency, metaprogramming, or contributing to open source."
        },
        # ... more recommendations
    }
    # ... returns appropriate recommendation
```
This tool provides different recommendations based on:
- What topic the user is interested in
- What experience level they have

## Step 5: Creating the Dynamic AI Assistant 🤖
```python
dynamic_agent = Agent[UserContext](
    name="Personalized Assistant",
    instructions=dynamic_instructions,
    tools=[get_recommendation],
)
```
This creates an AI assistant that:
- Uses the dynamic_instructions function to get custom instructions
- Can access the user's profile information
- Uses the recommendation tool to give personalized suggestions

## Step 6: Running the Program with Different Users 🏃‍♂️
```python
async def main():
    # Create different user contexts
    beginner_user = UserContext(
        name="Alex",
        language="English",
        interests=["programming", "art", "music"],
        experience_level="beginner"
    )
    
    expert_user = UserContext(
        name="Sam",
        language="English",
        interests=["programming", "AI", "mathematics"],
        experience_level="expert"
    )
    
    # Test with different users
    result = await runner.run(dynamic_agent, "Tell me about programming", context=beginner_user)
    result = await runner.run(dynamic_agent, "Tell me about programming", context=expert_user)
```
This tests the AI with different types of users:
1. A beginner who gets simple explanations without jargon
2. An expert who gets advanced information with technical terms

## Final Summary 📌
✅ We created a way to store information about different users
✅ We created a function that generates custom instructions based on the user
✅ We created an AI that adapts its responses to match the user's level
✅ We tested the AI with both beginners and experts

## Try It Yourself! 🚀
1. Install the required packages:
   ```
   uv add openai-agents dotenv
   ```
2. Create a `.env` file with your API key
3. Run the program:
   ```
   uv run basicdynamicinstructions.py
   ```
4. Try creating different user profiles with various experience levels!

## What You'll Learn 🧠
- How to create dynamic instructions that change based on context
- How to store and use user information
- How to personalize AI responses for different users
- How to use conditional logic to modify agent behavior

Happy coding! 🎉 