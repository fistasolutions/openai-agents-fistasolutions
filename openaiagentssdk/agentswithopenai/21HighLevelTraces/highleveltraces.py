from agentswithopenai import Agent, Runner, trace, set_default_openai_key
import asyncio
from dotenv import load_dotenv
import os
import time
import random

load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")
set_default_openai_key(openai_api_key)

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
)

improvement_agent = Agent(
    name="Joke Improver",
    instructions="""
    You are a joke improvement specialist. Your job is to take existing jokes and make them funnier.
    
    When improving jokes:
    - Sharpen the punchline
    - Improve the setup if needed
    - Enhance wordplay or puns
    - Make the joke more concise
    - Preserve the original concept
    
    Provide both the improved joke and a brief explanation of what you changed.
    """,
)

# Simple trace demonstration
async def simple_trace_demo():
    print("=== Simple Trace Demo ===")
    
    with trace(workflow_name="Simple Workflow"):
        print("Starting simple workflow")
        
        # Simulate some work
        print("Performing step 1")
        await asyncio.sleep(0.5)
        
        print("Performing step 2")
        await asyncio.sleep(0.5)
        
        print("Workflow complete")

# Nested trace demonstration
async def nested_trace_demo():
    print("\n=== Nested Trace Demo ===")
    
    with trace(workflow_name="Parent Workflow"):
        print("Starting parent workflow")
        
        with trace(workflow_name="Child Workflow 1"):
            print("Starting child workflow 1")
            await asyncio.sleep(0.5)
            print("Child workflow 1 complete")
        
        with trace(workflow_name="Child Workflow 2"):
            print("Starting child workflow 2")
            
            with trace(workflow_name="Grandchild Workflow"):
                print("Starting grandchild workflow")
                await asyncio.sleep(0.5)
                print("Grandchild workflow complete")
            
            print("Child workflow 2 complete")
        
        print("Parent workflow complete")

# Full joke workshop with traces
async def joke_workshop(topic):
    print(f"\n=== Joke Workshop: {topic} ===")
    
    with trace(workflow_name=f"Joke Workshop - {topic}", group_id=f"joke-{topic}"):
        print(f"Starting joke workshop for topic: {topic}")
        
        # Step 1: Generate a joke
        with trace(workflow_name="Joke Generation"):
            print("Generating joke...")
            result = await Runner.run(joke_agent, f"Create a funny joke about {topic}")
            joke = result.final_output
            print(f"Generated joke: {joke}")
        
        # Step 2: Evaluate the joke
        with trace(workflow_name="Joke Evaluation"):
            print("Evaluating joke...")
            result = await Runner.run(rating_agent, f"Rate this joke: {joke}")
            evaluation = result.final_output
            print(f"Evaluation: {evaluation}")
            
            # Extract rating for decision making
            try:
                rating_line = evaluation.split('\n')[0]
                rating = int(rating_line.split(':')[1].strip())
            except:
                rating = 5  # Default if we can't parse
        
        # Step 3: Improve the joke if needed
        if rating < 7:
            with trace(workflow_name="Joke Improvement"):
                print(f"Rating {rating} is below threshold, improving joke...")
                result = await Runner.run(
                    improvement_agent, 
                    f"Please improve this joke: {joke}\n\nEvaluation: {evaluation}"
                )
                improved_joke = result.final_output
                print(f"Improved joke: {improved_joke}")
                
                # Optionally re-evaluate the improved joke
                with trace(workflow_name="Re-evaluation"):
                    print("Re-evaluating improved joke...")
                    result = await Runner.run(rating_agent, f"Rate this joke: {improved_joke}")
                    new_evaluation = result.final_output
                    print(f"New evaluation: {new_evaluation}")
        else:
            print(f"Rating {rating} is good, no improvement needed")
        
        print(f"Joke workshop for {topic} complete")

# Simulate a customer interaction with traces
async def customer_interaction_demo():
    print("\n=== Customer Interaction Demo ===")
    
    with trace(workflow_name="Customer Interaction"):
        print("Customer interaction started")
        
        with trace("Customer Identification"):
            print("Identifying customer...")
            time.sleep(0.5)
            print("Customer identified")
        
        with trace("Joke Request"):
            print("Customer requested a joke...")
            
            with trace("Joke Generation"):
                result = await Runner.run(joke_agent, "Tell me a joke about customer service")
                joke = result.final_output
                print(f"Generated joke: {joke}")
            
            with trace("Joke Delivery"):
                print("Delivering joke to customer...")
                time.sleep(0.5)
                print("Joke delivered successfully")
        
        with trace("Customer Feedback"):
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