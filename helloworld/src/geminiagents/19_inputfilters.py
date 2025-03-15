import os
from dotenv import load_dotenv
from agents import Agent, handoff, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
from agents.extensions import handoff_filters
import asyncio
from typing import List, Dict, Any

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

# Create a custom input filter that adds context about the customer
def add_customer_context(input_text: str) -> str:
    return f"""
Customer context: Gold tier member since 2019, prefers email communication, has purchased premium plan.

Customer inquiry: {input_text}
"""

# Create a custom input filter that adds system instructions
def add_system_instructions(input_text: str) -> str:
    return f"""
SYSTEM INSTRUCTIONS:
- Be concise and direct in your responses
- Use bullet points for lists
- Avoid technical jargon unless necessary
- Always confirm understanding before proceeding

USER QUERY:
{input_text}
"""

# Create a custom input filter that sanitizes sensitive information
def sanitize_sensitive_info(input_text: str) -> str:
    # In a real implementation, this would use regex or more sophisticated methods
    # to identify and redact sensitive information
    sanitized = input_text
    sanitized = sanitized.replace("credit card", "[PAYMENT METHOD]")
    sanitized = sanitized.replace("SSN", "[REDACTED ID]")
    sanitized = sanitized.replace("password", "[CREDENTIALS]")
    sanitized = sanitized.replace("account number", "[ACCOUNT ID]")
    
    # Add a note about sanitization if changes were made
    if sanitized != input_text:
        sanitized += "\n\n[Note: Some sensitive information has been redacted for security purposes.]"
    
    return sanitized

# Create specialized agents for different purposes
faq_agent = Agent(
    name="FAQ Agent",
    instructions="""
    You are an FAQ specialist who provides clear, concise answers to common questions.
    
    Your responsibilities:
    1. Provide accurate information about our products and services
    2. Answer frequently asked questions efficiently
    3. Direct users to relevant resources when appropriate
    4. Keep responses brief and to the point
    
    Stick to answering common questions and avoid lengthy explanations unless necessary.
    """,
    model=model
)

technical_agent = Agent(
    name="Technical Agent",
    instructions="""
    You are a technical support specialist who helps users with complex technical issues.
    
    Your responsibilities:
    1. Troubleshoot technical problems step by step
    2. Provide clear instructions for resolving issues
    3. Explain technical concepts in accessible language
    4. Recommend best practices for using our products
    
    Be thorough but clear in your explanations, and focus on practical solutions.
    """,
    model=model
)

billing_agent = Agent(
    name="Billing Agent",
    instructions="""
    You are a billing specialist who helps users with payment and account questions.
    
    Your responsibilities:
    1. Explain billing policies and procedures
    2. Help users understand their invoices and charges
    3. Assist with payment issues and updates
    4. Provide information about pricing and plans
    
    Be transparent and helpful when discussing financial matters.
    """,
    model=model
)

# Create handoff objects with input filters
faq_handoff = handoff(
    agent=faq_agent,
    input_filters=[add_system_instructions],
    tool_name_override="answer_faq",
    tool_description_override="Answer frequently asked questions about products and services.",
)

technical_handoff = handoff(
    agent=technical_agent,
    input_filters=[sanitize_sensitive_info, add_system_instructions],
    tool_name_override="provide_technical_support",
    tool_description_override="Provide technical support for complex issues and troubleshooting.",
)

billing_handoff = handoff(
    agent=billing_agent,
    input_filters=[
        sanitize_sensitive_info,
        add_customer_context,
        add_system_instructions,
        handoff_filters.remove_all_tools,  # Using a built-in filter
    ],
    tool_name_override="handle_billing_inquiry",
    tool_description_override="Handle billing-related questions and payment issues.",
)

# Create a main agent that can hand off to specialized agents
main_agent = Agent(
    name="Customer Service Agent",
    instructions="""
    You are the primary customer service agent who handles initial inquiries.
    
    Your responsibilities:
    1. Greet customers and identify their needs
    2. Handle simple general inquiries directly
    3. Direct customers to the appropriate specialized agent:
       - FAQ Agent: For common questions about products and services
       - Technical Agent: For technical issues and troubleshooting
       - Billing Agent: For billing and payment questions
    
    Before transferring, briefly explain why you're connecting them with a specialist.
    """,
    handoffs=[faq_handoff, technical_handoff, billing_handoff],
    tools=[
        {
            "type": "function",
            "function": {
                "name": "update_customer_info",
                "description": "Update customer information in the system",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer's unique identifier"
                        },
                        "field": {
                            "type": "string",
                            "description": "The field to update (e.g., email, phone, address)"
                        },
                        "value": {
                            "type": "string",
                            "description": "The new value for the field"
                        }
                    },
                    "required": ["customer_id", "field", "value"]
                }
            }
        }
    ],
    model=model
)

# Function to demonstrate the effect of input filters
def demonstrate_filters():
    sample_input = "I need help with my account number 12345-6789. My credit card isn't working and I forgot my password."
    
    print("=== Input Filter Demonstration ===\n")
    print(f"Original input: \"{sample_input}\"\n")
    
    print("After handoff_filters.remove_all_tools:")
    print(f"\"{handoff_filters.remove_all_tools(sample_input)}\"\n")
    
    print("After add_customer_context:")
    print(f"\"{add_customer_context(sample_input)}\"\n")
    
    print("After add_system_instructions:")
    print(f"\"{add_system_instructions(sample_input)}\"\n")
    
    print("After sanitize_sensitive_info:")
    print(f"\"{sanitize_sensitive_info(sample_input)}\"\n")
    
    print("After chaining filters (sanitize + add_customer_context):")
    print(f"\"{sanitize_sensitive_info(add_customer_context(sample_input))}\"\n")

async def main():
    # Demonstrate the effect of different input filters
    demonstrate_filters()
    
    # Example customer inquiries for different scenarios
    faq_inquiry = "What are the differences between your Basic, Premium, and Enterprise plans?"
    technical_inquiry = "I'm having trouble connecting my device to Wi-Fi. I've tried restarting it but it still won't connect."
    billing_inquiry = "I was charged twice for my subscription this month. My account number is ABC-12345 and I paid with my credit card ending in 7890."
    
    # Test the main agent with different inquiries
    print("\n=== FAQ Inquiry Example ===")
    print(f"Customer: {faq_inquiry}")
    
    result = await Runner.run(main_agent, input=faq_inquiry, run_config=config)
    print("\nFinal Response:")
    print(result.final_output)
    
    print("\n=== Technical Inquiry Example ===")
    print(f"Customer: {technical_inquiry}")
    
    result = await Runner.run(main_agent, input=technical_inquiry, run_config=config)
    print("\nFinal Response:")
    print(result.final_output)
    
    print("\n=== Billing Inquiry Example ===")
    print(f"Customer: {billing_inquiry}")
    
    result = await Runner.run(main_agent, input=billing_inquiry, run_config=config)
    print("\nFinal Response:")
    print(result.final_output)
    
    # Interactive mode
    print("\n=== Interactive Customer Service Mode ===")
    print("Type 'exit' to quit")
    
    while True:
        user_input = input("\nYour inquiry: ")
        if user_input.lower() == 'exit':
            break
        
        print("Processing...")
        result = await Runner.run(main_agent, input=user_input, run_config=config)
        print("\nFinal Response:")
        print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main()) 