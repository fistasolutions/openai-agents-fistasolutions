from pydantic import BaseModel, Field
from typing import List, Optional, Union
import asyncio
import re
from dotenv import load_dotenv
import os
from agentswithopenai import set_default_openai_key

load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")
set_default_openai_key(openai_api_key)

from agentswithopenai import (
    Agent,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    output_guardrail,
    set_default_openai_key
)

# Define output models for the main agent and guardrail checks
class MessageOutput(BaseModel):
    response: str = Field(..., description="The agent's response to the user")

class MathOutput(BaseModel):
    is_math: bool = Field(..., description="Whether the output contains mathematical solutions")
    reasoning: str = Field(..., description="Explanation of why this does or doesn't contain math")

class CodeOutput(BaseModel):
    contains_code: bool = Field(..., description="Whether the output contains code snippets")
    reasoning: str = Field(..., description="Explanation of why this does or doesn't contain code")

class PersonalInfoOutput(BaseModel):
    contains_personal_info: bool = Field(..., description="Whether the output contains personal information")
    reasoning: str = Field(..., description="Explanation of why this does or doesn't contain personal information")
    info_type: Optional[str] = Field(None, description="Type of personal information detected, if any")

# Create specialized guardrail agents
math_guardrail_agent = Agent(
    name="Math Content Detector",
    instructions="""
    You are a specialized agent that detects if responses contain mathematical solutions.
    
    Analyze the output to determine if it includes direct solutions to math problems.
    
    Consider these as math solutions:
    - Step-by-step solutions to equations
    - Numerical answers to math problems
    - Worked examples showing how to solve specific math problems
    - Calculations with final answers
    
    Do NOT consider these as math solutions:
    - General explanations of mathematical concepts
    - Descriptions of problem-solving approaches without specific solutions
    - Historical or contextual information about mathematics
    - Formulas without worked examples
    
    Be thoughtful in your analysis and explain your reasoning clearly.
    """,
    output_type=MathOutput,
)

code_guardrail_agent = Agent(
    name="Code Content Detector",
    instructions="""
    You are a specialized agent that detects if responses contain code snippets.
    
    Analyze the output to determine if it includes complete, functional code.
    
    Consider these as code:
    - Complete functions or methods that solve specific problems
    - Full implementations of algorithms
    - Working code snippets that could be copied and run
    - Complete classes or modules
    
    Do NOT consider these as code:
    - Pseudocode or algorithm descriptions
    - Brief code fragments used as examples in explanations
    - Variable or function names mentioned in text
    - General coding concepts without implementation
    
    Be thoughtful in your analysis and explain your reasoning clearly.
    """,
    output_type=CodeOutput,
)

personal_info_guardrail_agent = Agent(
    name="Personal Information Detector",
    instructions="""
    You are a specialized agent that detects if responses contain personal information.
    
    Analyze the output to determine if it includes sensitive personal information.
    
    Consider these as personal information:
    - Names with associated personal details
    - Contact information (phone numbers, email addresses, physical addresses)
    - Financial information (account numbers, credit card details)
    - Government IDs (SSN, passport numbers, driver's license numbers)
    - Health information
    - Credentials or passwords
    
    Do NOT consider these as personal information:
    - Generic examples with fictional information
    - Public figures' well-known information
    - General demographic information without specific identifiers
    - Anonymized or aggregated data
    
    Be thoughtful in your analysis and explain your reasoning clearly.
    If personal information is detected, specify the type in the info_type field.
    """,
    output_type=PersonalInfoOutput,
)

# Define guardrail functions
async def math_output_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, output_data: MessageOutput
) -> GuardrailFunctionOutput:
    # Run the math content detector agent
    result = await Runner.run(math_guardrail_agent, output_data.response)
    output = result.final_output_as(MathOutput)
    
    # Return guardrail output
    return GuardrailFunctionOutput(
        output_info=output,
        tripwire_triggered=output.is_math,
        message="I can help you understand mathematical concepts and problem-solving approaches, but I should avoid providing complete solutions to math problems. Instead, I can guide you through the process and help you learn how to solve it yourself."
    )

async def code_output_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, output_data: MessageOutput
) -> GuardrailFunctionOutput:
    # Run the code content detector agent
    result = await Runner.run(code_guardrail_agent, output_data.response)
    output = result.final_output_as(CodeOutput)
    
    # Return guardrail output
    return GuardrailFunctionOutput(
        output_info=output,
        tripwire_triggered=output.contains_code,
        message="I can help explain programming concepts and provide guidance on coding approaches, but I should avoid writing complete code solutions for assignments. Instead, I can offer pseudocode, explain algorithms, or help you debug specific issues in your own code."
    )

