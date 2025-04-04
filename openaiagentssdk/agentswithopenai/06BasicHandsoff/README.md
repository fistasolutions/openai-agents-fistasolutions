# 🤝 Basic Handoffs Example

## What This Code Does (Big Picture)
Imagine a travel company with different specialists - one for booking flights, another for handling refunds. This code creates a smart receptionist AI that listens to your question and then connects you with the right specialist for help!

Now, let's go step by step!

## Step 1: Setting Up the Magic Key 🗝️
```python
from agentswithopenai import Agent,Runner, ModelSettings, function_tool
from dotenv import load_dotenv
import asyncio
import os
from typing import List, Optional
from agentswithopenai import set_default_openai_key

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
set_default_openai_key(api_key)
```
The AI assistants need a magic key (API key) to work properly.

This code finds the magic key hidden in a secret file (.env) and unlocks it.

## Step 2: Creating Tools for the Specialists 🛠️
```python
@function_tool
def get_available_flights(origin: str, destination: str, date: str) -> str:
    """Get available flights between two cities on a specific date"""
    # This is a mock implementation
    flights = [
        {"flight": "AA123", "departure": "08:00", "arrival": "10:30", "price": "$299"},
        {"flight": "DL456", "departure": "12:15", "arrival": "14:45", "price": "$329"},
        {"flight": "UA789", "departure": "16:30", "arrival": "19:00", "price": "$279"}
    ]
    # ... returns flight information
```
This tool helps the booking specialist find available flights.

```python
@function_tool
def check_refund_eligibility(booking_reference: str) -> str:
    """Check if a flight booking is eligible for a refund"""
    # ... checks refund eligibility
```
This tool helps the refund specialist check if a booking can be refunded.

## Step 3: Creating Specialist Agents 👨‍💼👩‍💼
```python
booking_agent = Agent(
    name="Booking Agent",
    instructions="You are a specialized booking agent for a travel company...",
    tools=[get_available_flights]
)

refund_agent = Agent(
    name="Refund Agent",
    instructions="You are a specialized refund agent for a travel company...",
    tools=[check_refund_eligibility]
)
```
These create two specialist AIs:
- A booking agent who knows how to find flights
- A refund agent who knows how to handle refunds

## Step 4: Creating the Receptionist (Triage Agent) 🧑‍💼
```python
triage_agent = Agent(
    name="Travel Assistant",
    instructions="""
    You are a helpful travel assistant that can help with various travel-related questions.
    
    If the user asks about booking flights or needs help with a new reservation,
    hand off the conversation to the Booking Agent.
    
    If the user asks about refunds, cancellations, or reimbursements,
    hand off the conversation to the Refund Agent.
    """,
    handoffs=[booking_agent, refund_agent]
)
```
This creates a receptionist AI that:
- Listens to all customer questions first
- Decides which specialist can best help
- Hands off the conversation to that specialist

## Step 5: Running the Program with Different Questions 🏃‍♂️
```python
async def main():
    # Example conversations
    booking_query = "I need to book a flight from New York to Los Angeles next week"
    refund_query = "I need to cancel my flight and get a refund. My booking reference is ABC123"
    general_query = "What's the weather like in Paris this time of year?"
    
    # Run the triage agent with each query
    response = await runner.run(triage_agent, booking_query)
    response = await runner.run(triage_agent, refund_query)
    response = await runner.run(triage_agent, general_query)
```
This tests the system with different questions:
1. A booking question (should go to the booking agent)
2. A refund question (should go to the refund agent)
3. A general question (triage agent handles it directly)

## Final Summary 📌
✅ We created specialist agents for booking and refunds
✅ We gave each specialist the tools they need
✅ We created a triage agent that directs questions to specialists
✅ We tested the system with different types of questions

## Try It Yourself! 🚀
1. Install the required packages:
   ```
   uv add openai-agents dotenv
   ```
2. Create a `.env` file with your API key
3. Run the program:
   ```
   uv run basichandsoff.py
   ```
4. Try asking different travel-related questions!

## What You'll Learn 🧠
- How to create a system of cooperating agents
- How to set up handoffs between agents
- How to create specialist agents with specific tools
- How to track which agent handled a request

Happy coding! 🎉 