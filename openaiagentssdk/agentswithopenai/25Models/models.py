from agentswithopenai import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_default_openai_key, handoff
import asyncio
from dotenv import load_dotenv
import os
import time
from agentswithopenai import set_default_openai_key

load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")
set_default_openai_key(openai_api_key)

# Create agents with different models
spanish_agent = Agent(
    name="Spanish Agent",
    instructions="""
    You are a helpful assistant who only speaks Spanish.
    
    Always respond in Spanish, regardless of the language of the query.
    Be friendly, helpful, and conversational in your responses.
    If you're asked to speak in another language, politely explain in Spanish
    that you can only communicate in Spanish.
    """,
    model="gpt-3.5-turbo",  # Using a less expensive model for simple translation
)

french_agent = Agent(
    name="French Agent",
    instructions="""
    You are a helpful assistant who only speaks French.
    
    Always respond in French, regardless of the language of the query.
    Be friendly, helpful, and conversational in your responses.
    If you're asked to speak in another language, politely explain in French
    that you can only communicate in French.
    """,
    model="gpt-3.5-turbo",  # Using a less expensive model for simple translation
)

german_agent = Agent(
    name="German Agent",
    instructions="""
    You are a helpful assistant who only speaks German.
    
    Always respond in German, regardless of the language of the query.
    Be friendly, helpful, and conversational in your responses.
    If you're asked to speak in another language, politely explain in German
    that you can only communicate in German.
    """,
    model="gpt-3.5-turbo",  # Using a less expensive model for simple translation
)

# Create a triage agent that can hand off to language-specific agents
triage_agent = Agent(
    name="Language Triage Agent",
    instructions="""
    You are a language triage assistant. Your job is to:
    
    1. Identify the language the user wants to communicate in
    2. Direct them to the appropriate language-specific agent
    3. If they want Spanish, hand off to the Spanish Agent
    4. If they want French, hand off to the French Agent
    5. If they want German, hand off to the German Agent
    6. For any other language or general queries, respond in English
    
    Be friendly and helpful in your responses.
    """,
    handoffs=[
        spanish_agent,
        french_agent,
        german_agent,
    ],
    model="gpt-4o",  # Using a more capable model for the triage agent
)

# Create a custom model configuration
custom_model_config = {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 0.95,
    "frequency_penalty": 0.5,
    "presence_penalty": 0.5,
}

# Create an agent with a custom model configuration
creative_agent = Agent(
    name="Creative Writer",
    instructions="""
    You are a creative writing assistant. Your job is to:
    
    1. Help users with creative writing tasks
    2. Generate story ideas, characters, and plot elements
    3. Provide feedback on writing samples
    4. Suggest improvements to prose and dialogue
    5. Offer writing tips and techniques
    
    Be imaginative, encouraging, and helpful in your responses.
    """,
    model=custom_model_config,  # Using a custom model configuration
)

