# 🤖 Agents As Tools Example

## What This Code Does (Big Picture)
Imagine having a team of robot specialists where one robot can ask another for help with specific tasks! This code shows how to create a system where a manager AI can delegate tasks to specialist AIs that are experts in different areas.

Now, let's go step by step!

## Step 1: Setting Up the Magic Key 🗝️
```python
from agentswithopenai import Agent, Runner, function_tool, set_default_openai_key
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")
set_default_openai_key(openai_api_key)
```
The AI assistants need a magic key (API key) to work properly.

This code finds the magic key hidden in a secret file (.env) and unlocks it.

## Step 2: Creating Specialist Agents 👨‍🔬👩‍🏫👨‍💻
```python
math_specialist = Agent(
    name="Math Specialist",
    instructions="""
    You are a mathematics expert. Solve math problems step by step,
    showing your work and explaining each step clearly.
    Use proper mathematical notation when helpful.
    Double-check your calculations for accuracy.
    """,
)

writing_specialist = Agent(
    name="Writing Specialist",
    instructions="""
    You are a writing expert. Help improve text by enhancing clarity,
    fixing grammar issues, and making the writing more engaging.
    Explain your changes so the user understands how to improve their writing.
    Consider the audience and purpose of the text when making suggestions.
    """,
)

research_specialist = Agent(
    name="Research Specialist",
    instructions="""
    You are a research expert. Find and summarize information on various topics,
    providing well-organized and accurate information.
    Cite sources when possible and distinguish between facts and opinions.
    Present information in a structured, easy-to-understand format.
    """,
)
```
This creates three specialist AIs:
- A math expert who solves problems step by step
- A writing expert who improves text and explains changes
- A research expert who finds and summarizes information

## Step 3: Creating Tools That Use These Specialists 🛠️
```python
@function_tool
async def solve_math_problem(problem: str) -> str:
    """Solve a mathematical problem using the Math Specialist"""
    result = await Runner.run(math_specialist, problem)
    return result.final_output

@function_tool
async def improve_writing(text: str) -> str:
    """Improve writing using the Writing Specialist"""
    result = await Runner.run(writing_specialist, text)
    return result.final_output

@function_tool
async def research_question(question: str) -> str:
    """Research a topic using the Research Specialist"""
    result = await Runner.run(research_specialist, question)
    return result.final_output
```
These tools:
- Take a problem, text, or question as input
- Send it to the appropriate specialist agent
- Return the specialist's response

## Step 4: Creating a Manager Agent 🧑‍💼
```python
manager_agent = Agent(
    name="Task Manager",
    instructions="""
    You are a helpful assistant that can handle various tasks by delegating to specialists.
    - For math problems, use the solve_math_problem tool
    - For writing improvement, use the improve_writing tool
    - For research questions, use the research_question tool
    
    Determine which specialist would be best for each user request and use the appropriate tool.
    If a request doesn't clearly fit one specialist, ask clarifying questions.
    """,
    tools=[solve_math_problem, improve_writing, research_question],
)
```
This creates a manager AI that:
- Understands different types of requests
- Decides which specialist to use for each request
- Delegates tasks to the appropriate specialist
- Asks for clarification if needed

## Step 5: Running the Program with Different Requests 🏃‍♂️
```python
async def main():
    # Example requests for different specialists
    math_query = "Solve the quadratic equation: 2x² + 5x - 3 = 0"
    writing_query = "Can you improve this sentence: 'The cat sat on the mat and it was happy.'"
    research_query = "What are the main causes of climate change?"
    
    # Run the manager agent with each query
    print("\n--- Math Problem ---")
    result = await Runner.run(manager_agent, math_query)
    print(result.final_output)
    
    print("\n--- Writing Improvement ---")
    result = await Runner.run(manager_agent, writing_query)
    print(result.final_output)
    
    print("\n--- Research Question ---")
    result = await Runner.run(manager_agent, research_query)
    print(result.final_output)
```
This tests the system with different types of requests:
1. A math problem (should go to the math specialist)
2. A writing improvement request (should go to the writing specialist)
3. A research question (should go to the research specialist)

## Step 6: Creating an Interactive Mode 💬
```python
print("\n--- Interactive Mode ---")
print("Type 'exit' to quit")

while True:
    user_input = input("\nYou: ")
    if user_input.lower() == 'exit':
        break
    
    result = await Runner.run(manager_agent, user_input)
    print(f"\nManager: {result.final_output}")
```
This creates an interactive mode where:
- You can ask any type of question
- The manager decides which specialist to use
- You get responses from the appropriate specialist
- You can type "exit" to quit

## Final Summary 📌
✅ We created specialist agents for math, writing, and research
✅ We created tools that delegate tasks to these specialists
✅ We created a manager agent that decides which specialist to use
✅ We tested the system with different types of requests
✅ We created an interactive mode for asking any question

## Try It Yourself! 🚀
1. Install the required packages:
   ```
   uv add openai-agents dotenv
   ```
2. Create a `.env` file with your API key
3. Run the program:
   ```
   uv run agentsastools.py
   ```
4. Try asking different types of questions to see which specialist handles them!

## What You'll Learn 🧠
- How to create a hierarchy of agents
- How to use agents as tools for other agents
- How to delegate tasks based on specialization
- How to build complex agent systems

Happy coding! 🎉 