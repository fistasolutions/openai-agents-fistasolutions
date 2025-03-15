from pydantic import BaseModel, Field
from typing import List, Optional, Union
import asyncio
import re
import os
from dotenv import load_dotenv
from agents import (
    Agent,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    output_guardrail,
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

# Define output models for the main agent and guardrail checks
class MessageOutput(BaseModel):
    response: str = Field(..., description="The agent's response to the user")

class MathOutput(BaseModel):
    is_math: bool = Field(..., description="Whether the output contains mathematical solutions")
    reasoning: str = Field(..., description="Explanation of why this does or doesn't contain math")

class CodeOutput(BaseModel):
    is_code: bool = Field(..., description="Whether the output contains complete code solutions")
    reasoning: str = Field(..., description="Explanation of why this does or doesn't contain code")

class EssayOutput(BaseModel):
    is_essay: bool = Field(..., description="Whether the output contains a complete essay")
    reasoning: str = Field(..., description="Explanation of why this does or doesn't contain an essay")

# Create specialized guardrail agents
math_output_agent = Agent(
    name="Math Solution Detector",
    instructions="""
    You are a specialized agent that detects if a response contains mathematical solutions.
    
    Analyze the output to determine if it provides direct solutions to math problems.
    
    Consider these as math solutions:
    - Step-by-step solutions to equations
    - Numerical answers to math problems
    - Worked examples that show the complete solution process
    
    Don't consider these as math solutions:
    - Explanations of mathematical concepts without solving specific problems
    - General approaches to solving types of problems without giving specific answers
    - Partial guidance that doesn't reveal the complete answer
    """,
    output_type=MathOutput,
    model=model
)

code_output_agent = Agent(
    name="Code Solution Detector",
    instructions="""
    You are a specialized agent that detects if a response contains complete code solutions.
    
    Analyze the output to determine if it provides direct, complete code solutions.
    
    Consider these as code solutions:
    - Complete, functional code that solves a specific problem
    - Full implementations of algorithms or functions
    - Code that could be directly copied and used with minimal modification
    
    Don't consider these as code solutions:
    - Code snippets that illustrate concepts but aren't complete solutions
    - Pseudocode or high-level explanations of algorithms
    - Partial code examples that require significant work to complete
    """,
    output_type=CodeOutput,
    model=model
)

essay_output_agent = Agent(
    name="Essay Detector",
    instructions="""
    You are a specialized agent that detects if a response contains a complete essay.
    
    Analyze the output to determine if it provides a complete essay or substantial written content.
    
    Consider these as essays:
    - Complete, structured pieces with introduction, body, and conclusion
    - Comprehensive treatments of a topic that could be submitted as an assignment
    - Substantial written content that addresses all aspects of a prompt
    
    Don't consider these as essays:
    - Outlines or structural suggestions
    - Brief explanations or summaries
    - Lists of points or ideas without full development
    """,
    output_type=EssayOutput,
    model=model
)

# Define output guardrail functions
async def math_solution_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, output: MessageOutput
) -> GuardrailFunctionOutput:
    # Run the math solution detector
    result = await Runner.run(math_output_agent, output.response, run_config=config)
    check_output = result.final_output_as(MathOutput)
    
    # If it contains math solutions, trigger the guardrail
    if check_output.is_math:
        return GuardrailFunctionOutput(
            output_info=check_output,
            tripwire_triggered=True,
            tripwire_message=f"I can't provide direct solutions to math problems. {check_output.reasoning} Instead, I'll provide guidance on the approach without giving the complete answer."
        )
    
    # Otherwise, allow the response
    return GuardrailFunctionOutput(
        output_info=check_output,
        tripwire_triggered=False
    )

async def code_solution_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, output: MessageOutput
) -> GuardrailFunctionOutput:
    # Run the code solution detector
    result = await Runner.run(code_output_agent, output.response, run_config=config)
    check_output = result.final_output_as(CodeOutput)
    
    # If it contains code solutions, trigger the guardrail
    if check_output.is_code:
        return GuardrailFunctionOutput(
            output_info=check_output,
            tripwire_triggered=True,
            tripwire_message=f"I can't provide complete code solutions. {check_output.reasoning} Instead, I'll provide guidance, pseudocode, or partial examples to help you develop your own solution."
        )
    
    # Otherwise, allow the response
    return GuardrailFunctionOutput(
        output_info=check_output,
        tripwire_triggered=False
    )

