from dataclasses import dataclass
from typing import List, Optional, Callable
import os
from dotenv import load_dotenv
from agents import Agent, function_tool, RunContextWrapper, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
import asyncio
import random

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

# Define the UserContext class
@dataclass
class UserContext:
    name: str
    language: str
    interests: List[str]
    experience_level: str  # "beginner", "intermediate", or "expert"

# Define a function that generates dynamic instructions based on context
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
    elif user.experience_level == "intermediate":
        base_instructions += """
        You can use some technical terms but explain complex concepts.
        Provide more detailed information and some advanced tips.
        """
    elif user.experience_level == "expert":
        base_instructions += """
        You can use technical language freely.
        Focus on advanced techniques and in-depth analysis.
        Be concise and precise in your explanations.
        """
    
    # Add language-specific instructions
    if user.language != "English":
        base_instructions += f"""
        Respond in {user.language} when possible.
        Use simple sentence structures for clarity.
        """
    
    return base_instructions

# Define some tools for the agent
@function_tool
def get_recommendation(topic: str, experience_level: str) -> str:
    """Get a personalized recommendation on a specific topic based on experience level"""
    recommendations = {
        "programming": {
            "beginner": "Try starting with Python - it's beginner-friendly and versatile.",
            "intermediate": "Consider learning a framework like Django or Flask for web development.",
            "expert": "Explore advanced topics like concurrency, metaprogramming, or contributing to open source."
        },
        "cooking": {
            "beginner": "Start with simple recipes that have few ingredients and steps.",
            "intermediate": "Try experimenting with different cuisines and techniques.",
            "expert": "Consider molecular gastronomy or advanced baking techniques."
        },
        "photography": {
            "beginner": "Learn the basics of composition and lighting with your smartphone.",
            "intermediate": "Experiment with manual settings on a DSLR or mirrorless camera.",
            "expert": "Try specialized techniques like astrophotography or advanced post-processing."
        }
    }
    
    if topic.lower() in recommendations:
        if experience_level.lower() in recommendations[topic.lower()]:
            return recommendations[topic.lower()][experience_level.lower()]
    
    return f"I don't have specific recommendations for {topic} at {experience_level} level yet."

# Create an agent with dynamic instructions
dynamic_agent = Agent[UserContext](
    name="Personalized Assistant",
    instructions=dynamic_instructions,
    tools=[get_recommendation],
    model=model
)

async def main():
    # Create different user contexts
    beginner_user = UserContext(
        name="Alex",
        language="English",
        interests=["programming", "cooking", "hiking"],
        experience_level="beginner"
    )
    
    intermediate_user = UserContext(
        name="Maria",
        language="Spanish",
        interests=["photography", "travel", "music"],
        experience_level="intermediate"
    )
    
    expert_user = UserContext(
        name="Dr. Chen",
        language="English",
        interests=["quantum physics", "mathematics", "programming"],
        experience_level="expert"
    )
    
    runner = Runner()
    
    # Example queries
    general_query = "Can you help me learn something new?"
    specific_query = "I want to improve my programming skills"
    
    # Test with different user contexts
    print("\n--- Beginner User Example ---")
    result = await runner.run(dynamic_agent, general_query, context=beginner_user, run_config=config)
    print(f"Query: {general_query}")
    print(f"Response for {beginner_user.name} (Beginner):")
    print(result.final_output)
    
    print("\n--- Intermediate User Example ---")
    result = await runner.run(dynamic_agent, general_query, context=intermediate_user, run_config=config)
    print(f"Query: {general_query}")
    print(f"Response for {intermediate_user.name} (Intermediate):")
    print(result.final_output)
    
    print("\n--- Expert User Example ---")
    result = await runner.run(dynamic_agent, specific_query, context=expert_user, run_config=config)
    print(f"Query: {specific_query}")
    print(f"Response for {expert_user.name} (Expert):")
    print(result.final_output)
    
    # Interactive mode with random user selection
    print("\n--- Interactive Mode ---")
    print("Type 'exit' to quit")
    
    users = [beginner_user, intermediate_user, expert_user]
    current_user = random.choice(users)
    print(f"Current user: {current_user.name} ({current_user.experience_level})")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            break
        elif user_input.lower() == 'switch user':
            current_user = random.choice(users)
            print(f"Switched to user: {current_user.name} ({current_user.experience_level})")
            continue
        
        response = await runner.run(dynamic_agent, user_input, context=current_user, run_config=config)
        print(f"\nAgent to {current_user.name}: {response.final_output}")

if __name__ == "__main__":
    asyncio.run(main()) 