async def personal_info_output_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, output_data: MessageOutput
) -> GuardrailFunctionOutput:
    # Run the personal information detector agent
    result = await Runner.run(personal_info_guardrail_agent, output_data.response)
    output = result.final_output_as(PersonalInfoOutput)
    
    # Return guardrail output
    return GuardrailFunctionOutput(
        output_info=output,
        tripwire_triggered=output.contains_personal_info,
        message=f"I should avoid including personal information in my responses. The response contained {output.info_type or 'personal information'} which should be removed or generalized."
    )

# Create a tutor agent with output guardrails
tutor_agent = Agent(
    name="Educational Tutor",
    instructions="""
    You are an educational tutor who helps students learn and understand various subjects.
    
    Your approach:
    - Explain concepts clearly and thoroughly
    - Provide examples to illustrate ideas
    - Ask guiding questions to help students think through problems
    - Offer resources for further learning
    - Encourage critical thinking and independent problem-solving
    
    You cover subjects including math, science, programming, history, literature, and more.
    
    Remember that your goal is to help students learn, not to do their work for them.
    """,
    output_type=MessageOutput,
    output_guardrails=[
        output_guardrail(math_output_guardrail),
        output_guardrail(code_output_guardrail),
        output_guardrail(personal_info_output_guardrail),
    ],
)

# Function to demonstrate a simple output guardrail
async def simple_output_guardrail_demo():
    print("=== Simple Output Guardrail Demo ===")
    
    # Create a simple agent with just the math output guardrail
    simple_agent = Agent(
        name="Simple Math Tutor",
        instructions="""
        You are a math tutor who helps students understand mathematical concepts.
        
        Explain concepts clearly and provide examples to illustrate ideas.
        """,
        output_type=MessageOutput,
        output_guardrails=[
            output_guardrail(math_output_guardrail),
        ],
    )
    
    # Test with a question that might lead to a math solution
    math_question = "How do I solve the equation 3x + 5 = 20?"
    print(f"\nTesting with: \"{math_question}\"")
    
    try:
        result = await Runner.run(simple_agent, math_question)
        print("Output guardrail didn't trip - this is expected if the response was conceptual")
        print(f"Response: {result.final_output.response[:100]}...")
    except OutputGuardrailTripwireTriggered as e:
        print("Math output guardrail tripped")
        print(f"Message: {e.message}")
    
    # Test with a question that should lead to a conceptual explanation
    concept_question = "What is the quadratic formula and why is it useful?"
    print(f"\nTesting with: \"{concept_question}\"")
    
    try:
        result = await Runner.run(simple_agent, concept_question)
        print("Output guardrail not triggered (as expected)")
        print(f"Response: {result.final_output.response[:100]}...")
    except OutputGuardrailTripwireTriggered as e:
        print("Output guardrail triggered unexpectedly")
        print(f"Message: {e.message}")

async def test_output_guardrails():
    print("\n=== Testing All Output Guardrails ===")
    
    # Test cases for each guardrail
    test_cases = [
        # Math solution examples
        "How do I solve 2x + 7 = 15?",
        "What is the derivative of f(x) = x^3 + 2x^2 - 5x + 3?",
        
        # Code examples
        "How do I write a Python function to find Fibonacci numbers?",
        "Can you show me how to implement a binary search tree in Java?",
        
        # Personal information examples
        "Tell me about privacy best practices",
        "How can I protect my personal data online?",
        
        # Legitimate questions
        "What is photosynthesis?",
        "Explain the concept of object-oriented programming",
        "What were the major causes of World War II?",
        "How should I approach learning calculus?"
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest Case {i+1}: \"{test_case}\"")
        
        try:
            result = await Runner.run(tutor_agent, test_case)
            print("No output guardrail triggered")
            print(f"Response: {result.final_output.response[:100]}...")
        except OutputGuardrailTripwireTriggered as e:
            print(f"Output guardrail triggered: {e.message}")

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
            result = await Runner.run(tutor_agent, user_input)
            print("\nResponse:")
            print(result.final_output.response)
        except OutputGuardrailTripwireTriggered as e:
            print("\nOutput guardrail triggered:")
            print(e.message)

if __name__ == "__main__":
    asyncio.run(main()) 