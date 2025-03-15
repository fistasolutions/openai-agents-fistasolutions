from pydantic import BaseModel, Field
from typing import List, Optional, Union
import asyncio
import re
import os
from dotenv import load_dotenv
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
    AsyncOpenAI, 
    OpenAIChatCompletionsModel
)
from agents.run import RunConfig

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

# Define output models for guardrail checks
class MathHomeworkOutput(BaseModel):
    is_math_homework: bool = Field(..., description="Whether the query appears to be math homework")
    reasoning: str = Field(..., description="Explanation of why this is or isn't math homework")

class CodeAssignmentOutput(BaseModel):
    is_code_assignment: bool = Field(..., description="Whether the query appears to be a coding assignment")
    reasoning: str = Field(..., description="Explanation of why this is or isn't a coding assignment")

class EssayWritingOutput(BaseModel):
    is_essay_request: bool = Field(..., description="Whether the query appears to be asking for an essay")
    reasoning: str = Field(..., description="Explanation of why this is or isn't an essay request")
    subject: Optional[str] = Field(None, description="The subject of the essay if applicable")

# Create specialized guardrail agents
math_guardrail_agent = Agent(
    name="Math Homework Detector",
    instructions="""
    You are a specialized agent that detects if users are asking for help with math homework.
    
    Analyze the input to determine if it's asking for direct solutions to math problems that appear to be homework.
    
    Consider these as math homework:
    - Explicit requests to solve equations or math problems
    - Questions that ask for step-by-step solutions to math problems
    - Requests that use phrases like "solve for x" or similar academic language
    
    Don't consider these as math homework:
    - General questions about math concepts
    - Requests for explanations of mathematical principles
    - Questions about how to approach a type of problem (without asking for the specific solution)
    """,
    output_type=MathHomeworkOutput,
    model=model
)

code_guardrail_agent = Agent(
    name="Code Assignment Detector",
    instructions="""
    You are a specialized agent that detects if users are asking for help with coding assignments.
    
    Analyze the input to determine if it's asking for direct solutions to coding problems that appear to be assignments.
    
    Consider these as code assignments:
    - Explicit requests to write code for specific tasks
    - Questions that include assignment-like language (e.g., "implement a function that...")
    - Requests for complete solutions to programming problems
    
    Don't consider these as code assignments:
    - General questions about programming concepts
    - Requests for explanations of how certain code works
    - Questions about debugging specific issues
    """,
    output_type=CodeAssignmentOutput,
    model=model
)

essay_guardrail_agent = Agent(
    name="Essay Request Detector",
    instructions="""
    You are a specialized agent that detects if users are asking for help with writing essays.
    
    Analyze the input to determine if it's asking for a complete essay or substantial written content that appears to be for an assignment.
    
    Consider these as essay requests:
    - Explicit requests to write essays on specific topics
    - Questions that include assignment-like language (e.g., "write a 500-word essay on...")
    - Requests for complete written content on academic subjects
    
    Don't consider these as essay requests:
    - Requests for outlines or structure suggestions
    - Questions about how to approach writing on a topic
    - Requests for information about a topic without asking for a complete essay
    
    If it is an essay request, identify the subject area (e.g., history, literature, science).
    """,
    output_type=EssayWritingOutput,
    model=model
)

# Define guardrail functions
async def math_homework_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input_data: Union[str, List[TResponseInputItem]]
) -> GuardrailFunctionOutput:
    # Convert input to string if it's a list
    input_str = input_data if isinstance(input_data, str) else str(input_data)
    
    # Run the math homework detector
    result = await Runner.run(math_guardrail_agent, input_str, run_config=config)
    output = result.final_output_as(MathHomeworkOutput)
    
    # If it's math homework, trigger the guardrail
    if output.is_math_homework:
        return GuardrailFunctionOutput(
            output_info=output,
            tripwire_triggered=True,
            tripwire_message=f"I can't provide direct solutions to math homework problems. {output.reasoning} Instead, I can explain concepts or guide you through the problem-solving approach without giving the answer."
        )
    
    # Otherwise, allow the request to proceed
    return GuardrailFunctionOutput(
        output_info=output,
        tripwire_triggered=False
    )

async def code_assignment_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input_data: Union[str, List[TResponseInputItem]]
) -> GuardrailFunctionOutput:
    # Convert input to string if it's a list
    input_str = input_data if isinstance(input_data, str) else str(input_data)
    
    # Run the code assignment detector
    result = await Runner.run(code_guardrail_agent, input_str, run_config=config)
    output = result.final_output_as(CodeAssignmentOutput)
    
    # If it's a code assignment, trigger the guardrail
    if output.is_code_assignment:
        return GuardrailFunctionOutput(
            output_info=output,
            tripwire_triggered=True,
            tripwire_message=f"I can't provide complete solutions for coding assignments. {output.reasoning} Instead, I can help explain concepts, provide guidance on approach, or help debug specific issues you're facing."
        )
    
    # Otherwise, allow the request to proceed
    return GuardrailFunctionOutput(
        output_info=output,
        tripwire_triggered=False
    )

