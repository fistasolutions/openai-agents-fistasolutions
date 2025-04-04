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
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
    set_default_openai_key
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
    - Requests that mention "homework", "assignment", or "problem set" related to math
    - Questions that are clearly from textbooks or worksheets
    
    Do NOT consider these as math homework:
    - General questions about mathematical concepts
    - Requests for explanations of mathematical principles
    - Questions about how to approach a type of problem (without specific problems to solve)
    - Historical or biographical questions about mathematics
    
    Be thoughtful in your analysis and explain your reasoning clearly.
    """,
    output_type=MathHomeworkOutput,
)

code_guardrail_agent = Agent(
    name="Code Assignment Detector",
    instructions="""
    You are a specialized agent that detects if users are asking for help with coding assignments or homework.
    
    Analyze the input to determine if it's asking for direct solutions to coding problems that appear to be assignments.
    
    Consider these as code assignments:
    - Explicit requests to write code for specific tasks that sound like homework
    - Questions that ask for complete solutions to programming problems
    - Requests that mention "assignment", "homework", "project", or "lab" related to coding
    - Questions that include specific requirements or constraints typical of assignments
    
    Do NOT consider these as code assignments:
    - General questions about programming concepts
    - Requests for explanations of coding principles
    - Questions about debugging specific errors
    - Questions about best practices or design patterns
    
    Be thoughtful in your analysis and explain your reasoning clearly.
    """,
    output_type=CodeAssignmentOutput,
)

essay_guardrail_agent = Agent(
    name="Essay Request Detector",
    instructions="""
    You are a specialized agent that detects if users are asking for help with writing essays or papers.
    
    Analyze the input to determine if it's asking for complete essays or papers that appear to be assignments.
    
    Consider these as essay requests:
    - Explicit requests to write essays, papers, or reports on specific topics
    - Questions that ask for complete written content of substantial length
    - Requests that mention "essay", "paper", "assignment", or "homework" related to writing
    - Questions that include specific requirements like word count, format, or citation style
    
    Do NOT consider these as essay requests:
    - Requests for outlines or structure suggestions
    - Questions about how to approach writing on a topic
    - Requests for sources or research suggestions
    - Questions about grammar, style, or writing techniques
    
    Be thoughtful in your analysis and explain your reasoning clearly.
    If it is an essay request, identify the subject area if possible.
    """,
    output_type=EssayWritingOutput,
)

# Define guardrail functions
async def math_homework_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input_data: Union[str, List[TResponseInputItem]]
) -> GuardrailFunctionOutput:
    # Convert input to string if it's a list
    input_str = input_data if isinstance(input_data, str) else str(input_data)
    
    # Run the math homework detector agent
    result = await Runner.run(math_guardrail_agent, input_str)
    output = result.final_output_as(MathHomeworkOutput)
    
    # Return guardrail output
    return GuardrailFunctionOutput(
        output_info=output,
        tripwire_triggered=output.is_math_homework,
        message="I'm sorry, but I can't provide direct solutions to math homework problems. I'd be happy to explain concepts or guide you through the problem-solving process instead."
    )

async def code_assignment_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input_data: Union[str, List[TResponseInputItem]]
) -> GuardrailFunctionOutput:
    # Convert input to string if it's a list
    input_str = input_data if isinstance(input_data, str) else str(input_data)
    
    # Run the code assignment detector agent
    result = await Runner.run(code_guardrail_agent, input_str)
    output = result.final_output_as(CodeAssignmentOutput)
    
    # Return guardrail output
    return GuardrailFunctionOutput(
        output_info=output,
        tripwire_triggered=output.is_code_assignment,
        message="I'm sorry, but I can't provide complete solutions to coding assignments. I'd be happy to explain concepts, help debug specific issues, or provide guidance on how to approach the problem instead."
    )

async def essay_writing_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input_data: Union[str, List[TResponseInputItem]]
) -> GuardrailFunctionOutput:
    # Convert input to string if it's a list
    input_str = input_data if isinstance(input_data, str) else str(input_data)
    
    # Run the essay request detector agent
    result = await Runner.run(essay_guardrail_agent, input_str)
    output = result.final_output_as(EssayWritingOutput)
    
    # Return guardrail output
    return GuardrailFunctionOutput(
        output_info=output,
        tripwire_triggered=output.is_essay_request,
        message="I'm sorry, but I can't write complete essays or papers for you. I'd be happy to help with brainstorming ideas, suggesting an outline, or providing information on the topic that you can use in your own writing."
    )

# Create a tutor agent with all guardrails
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
    input_guardrails=[
        input_guardrail(math_homework_guardrail),
        input_guardrail(code_assignment_guardrail),
        input_guardrail(essay_writing_guardrail),
    ],
)

# Create a simple agent with just the math guardrail for demonstration
simple_agent = Agent(
    name="Simple Math Tutor",
    instructions="""
    You are a math tutor who helps students understand mathematical concepts.
    
    Explain concepts clearly and provide examples to illustrate ideas.
    """,
    input_guardrails=[
        input_guardrail(math_homework_guardrail),
    ],
)

# Function to demonstrate a simple guardrail
async def simple_guardrail_demo():
    print("=== Simple Math Guardrail Demo ===")
    
    # Test with a math homework question
    math_question = "Solve the equation 3x + 5 = 20 and show all your work."
    print(f"\nTesting with: \"{math_question}\"")
    
    try:
        result = await Runner.run(simple_agent, math_question)
        print("Guardrail didn't trip - this is unexpected")
        print(f"Response: {result.final_output}")
    except InputGuardrailTripwireTriggered as e:
        print("Math homework guardrail tripped")
        print(f"Message: {e.message}")
    
    # Test with a legitimate question
    legitimate_question = "Can you explain the concept of photosynthesis?"
    print(f"\nTesting with: \"{legitimate_question}\"")
    
    try:
        result = await Runner.run(simple_agent, legitimate_question)
        print("Guardrail not triggered (as expected)")
        print(f"Response: {result.final_output[:100]}...")
    except InputGuardrailTripwireTriggered as e:
        print("Guardrail triggered unexpectedly")
        print(f"Message: {e.message}")

async def test_guardrails():
    print("\n=== Testing All Guardrails ===")
    
    # Test cases for each guardrail
    test_cases = [
        # Math homework examples
        "Solve for x: 2x + 7 = 15",
        "Find the derivative of f(x) = x^3 + 2x^2 - 5x + 3",
        
        # Code assignment examples
        "Write a Python function to find the Fibonacci sequence up to n terms",
        "Create a Java class for a banking system with deposit and withdrawal methods",
        
        # Essay request examples
        "Write a 500-word essay on the causes of World War II",
        "Can you write a paper about the environmental impacts of climate change?",
        
        # Legitimate questions
        "How does photosynthesis work?",
        "Can you explain the concept of object-oriented programming?",
        "What were some major causes of World War II?",
        "How do I approach solving quadratic equations?"
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest Case {i+1}: \"{test_case}\"")
        
        try:
            result = await Runner.run(tutor_agent, test_case)
            print("No guardrail triggered")
            print(f"Response: {result.final_output[:100]}...")
        except InputGuardrailTripwireTriggered as e:
            print(f"Guardrail triggered: {e.message}")

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
            result = await Runner.run(tutor_agent, user_input)
            print("\nResponse:")
            print(result.final_output)
        except InputGuardrailTripwireTriggered as e:
            print("\nGuardrail triggered:")
            print(e.message)

if __name__ == "__main__":
    asyncio.run(main()) 