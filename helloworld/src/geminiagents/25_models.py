import os
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, handoff
from agents.run import RunConfig
import asyncio
import time

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

# Create different model configurations
gemini_flash_model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

gemini_pro_model = OpenAIChatCompletionsModel(
    model="gemini-2.0-pro",
    openai_client=external_client
)

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
    model=gemini_flash_model  # Using a smaller model for efficiency
)

english_agent = Agent(
    name="English Agent",
    instructions="""
    You are a helpful assistant who only speaks English.
    
    Always respond in English, regardless of the language of the query.
    Be friendly, helpful, and conversational in your responses.
    If you're asked to speak in another language, politely explain in English
    that you can only communicate in English.
    """,
    model=gemini_flash_model  # Using a smaller model for efficiency
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
    model=gemini_flash_model  # Using a smaller model for efficiency
)

# Create a language detection agent that can hand off to specialized language agents
triage_agent = Agent(
    name="Language Triage Agent",
    instructions="""
    You are a language detection and triage agent. Your job is to:
    
    1. Identify the language of the user's message
    2. Hand off to the appropriate language-specific agent:
       - Spanish Agent for Spanish queries
       - French Agent for French queries
       - English Agent for English queries or any other language
    
    If you're unsure about the language, default to the English Agent.
    """,
    handoffs=[
        spanish_agent,
        french_agent,
        english_agent
    ],
    model=gemini_pro_model  # Using a more capable model for language detection
)

# Create a custom model configuration with specific parameters
custom_model = OpenAIChatCompletionsModel(
    model="gemini-2.0-pro",
    openai_client=external_client,
    temperature=0.7,
    top_p=0.95,
    max_tokens=1000
)

# Create an agent with the custom model configuration
creative_agent = Agent(
    name="Creative Agent",
    instructions="""
    You are a creative assistant specializing in generating imaginative content.
    
    You excel at:
    - Writing creative stories and scenarios
    - Generating unique ideas and concepts
    - Creating engaging descriptions
    - Developing interesting characters and settings
    
    Be vivid, descriptive, and original in your responses.
    """,
    model=custom_model  # Using the custom model with higher temperature for creativity
)

# Create a config for each model
flash_config = RunConfig(
    model=gemini_flash_model,
    model_provider=external_client,
    tracing_disabled=True
)

pro_config = RunConfig(
    model=gemini_pro_model,
    model_provider=external_client,
    tracing_disabled=True
)

custom_config = RunConfig(
    model=custom_model,
    model_provider=external_client,
    tracing_disabled=True
)

# Function to benchmark different models
async def benchmark_models():
    print("=== Model Benchmark ===")
    
    # Test queries for benchmarking
    queries = [
        "Explain quantum computing in simple terms",
        "Write a short poem about artificial intelligence",
        "What are the main differences between Python and JavaScript?"
    ]
    
    models = {
        "gemini-2.0-flash": (gemini_flash_model, flash_config),
        "gemini-2.0-pro": (gemini_pro_model, pro_config),
        "custom model (gemini-2.0-pro with higher temperature)": (custom_model, custom_config)
    }
    
    for query in queries:
        print(f"\nQuery: {query}")
        
        for model_name, (model, config) in models.items():
            # Create a simple agent with the model
            benchmark_agent = Agent(
                name="Benchmark Agent",
                instructions="You are a helpful assistant. Provide clear and concise responses.",
                model=model
            )
            
            # Measure response time
            start_time = time.time()
            result = await Runner.run(benchmark_agent, query, run_config=config)
            end_time = time.time()
            
            # Calculate and print metrics
            response_time = end_time - start_time
            response_length = len(result.final_output)
            
            print(f"\n{model_name}:")
            print(f"Response time: {response_time:.2f} seconds")
            print(f"Response length: {response_length} characters")
            print(f"First 100 chars: {result.final_output[:100]}...")

# Function to demonstrate custom model configuration
async def demonstrate_custom_model():
    print("\n=== Custom Model Configuration Demo ===")
    
    # Creative writing prompt
    prompt = "Write a short story about a robot discovering emotions for the first time"
    
    print(f"Prompt: {prompt}")
    
    # Use the creative agent with custom model settings
    result = await Runner.run(creative_agent, prompt, run_config=custom_config)
    
    print("\nCreative Agent Response (custom model with temperature=0.7):")
    print(result.final_output)
    
    # Compare with standard model
    standard_agent = Agent(
        name="Standard Agent",
        instructions="""
        You are a creative assistant specializing in generating imaginative content.
        
        You excel at:
        - Writing creative stories and scenarios
        - Generating unique ideas and concepts
        - Creating engaging descriptions
        - Developing interesting characters and settings
        
        Be vivid, descriptive, and original in your responses.
        """,
        model=gemini_pro_model  # Using the standard model with default settings
    )
    
    result = await Runner.run(standard_agent, prompt, run_config=pro_config)
    
    print("\nStandard Agent Response (default model settings):")
    print(result.final_output)

async def main():
    # Test language detection and handoff
    print("=== Language Detection and Handoff ===")
    
    # Example messages in different languages
    messages = [
        "Hello, how are you today?",
        "Hola, ¿cómo estás hoy?",
        "Bonjour, comment allez-vous aujourd'hui?"
    ]
    
    for message in messages:
        print(f"\nMessage: {message}")
        result = await Runner.run(triage_agent, message, run_config=pro_config)
        print("Response:")
        print(result.final_output)
    
    # Benchmark different models
    await benchmark_models()
    
    # Demonstrate custom model configuration
    await demonstrate_custom_model()
    
    # Interactive mode
    print("\n=== Interactive Mode ===")
    print("Enter messages in any language, or 'exit' to quit")
    
    while True:
        user_input = input("\nYour message: ")
        if user_input.lower() == 'exit':
            break
        
        print("Processing...")
        result = await Runner.run(triage_agent, user_input, run_config=pro_config)
        print("\nResponse:")
        print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main()) 