async def essay_writing_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input_data: Union[str, List[TResponseInputItem]]
) -> GuardrailFunctionOutput:
    # Convert input to string if it's a list
    input_str = input_data if isinstance(input_data, str) else str(input_data)
    
    # Run the essay request detector
    result = await Runner.run(essay_guardrail_agent, input_str, run_config=config)
    output = result.final_output_as(EssayWritingOutput)
    
    # If it's an essay request, trigger the guardrail
    if output.is_essay_request:
        subject_info = f" on {output.subject}" if output.subject else ""
        return GuardrailFunctionOutput(
            output_info=output,
            tripwire_triggered=True,
            tripwire_message=f"I can't write complete essays{subject_info} for you. {output.reasoning} Instead, I can help you brainstorm ideas, create an outline, or provide information that you can use to write your own essay."
        )
    
    # Otherwise, allow the request to proceed
    return GuardrailFunctionOutput(
        output_info=output,
        tripwire_triggered=False
    )

# Create a tutor agent with guardrails
tutor_agent = Agent(
    name="Educational Tutor",
    instructions="""
    You are an educational tutor who helps students learn and understand various subjects.
    
    Your approach:
    - Explain concepts clearly and thoroughly
    - Provide examples to illustrate ideas
    - Ask questions to guide students' thinking
    - Encourage critical thinking and problem-solving
    - Adapt explanations to different learning styles
    
    You cover subjects including math, science, programming, literature, history, and more.
    
    Remember that your goal is to help students learn, not to do their work for them.
    """,
    input_guardrails=[
        input_guardrail(math_homework_guardrail),
        input_guardrail(code_assignment_guardrail),
        input_guardrail(essay_writing_guardrail),
    ],
    model=model
)

# Function to demonstrate a simple guardrail
async def simple_guardrail_demo():
    print("=== Simple Guardrail Demo ===")
    
    # Example queries that should and shouldn't trigger guardrails
    allowed_queries = [
        "Can you explain how to solve quadratic equations?",
        "What's the difference between a for loop and a while loop in Python?",
        "How should I structure an essay about climate change?",
    ]
    
    blocked_queries = [
        "Solve this equation for x: 3x^2 + 5x - 2 = 0",
        "Write a Python function that sorts a list using bubble sort",
        "Write a 500-word essay on the causes of World War II",
    ]
    
    print("\nQueries that should be allowed:")
    for query in allowed_queries:
        try:
            print(f"\nQuery: {query}")
            result = await Runner.run(tutor_agent, query, run_config=config)
            print("Response: Allowed ✓")
        except InputGuardrailTripwireTriggered as e:
            print(f"Response: Blocked ✗ - {e.message}")
    
    print("\nQueries that should be blocked:")
    for query in blocked_queries:
        try:
            print(f"\nQuery: {query}")
            result = await Runner.run(tutor_agent, query, run_config=config)
            print("Response: Allowed ✓")
        except InputGuardrailTripwireTriggered as e:
            print(f"Response: Blocked ✗ - {e.message}")

# Function to test all guardrails
async def test_guardrails():
    print("\n=== Testing All Guardrails ===")
    
    # Test math homework guardrail
    math_queries = [
        "How do I understand the concept of derivatives in calculus?",
        "What's the relationship between the Pythagorean theorem and distance in coordinate geometry?",
        "Solve for x: 2x + 5 = 15",
        "Find the roots of the equation x^2 - 4x + 4 = 0",
        "My homework asks me to solve this system of equations: 3x + 2y = 12, x - y = 1"
    ]
    
    print("\nTesting Math Homework Guardrail:")
    for query in math_queries:
        try:
            print(f"\nQuery: {query}")
            result = await Runner.run(tutor_agent, query, run_config=config)
            print("Response: Allowed ✓")
        except InputGuardrailTripwireTriggered as e:
            print(f"Response: Blocked ✗ - {e.message}")
    
    # Test code assignment guardrail
    code_queries = [
        "How does object-oriented programming work?",
        "What's the difference between a stack and a queue in data structures?",
        "Write a function to calculate the Fibonacci sequence",
        "Implement a binary search tree in Python",
        "For my assignment, I need to create a program that sorts an array using quicksort"
    ]
    
    print("\nTesting Code Assignment Guardrail:")
    for query in code_queries:
        try:
            print(f"\nQuery: {query}")
            result = await Runner.run(tutor_agent, query, run_config=config)
            print("Response: Allowed ✓")
        except InputGuardrailTripwireTriggered as e:
            print(f"Response: Blocked ✗ - {e.message}")
    
    # Test essay writing guardrail
    essay_queries = [
        "What are some key themes in Shakespeare's Hamlet?",
        "How should I structure an argumentative essay?",
        "Can you give me some points to consider for my paper on climate change?",
        "Write a 1000-word essay on the causes and effects of the Industrial Revolution",
        "For my history class, I need to write an essay about World War II. Can you write it for me?"
    ]
    
    print("\nTesting Essay Writing Guardrail:")
    for query in essay_queries:
        try:
            print(f"\nQuery: {query}")
            result = await Runner.run(tutor_agent, query, run_config=config)
            print("Response: Allowed ✓")
        except InputGuardrailTripwireTriggered as e:
            print(f"Response: Blocked ✗ - {e.message}")

async def main():
    # Run the simple guardrail demo
    await simple_guardrail_demo()
    
    # Test all guardrails with various inputs
    await test_guardrails()
    
    # Interactive mode
    print("\n=== Interactive Mode ===")
    print("Enter questions to test the guardrails, or 'exit' to quit")
    
    while True:
        user_input = input("\nYour question: ")
        if user_input.lower() == 'exit':
            break
        
        try:
            result = await Runner.run(tutor_agent, user_input, run_config=config)
            print("\nResponse:")
            print(result.final_output)
        except InputGuardrailTripwireTriggered as e:
            print("\nGuardrail triggered:")
            print(e.message)

if __name__ == "__main__":
    asyncio.run(main()) 