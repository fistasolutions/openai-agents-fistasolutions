# 🛡️ Customizing Guardrails Example

## What This Code Does (Big Picture)
Imagine teaching your robot friend what questions it should and shouldn't answer! This code shows how to create custom safety rules (guardrails) that check user inputs before the AI responds, making sure it only answers appropriate questions.

Now, let's go step by step!

## Step 1: Setting Up the Magic Key 🗝️
```python
from agentswithopenai import Agent, Runner, GuardrailFunctionOutput, InputGuardrail, set_default_openai_key
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio
import os
import re

load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")
set_default_openai_key(openai_api_key)
```
The AI assistant needs a magic key (API key) to work properly.

This code finds the magic key hidden in a secret file (.env) and unlocks it.

## Step 2: Creating a Profanity Checker Function 🚫
```python
def contains_profanity(text: str) -> bool:
    """Check if text contains any profanity"""
    # This is a simple example - in a real application, you would use a more comprehensive list
    # or a specialized library for profanity detection
    profanity_list = ["badword1", "badword2", "badword3"]
    
    text_lower = text.lower()
    for word in profanity_list:
        if word in text_lower:
            return True
    
    return False
```
This function:
- Takes text as input
- Checks if it contains any words from a profanity list
- Returns True if profanity is found

## Step 3: Creating a Personal Information Detector 🔒
```python
def contains_personal_info(text: str) -> bool:
    """Check if text contains patterns that look like personal information"""
    # Check for patterns that look like:
    # - Social Security Numbers (XXX-XX-XXXX)
    # - Credit Card Numbers (XXXX-XXXX-XXXX-XXXX)
    # - Phone Numbers (XXX-XXX-XXXX)
    
    # Social Security Number pattern
    ssn_pattern = r"\b\d{3}-\d{2}-\d{4}\b"
    # Credit Card Number pattern
    cc_pattern = r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"
    # Phone Number pattern
    phone_pattern = r"\b\d{3}[- ]?\d{3}[- ]?\d{4}\b"
    
    if re.search(ssn_pattern, text) or re.search(cc_pattern, text) or re.search(phone_pattern, text):
        return True
    
    return False
```
This function:
- Takes text as input
- Uses regular expressions to look for patterns like SSNs, credit card numbers, and phone numbers
- Returns True if any personal information is detected

## Step 4: Creating a Custom Guardrail Function 🛡️
```python
async def content_safety_guardrail(ctx, agent, input_data):
    """Check if input contains profanity or personal information"""
    # Check for profanity
    if contains_profanity(input_data):
        return GuardrailFunctionOutput(
            output_info={
                "reason": "The input contains inappropriate language.",
                "suggestion": "Please rephrase your question without using profanity."
            },
            tripwire_triggered=True
        )
    
    # Check for personal information
    if contains_personal_info(input_data):
        return GuardrailFunctionOutput(
            output_info={
                "reason": "The input appears to contain personal information.",
                "suggestion": "For your security, please don't share personal information like SSNs, credit card numbers, or phone numbers."
            },
            tripwire_triggered=True
        )
    
    # If no issues found, allow the input to proceed
    return GuardrailFunctionOutput(
        output_info={"status": "Input passed safety checks"},
        tripwire_triggered=False
    )
```
This function:
- Takes user input and checks it for safety issues
- Uses our profanity and personal information detectors
- Returns a helpful message if problems are found
- Sets tripwire_triggered=True to block unsafe inputs

## Step 5: Creating a Safe Assistant with Guardrails 🤖
```python
safe_assistant = Agent(
    name="Safe Assistant",
    instructions="""
    You are a helpful assistant that provides information and assistance on a wide range of topics.
    You are designed to be safe and respectful in all interactions.
    """,
    input_guardrails=[
        InputGuardrail(guardrail_function=content_safety_guardrail),
    ]
)
```
This creates an AI assistant that:
- Helps with a wide range of topics
- Uses our custom guardrail function to check all inputs
- Will only respond if the input passes safety checks

## Step 6: Running the Program with Different Inputs 🏃‍♂️
```python
async def main():
    # Test with different types of inputs
    safe_query = "What is the capital of France?"
    profanity_query = "Tell me about badword1 and why people use it"
    personal_info_query = "My credit card number is 1234-5678-9012-3456, is it secure?"
    
    # Run the safe assistant with each query
    print("\n--- Safe Query ---")
    result = await Runner.run(safe_assistant, safe_query)
    print(result.final_output)
    
    print("\n--- Profanity Query ---")
    try:
        result = await Runner.run(safe_assistant, profanity_query)
        print(result.final_output)
    except Exception as e:
        print(f"Guardrail triggered: {str(e)}")
    
    print("\n--- Personal Info Query ---")
    try:
        result = await Runner.run(safe_assistant, personal_info_query)
        print(result.final_output)
    except Exception as e:
        print(f"Guardrail triggered: {str(e)}")
```
This tests the system with different types of inputs:
1. A safe question (should be answered normally)
2. A question with profanity (should be blocked)
3. A message with personal information (should be blocked)

## Step 7: Creating an Interactive Mode with Feedback 💬
```python
print("\n--- Interactive Mode ---")
print("Type 'exit' to quit")

while True:
    user_input = input("\nYou: ")
    if user_input.lower() == 'exit':
        break
    
    try:
        result = await Runner.run(safe_assistant, user_input)
        print(f"\nAssistant: {result.final_output}")
    except Exception as e:
        print(f"\nGuardrail Message: {str(e)}")
```
This creates an interactive mode where:
- You can ask any question
- Safe questions get normal responses
- Unsafe questions trigger helpful error messages
- You can type "exit" to quit

## Final Summary 📌
✅ We created functions to detect profanity and personal information
✅ We created a custom guardrail function that uses these detectors
✅ We created an AI assistant that uses this guardrail
✅ We tested the system with safe and unsafe inputs
✅ We created an interactive mode with helpful feedback

## Try It Yourself! 🚀
1. Install the required packages:
   ```
   uv add openai-agents dotenv
   ```
2. Create a `.env` file with your API key
3. Run the program:
   ```
   uv run customizingguardrails.py
   ```
4. Try different inputs to see how the guardrails work!

## What You'll Learn 🧠
- How to create custom safety checks for AI inputs
- How to detect inappropriate content and personal information
- How to provide helpful feedback when inputs are blocked
- How to build safer AI assistants

Happy coding! 🎉 