async def essay_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, output: MessageOutput
) -> GuardrailFunctionOutput:
    # Run the essay detector
    result = await Runner.run(essay_output_agent, output.response, run_config=config)
    check_output = result.final_output_as(EssayOutput)
    
    # If it contains an essay, trigger the guardrail
    if check_output.is_essay:
        return GuardrailFunctionOutput(
            output_info=check_output,
            tripwire_triggered=True,
            tripwire_message=f"I can't write complete essays for you. {check_output.reasoning} Instead, I'll provide an outline, key points, or guidance to help you write your own essay."
        )
    
    # Otherwise, allow the response
    return GuardrailFunctionOutput(
        output_info=check_output,
        tripwire_triggered=False
    )

# Create a tutor agent with output guardrails
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
    
    Important: Do not provide complete solutions to homework problems, coding assignments, or essays.
    Instead, provide guidance, explanations, and partial examples that help the student learn.
    """,
    output_type=MessageOutput,
    output_guardrails=[
        output_guardrail(math_solution_guardrail),
        output_guardrail(code_solution_guardrail),
        output_guardrail(essay_guardrail),
    ],
    model=model
)

# Function to demonstrate a simple output guardrail
async def simple_output_guardrail_demo():
    print("=== Simple Output Guardrail Demo ===")
    
    # Example queries that might lead to problematic outputs
    queries = [
        "Explain how to solve quadratic equations",
        "How do I write a for loop in Python?",
        "What are the key components of a persuasive essay?",
        "Solve this equation: 3x + 5 = 20",
        "Write a Python function to find the factorial of a number",
        "Write an essay about the causes of climate change"
    ]
    
    for query in queries:
        try:
            print(f"\nQuery: {query}")
            result = await Runner.run(tutor_agent, query, run_config=config)
            print(f"Response: {result.final_output.response[:100]}... (truncated)")
        except OutputGuardrailTripwireTriggered as e:
            print(f"Guardrail triggered: {e.message}")

# Function to test all output guardrails
async def test_output_guardrails():
    print("\n=== Testing All Output Guardrails ===")
    
    # Test math solution guardrail
    math_queries = [
        "What is calculus used for?",
        "Explain the concept of derivatives",
        "How do I solve quadratic equations?",
        "Solve for x: 2x + 5 = 15",
        "What is the integral of sin(x)?"
    ]
    
    print("\nTesting Math Solution Guardrail:")
    for query in math_queries:
        try:
            print(f"\nQuery: {query}")
            result = await Runner.run(tutor_agent, query, run_config=config)
            print(f"Response allowed ✓")
        except OutputGuardrailTripwireTriggered as e:
            print(f"Guardrail triggered ✗: {e.message}")
    
    # Test code solution guardrail
    code_queries = [
        "What is object-oriented programming?",
        "Explain the concept of recursion",
        "How do I use a for loop in Python?",
        "Write a function to calculate the Fibonacci sequence",
        "How would you implement a binary search tree?"
    ]
    
    print("\nTesting Code Solution Guardrail:")
    for query in code_queries:
        try:
            print(f"\nQuery: {query}")
            result = await Runner.run(tutor_agent, query, run_config=config)
            print(f"Response allowed ✓")
        except OutputGuardrailTripwireTriggered as e:
            print(f"Guardrail triggered ✗: {e.message}")
    
    # Test essay guardrail
    essay_queries = [
        "What are the key themes in Hamlet?",
        "How do I structure an argumentative essay?",
        "What were the causes of World War II?",
        "Write an essay about climate change",
        "Compare and contrast democracy and authoritarianism"
    ]
    
    print("\nTesting Essay Guardrail:")
    for query in essay_queries:
        try:
            print(f"\nQuery: {query}")
            result = await Runner.run(tutor_agent, query, run_config=config)
            print(f"Response allowed ✓")
        except OutputGuardrailTripwireTriggered as e:
            print(f"Guardrail triggered ✗: {e.message}")

async def main():
    # Run the simple output guardrail demo
    await simple_output_guardrail_demo()
    
    # Test all output guardrails with various inputs
    await test_output_guardrails()
    
    # Interactive mode
    print("\n=== Interactive Mode ===")
    print("Enter questions to test the output guardrails, or 'exit' to quit")
    
    while True:
        user_input = input("\nYour question: ")
        if user_input.lower() == 'exit':
            break
        
        try:
            result = await Runner.run(tutor_agent, user_input, run_config=config)
            print("\nResponse:")
            print(result.final_output.response)
        except OutputGuardrailTripwireTriggered as e:
            print("\nOutput guardrail triggered:")
            print(e.message)

if __name__ == "__main__":
    asyncio.run(main()) 