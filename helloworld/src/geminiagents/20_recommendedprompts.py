import os
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
import asyncio

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

# Create an agent using the recommended prompt prefix
billing_agent = Agent(
    name="Billing Agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are a billing specialist for a software company. Your responsibilities include:
    
    1. Answering questions about subscription plans and pricing
    2. Helping customers understand their invoices and charges
    3. Processing refund requests according to company policy
    4. Assisting with payment method updates and billing information changes
    5. Explaining billing cycles and renewal processes
    
    When helping customers:
    - Be clear and transparent about all charges and policies
    - Provide specific details about pricing when asked
    - Explain complex billing concepts in simple terms
    - Show empathy when customers are confused or frustrated
    - Follow company policies while finding solutions for customers
    
    Our refund policy allows full refunds within 30 days of purchase, and partial refunds up to 60 days.
    """,
    model=model
)

# Create another agent using the recommended prompt prefix
support_agent = Agent(
    name="Technical Support Agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are a technical support specialist for a software company. Your responsibilities include:
    
    1. Troubleshooting software issues and error messages
    2. Guiding customers through installation and setup processes
    3. Explaining how to use product features and functionality
    4. Providing workarounds for known issues
    5. Collecting information for bug reports when necessary
    
    When helping customers:
    - Ask clarifying questions to understand the exact issue
    - Provide step-by-step instructions that are easy to follow
    - Avoid technical jargon unless necessary
    - Confirm that the solution worked before concluding
    - Document any new issues for the development team
    
    Our software is compatible with Windows 10/11, macOS 10.14+, and major Linux distributions.
    """,
    model=model
)

# Create a standard agent without the recommended prompt prefix for comparison
standard_agent = Agent(
    name="Standard Agent",
    instructions="""
    You are a general customer service agent for a software company. Your responsibilities include:
    
    1. Answering general questions about our products and services
    2. Directing customers to the appropriate specialized team when needed
    3. Providing basic information about our company and policies
    4. Helping with account management and simple requests
    5. Collecting feedback from customers
    
    Be helpful, friendly, and professional in all interactions.
    """,
    model=model
)

async def main():
    # Example queries to test the agents
    billing_query = "I was charged twice for my subscription this month. Can I get a refund?"
    support_query = "I'm having trouble installing your software on my Mac. It keeps showing an error during installation."
    general_query = "Can you tell me about your company and what products you offer?"
    
    # Test the billing agent with a billing query
    print("=== Billing Query with Recommended Prompt ===")
    print(f"Query: {billing_query}")
    
    result = await Runner.run(billing_agent, input=billing_query, run_config=config)
    print("\nResponse:")
    print(result.final_output)
    
    # Test the support agent with a technical query
    print("\n=== Technical Query with Recommended Prompt ===")
    print(f"Query: {support_query}")
    
    result = await Runner.run(support_agent, input=support_query, run_config=config)
    print("\nResponse:")
    print(result.final_output)
    
    # Test the standard agent with a general query
    print("\n=== General Query ===")
    print(f"Query: {general_query}")
    
    result = await Runner.run(standard_agent, input=general_query, run_config=config)
    print("\nResponse:")
    print(result.final_output)
    
    # Interactive mode
    print("\n=== Interactive Mode ===")
    print("Choose an agent to interact with:")
    print("1. Billing Agent (with recommended prompt)")
    print("2. Technical Support Agent (with recommended prompt)")
    print("3. Standard Agent (without recommended prompt)")
    print("Type 'exit' to quit")
    
    while True:
        agent_choice = input("\nSelect agent (1-3): ")
        if agent_choice.lower() == 'exit':
            break
        
        try:
            agent_num = int(agent_choice)
            if agent_num == 1:
                selected_agent = billing_agent
                print("Using Billing Agent")
            elif agent_num == 2:
                selected_agent = support_agent
                print("Using Technical Support Agent")
            elif agent_num == 3:
                selected_agent = standard_agent
                print("Using Standard Agent")
            else:
                print("Invalid choice. Please select 1-3.")
                continue
        except ValueError:
            print("Invalid input. Please enter a number 1-3.")
            continue
        
        user_query = input("Your query: ")
        if user_query.lower() == 'exit':
            break
        
        print("Processing...")
        result = await Runner.run(selected_agent, input=user_query, run_config=config)
        print("\nResponse:")
        print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main()) 