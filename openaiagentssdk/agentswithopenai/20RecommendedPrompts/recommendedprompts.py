from agentswithopenai import Agent, Runner, set_default_openai_key
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")
set_default_openai_key(openai_api_key)

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
    - Use clear, step-by-step instructions
    - Avoid technical jargon unless necessary
    - Confirm understanding at each troubleshooting step
    - Be patient with users of all technical skill levels
    - Focus on resolving the immediate issue first
    
    Our software works on Windows 10+, macOS 10.15+, and major Linux distributions.
    """,
)

# Create a standard agent without the recommended prompt prefix
standard_agent = Agent(
    name="General Assistant",
    instructions="""
    You are a helpful assistant for a software company. Your responsibilities include:
    
    1. Answering general questions about the company and its products
    2. Providing basic information about features and capabilities
    3. Directing customers to the appropriate specialized teams
    4. Helping with account management and general inquiries
    5. Offering resources like documentation and tutorials
    
    When helping customers:
    - Be friendly and approachable
    - Provide accurate information
    - Acknowledge when you don't know something
    - Maintain a positive and helpful attitude
    - Focus on customer satisfaction
    """,
)

async def main():
    
    # Example queries for each agent
    billing_query = "I was charged twice for my subscription this month. Can I get a refund?"
    support_query = "I'm getting an error message when I try to install your software on my Mac."
    general_query = "What kind of products does your company offer?"
    
    # Test the billing agent with the recommended prompt prefix
    print("=== Billing Agent (with recommended prompt) ===")
    print(f"Query: {billing_query}")
    
    result = await Runner.run(billing_agent, input=billing_query)
    print("\nResponse:")
    print(result.final_output)
    
    # Test the support agent with the recommended prompt prefix
    print("\n=== Technical Support Agent (with recommended prompt) ===")
    print(f"Query: {support_query}")
    
    result = await Runner.run(support_agent, input=support_query)
    print("\nResponse:")
    print(result.final_output)
    
    # Test the standard agent without the recommended prompt prefix
    print("\n=== Standard Agent (without recommended prompt) ===")
    print(f"Query: {general_query}")
    
    result = await Runner.run(standard_agent, input=general_query)
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
        result = await Runner.run(selected_agent, input=user_query)
        print("\nResponse:")
        print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main()) 