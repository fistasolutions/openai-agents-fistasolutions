import os
from dotenv import load_dotenv
from agents import Agent, handoff, RunContextWrapper, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
import asyncio
from typing import Any, Dict, Optional

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

# Define custom handoff callbacks
def on_handoff_to_sales(ctx: RunContextWrapper[None]):
    print("\n[SYSTEM] Handoff to Sales Agent initiated")
    print("[SYSTEM] Logging customer information for sales follow-up")
    print("[SYSTEM] Preparing sales materials based on customer inquiry")

def on_handoff_to_support(ctx: RunContextWrapper[None]):
    print("\n[SYSTEM] Handoff to Support Agent initiated")
    print("[SYSTEM] Retrieving customer support history")
    print("[SYSTEM] Preparing troubleshooting resources")

def on_handoff_to_specialist(ctx: RunContextWrapper[None]):
    print("\n[SYSTEM] Handoff to Product Specialist initiated")
    print("[SYSTEM] Loading product documentation and specifications")
    print("[SYSTEM] Checking inventory and availability")

# Create specialized agents
sales_agent = Agent(
    name="Sales Agent",
    instructions="""
    You are a specialized sales agent. Your role is to:
    
    1. Help customers find the right products for their needs
    2. Provide pricing information and available discounts
    3. Explain product features and benefits
    4. Assist with placing orders
    5. Answer questions about shipping and delivery
    
    Be enthusiastic, helpful, and knowledgeable about our product offerings.
    Focus on understanding customer needs and recommending appropriate solutions.
    """,
    model=model
)

support_agent = Agent(
    name="Support Agent",
    instructions="""
    You are a specialized technical support agent. Your role is to:
    
    1. Help customers troubleshoot issues with their products
    2. Provide step-by-step guidance for resolving problems
    3. Explain how to use product features
    4. Assist with software updates and installations
    5. Document issues for further follow-up if needed
    
    Be patient, clear, and thorough in your explanations.
    Focus on resolving the customer's issue efficiently and effectively.
    """,
    model=model
)

product_specialist = Agent(
    name="Product Specialist",
    instructions="""
    You are a specialized product expert. Your role is to:
    
    1. Provide in-depth information about specific products
    2. Compare different product models and their features
    3. Explain technical specifications and compatibility
    4. Offer advice on product accessories and add-ons
    5. Share best practices for product use and maintenance
    
    Be detailed, accurate, and passionate about our products.
    Focus on helping customers understand the full capabilities of our offerings.
    """,
    model=model
)

# Create custom handoff objects with callbacks and overrides
sales_handoff = handoff(
    agent=sales_agent,
    on_handoff=on_handoff_to_sales,
    tool_name_override="transfer_to_sales_team",
    tool_description_override="Transfer the customer to the sales team for product information, pricing, and purchasing assistance.",
)

support_handoff = handoff(
    agent=support_agent,
    on_handoff=on_handoff_to_support,
    tool_name_override="connect_with_technical_support",
    tool_description_override="Connect the customer with technical support for troubleshooting and problem resolution.",
)

specialist_handoff = handoff(
    agent=product_specialist,
    on_handoff=on_handoff_to_specialist,
    tool_name_override="arrange_product_specialist_consultation",
    tool_description_override="Arrange a consultation with a product specialist for detailed product information and expert advice.",
)

# Create a main agent that can hand off to specialized agents
main_agent = Agent(
    name="Customer Service Agent",
    instructions="""
    You are the primary customer service agent. Your role is to:
    
    1. Greet customers and understand their initial needs
    2. Handle general inquiries and simple questions
    3. Direct customers to the appropriate specialized agent when needed:
       - Sales Team: For product selection, pricing, and purchasing
       - Technical Support: For troubleshooting and product issues
       - Product Specialist: For detailed product information and expert advice
    
    Before transferring a customer, briefly explain why you're connecting them with a specialist
    and what they can expect from the handoff.
    """,
    handoffs=[
        sales_handoff,
        support_handoff,
        specialist_handoff,
    ],
    model=model
)

async def main():
    # Example customer inquiries for different scenarios
    sales_inquiry = "I'm interested in buying a new laptop for video editing. What do you recommend?"
    support_inquiry = "My printer keeps showing an error code E-04. How can I fix this?"
    specialist_inquiry = "Can you tell me about the differences between your premium camera models?"
    general_inquiry = "What are your store hours this weekend?"
    
    # Test the main agent with different inquiries
    print("=== Sales Inquiry Example ===")
    print(f"Customer: {sales_inquiry}")
    
    result = await Runner.run(main_agent, input=sales_inquiry, run_config=config)
    print("\nResponse:")
    print(result.final_output)
    
    print("\n=== Support Inquiry Example ===")
    print(f"Customer: {support_inquiry}")
    
    result = await Runner.run(main_agent, input=support_inquiry, run_config=config)
    print("\nResponse:")
    print(result.final_output)
    
    print("\n=== Specialist Inquiry Example ===")
    print(f"Customer: {specialist_inquiry}")
    
    result = await Runner.run(main_agent, input=specialist_inquiry, run_config=config)
    print("\nResponse:")
    print(result.final_output)
    
    print("\n=== General Inquiry Example ===")
    print(f"Customer: {general_inquiry}")
    
    result = await Runner.run(main_agent, input=general_inquiry, run_config=config)
    print("\nResponse:")
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
        print("\nResponse:")
        print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main()) 