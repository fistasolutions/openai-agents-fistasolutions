import os
from dotenv import load_dotenv
from agents import Agent, Runner, trace, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
import asyncio
import time
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

# Create specialized agents for different tasks
joke_agent = Agent(
    name="Joke Generator",
    instructions="""
    You are a creative joke generator. Your job is to create original, funny jokes based on the topic provided.
    
    Guidelines for your jokes:
    - Keep jokes appropriate for all audiences
    - Avoid offensive or controversial content
    - Use wordplay, puns, and clever twists
    - Be concise and to the point
    - Create jokes that are easy to understand
    
    When asked for a joke, provide just the joke itself without additional commentary.
    """,
    model=model
)

rating_agent = Agent(
    name="Joke Evaluator",
    instructions="""
    You are a professional joke evaluator. Your job is to rate jokes on a scale of 1-10 and provide brief feedback.
    
    When rating jokes, consider:
    - Originality and creativity
    - Cleverness of wordplay or punchline
    - Overall humor value
    - Appropriateness for general audiences
    - Clarity and delivery
    
    Provide your rating in this format:
    Rating: [1-10]
    Feedback: [Brief explanation of your rating]
    """,
    model=model
)

improvement_agent = Agent(
    name="Joke Improver",
    instructions="""
    You are a joke improvement specialist. Your job is to take an existing joke and make it funnier.
    
    Ways to improve jokes:
    - Tighten the wording for better delivery
    - Enhance the punchline
    - Add a clever twist
    - Improve the setup to better lead to the punchline
    - Make the joke more relatable
    
    Provide the improved joke and a brief explanation of what you changed and why.
    """,
    model=model
)

# Function to demonstrate a simple trace
async def simple_trace_demo():
    print("=== Simple Trace Demo ===")
    
    with trace(workflow_name="Simple Workflow"):
        print("Starting simple workflow...")
        
        # Simulate some work
        print("Step 1: Initializing...")
        await asyncio.sleep(0.5)
        
        print("Step 2: Processing...")
        await asyncio.sleep(0.5)
        
        print("Step 3: Finalizing...")
        await asyncio.sleep(0.5)
        
        print("Simple workflow completed")

# Function to demonstrate nested traces
async def nested_trace_demo():
    print("\n=== Nested Trace Demo ===")
    
    with trace(workflow_name="Main Process"):
        print("Starting main process...")
        
        with trace(workflow_name="Initialization"):
            print("Initializing system...")
            await asyncio.sleep(0.5)
            print("System initialized")
        
        with trace(workflow_name="Data Processing"):
            print("Processing data...")
            
            with trace(workflow_name="Validation"):
                print("Validating input data...")
                await asyncio.sleep(0.3)
                print("Data validated")
            
            with trace(workflow_name="Transformation"):
                print("Transforming data...")
                await asyncio.sleep(0.3)
                print("Data transformed")
            
            print("Data processing complete")
        
        with trace(workflow_name="Finalization"):
            print("Finalizing results...")
            await asyncio.sleep(0.5)
            print("Results finalized")
        
        print("Main process completed")

# Function to run the joke workshop with traces
async def joke_workshop(topic):
    print(f"\n=== Joke Workshop: {topic} ===")
    
    with trace(workflow_name=f"Joke Workshop - {topic}"):
        print(f"Starting joke workshop for topic: {topic}")
        
        with trace(workflow_name="Joke Generation"):
            print(f"Generating joke about {topic}...")
            result = await Runner.run(joke_agent, f"Create a funny joke about {topic}", run_config=config)
            joke = result.final_output
            print(f"Generated joke: {joke}")
        
        with trace(workflow_name="Joke Evaluation"):
            print("Evaluating joke...")
            result = await Runner.run(rating_agent, f"Rate this joke: {joke}", run_config=config)
            rating = result.final_output
            print(f"Evaluation: {rating}")
        
        with trace(workflow_name="Joke Improvement"):
            print("Improving joke based on feedback...")
            result = await Runner.run(improvement_agent, f"Improve this joke: {joke}\nBased on this feedback: {rating}", run_config=config)
            improved_joke = result.final_output
            print(f"Improved joke: {improved_joke}")
        
        print("Joke workshop completed")
        return {
            "original_joke": joke,
            "rating": rating,
            "improved_joke": improved_joke
        }

# Function to demonstrate a customer interaction with traces
async def customer_interaction_demo():
    print("\n=== Customer Interaction Demo ===")
    
    with trace(workflow_name="Customer Interaction"):
        print("Customer interaction started")
        
        with trace(workflow_name="Greeting"):
            print("Greeting the customer...")
            time.sleep(0.5)
            print("Customer greeted successfully")
        
        with trace(workflow_name="Joke Request"):
            print("Customer requested a joke...")
            
            with trace(workflow_name="Joke Generation"):
                result = await Runner.run(joke_agent, "Tell me a joke about customer service", run_config=config)
                joke = result.final_output
                print(f"Generated joke: {joke}")
            
            with trace(workflow_name="Joke Delivery"):
                print("Delivering joke to customer...")
                time.sleep(0.5)
                print("Joke delivered successfully")
        
        with trace(workflow_name="Customer Feedback"):
            print("Getting customer feedback...")
            time.sleep(0.5)
            feedback = random.choice(["loved it", "thought it was okay", "didn't laugh"])
            print(f"Customer {feedback}")
        
        print("Customer interaction completed")

async def main():
    # Demonstrate a simple trace
    await simple_trace_demo()
    
    # Demonstrate nested traces
    await nested_trace_demo()
    
    # Run the full joke workshop with traces
    topics = ["cats", "technology", "cooking"]
    
    for topic in topics:
        await joke_workshop(topic)
    
    # Interactive mode
    print("\n=== Interactive Joke Workshop ===")
    print("Enter a topic for a joke workshop, or 'exit' to quit")
    
    while True:
        topic = input("\nJoke topic: ")
        if topic.lower() == 'exit':
            break
        
        await joke_workshop(topic)

if __name__ == "__main__":
    asyncio.run(main()) 