# Create an agent with a custom model class
async def create_custom_model_agent():
    # Create a custom OpenAI client
    client = AsyncOpenAI(
        api_key=openai_api_key,
        timeout=60.0,  # Custom timeout
    )
    
    # Create a custom model instance
    custom_model = OpenAIChatCompletionsModel(
        client=client,
        model="gpt-4o",
        temperature=0.2,  # Lower temperature for more deterministic outputs
        max_tokens=2000,  # Higher token limit for longer responses
        top_p=0.9,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    
    # Create an agent with the custom model
    technical_agent = Agent(
        name="Technical Documentation Writer",
        instructions="""
        You are a technical documentation writer. Your job is to:
        
        1. Create clear, concise technical documentation
        2. Explain complex concepts in simple terms
        3. Format information for readability
        4. Use consistent terminology
        5. Provide examples where helpful
        
        Be precise, thorough, and user-focused in your responses.
        """,
        model=custom_model,  # Using the custom model instance
    )
    
    return technical_agent

# Function to demonstrate model performance
async def compare_model_performance():
    print("=== Model Performance Comparison ===")
    
    # Create a simple agent with GPT-3.5 Turbo
    gpt35_agent = Agent(
        name="GPT-3.5 Agent",
        instructions="You are a helpful assistant. Provide concise answers to questions.",
        model="gpt-3.5-turbo",
    )
    
    # Create a simple agent with GPT-4o
    gpt4o_agent = Agent(
        name="GPT-4o Agent",
        instructions="You are a helpful assistant. Provide concise answers to questions.",
        model="gpt-4o",
    )
    
    # Test query
    test_query = "Explain quantum computing in simple terms."
    
    # Test GPT-3.5 Turbo
    print("\nTesting GPT-3.5 Turbo...")
    start_time = time.time()
    result = await Runner.run(gpt35_agent, test_query)
    gpt35_time = time.time() - start_time
    gpt35_response = result.final_output
    
    # Test GPT-4o
    print("Testing GPT-4o...")
    start_time = time.time()
    result = await Runner.run(gpt4o_agent, test_query)
    gpt4o_time = time.time() - start_time
    gpt4o_response = result.final_output
    
    # Print results
    print("\nGPT-3.5 Turbo:")
    print(f"Response time: {gpt35_time:.2f} seconds")
    print(f"Response: {gpt35_response[:150]}...")
    
    print("\nGPT-4o:")
    print(f"Response time: {gpt4o_time:.2f} seconds")
    print(f"Response: {gpt4o_response[:150]}...")
    
    print("\nComparison:")
    print(f"GPT-4o was {(gpt35_time/gpt4o_time if gpt4o_time > 0 else 0):.2f}x faster than GPT-3.5 Turbo" if gpt35_time > gpt4o_time else f"GPT-3.5 Turbo was {(gpt4o_time/gpt35_time if gpt35_time > 0 else 0):.2f}x faster than GPT-4o")

async def main():
    # Create the custom model agent
    technical_agent = await create_custom_model_agent()
    
    # Compare model performance
    await compare_model_performance()
    
    # Test language-specific agents
    print("\n=== Language-Specific Agents ===")
    
    # Test Spanish agent
    print("\nTesting Spanish Agent...")
    result = await Runner.run(spanish_agent, "Tell me about the weather today.")
    print(f"Response: {result.final_output}")
    
    # Test French agent
    print("\nTesting French Agent...")
    result = await Runner.run(french_agent, "Tell me about the weather today.")
    print(f"Response: {result.final_output}")
    
    # Test German agent
    print("\nTesting German Agent...")
    result = await Runner.run(german_agent, "Tell me about the weather today.")
    print(f"Response: {result.final_output}")
    
    # Test triage agent
    print("\n=== Language Triage Agent ===")
    
    # Test Spanish request
    print("\nTesting Spanish request...")
    result = await Runner.run(triage_agent, "I want to practice Spanish. Can you help me?")
    print(f"Response: {result.final_output}")
    
    # Test French request
    print("\nTesting French request...")
    result = await Runner.run(triage_agent, "I need assistance in French please.")
    print(f"Response: {result.final_output}")
    
    # Test general request
    print("\nTesting general request...")
    result = await Runner.run(triage_agent, "What's the capital of Japan?")
    print(f"Response: {result.final_output}")
    
    # Test creative agent with custom model config
    print("\n=== Creative Agent (Custom Model Config) ===")
    result = await Runner.run(creative_agent, "Give me an idea for a short story about time travel.")
    print(f"Response: {result.final_output}")
    
    # Test technical agent with custom model instance
    print("\n=== Technical Agent (Custom Model Instance) ===")
    result = await Runner.run(technical_agent, "Write documentation for a function that calculates fibonacci numbers.")
    print(f"Response: {result.final_output}")
    
    # Interactive mode
    print("\n=== Interactive Mode ===")
    print("Choose an agent to interact with:")
    print("1. Language Triage Agent")
    print("2. Creative Writer (Custom Config)")
    print("3. Technical Documentation Writer (Custom Instance)")
    print("Type 'exit' to quit")
    
    while True:
        agent_choice = input("\nSelect agent (1-3): ")
        if agent_choice.lower() == 'exit':
            break
        
        try:
            agent_num = int(agent_choice)
            if agent_num == 1:
                selected_agent = triage_agent
                print("Using Language Triage Agent")
            elif agent_num == 2:
                selected_agent = creative_agent
                print("Using Creative Writer")
            elif agent_num == 3:
                selected_agent = technical_agent
                print("Using Technical Documentation Writer")
            else:
                print("Invalid choice. Please select 1-3.")
                continue
        except ValueError:
            print("Invalid input. Please enter a number 1-3.")
            continue
        
        user_input = input("Your query: ")
        if user_input.lower() == 'exit':
            break
        
        print("Processing...")
        result = await Runner.run(selected_agent, input=user_input)
        print("\nResponse:")
        print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main()) 