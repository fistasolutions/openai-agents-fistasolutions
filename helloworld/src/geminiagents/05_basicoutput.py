from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from agents import Agent, function_tool, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
import asyncio
from datetime import datetime

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

# Define the structured output model
class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: List[str]
    location: Optional[str] = None
    description: Optional[str] = None

# Create an agent with structured output
calendar_extractor = Agent(
    name="Calendar Event Extractor",
    instructions="""
    You are a specialized assistant that extracts calendar events from text.
    Extract all details about events including:
    - Event name
    - Date (in YYYY-MM-DD format)
    - List of participants
    - Location (if mentioned)
    - Description (if available)
    
    If multiple events are mentioned, focus on the most prominent one.
    If a detail is not provided in the text, omit that field from your response.
    """,
    output_type=CalendarEvent,
    model=model
)

# Helper function to validate extracted dates
@function_tool
def validate_date(date_str: str) -> str:
    """Validate and format a date string to YYYY-MM-DD format"""
    try:
        # Try to parse the date - this is just an example and would need more robust parsing in a real app
        formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y"]
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return date_str  # Return original if no format matches
    except Exception:
        return date_str

# Create a more complex agent that also uses tools
advanced_calendar_extractor = Agent(
    name="Advanced Calendar Event Extractor",
    instructions="""
    You are a specialized assistant that extracts calendar events from text.
    Extract all details about events including:
    - Event name
    - Date (in YYYY-MM-DD format, use the validate_date tool to ensure correct formatting)
    - List of participants
    - Location (if mentioned)
    - Description (if available)
    
    If multiple events are mentioned, focus on the most prominent one.
    If a detail is not provided in the text, omit that field from your response.
    """,
    output_type=CalendarEvent,
    tools=[validate_date],
    model=model
)

async def main():
    # Example texts with calendar events
    simple_text = "Let's have a team meeting on 2023-05-15 with John, Sarah, and Mike."
    
    complex_text = """
    Hi team,
    
    I'm scheduling our quarterly planning session for May 20, 2023 at the main conference room.
    All department heads (Lisa, Mark, Jennifer, and David) should attend. We'll be discussing
    our Q3 objectives and reviewing Q2 performance. Please bring your department reports.
    
    Also, don't forget about the company picnic on 06/15/2023!
    """
    
    # Example using the basic calendar extractor
    print("\n--- Basic Calendar Extractor Example ---")
    result = await Runner.run(calendar_extractor, simple_text, run_config=config)
    print("Extracted Event:", result.final_output)
    print(f"Event Type: {type(result.final_output)}")
    
    # Example using the advanced calendar extractor with date validation
    print("\n--- Advanced Calendar Extractor Example ---")
    result = await Runner.run(advanced_calendar_extractor, complex_text, run_config=config)
    print("Extracted Event:", result.final_output)
    
    # Access structured data fields
    event = result.final_output
    print(f"\nEvent Name: {event.name}")
    print(f"Date: {event.date}")
    print(f"Participants: {', '.join(event.participants)}")
    if event.location:
        print(f"Location: {event.location}")
    if event.description:
        print(f"Description: {event.description}")

if __name__ == "__main__":
    asyncio.run(main()) 