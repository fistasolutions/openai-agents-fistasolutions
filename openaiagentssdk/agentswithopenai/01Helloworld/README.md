# 🌟 Hello World AI Assistant

## What This Code Does (Big Picture)
Imagine having a robot friend who can write poetry! This code creates a simple AI assistant using Claude (a smart AI) and asks it to write a haiku poem about recursion in programming.

Now, let's go step by step!

## Step 1: Setting Up the Magic Key 🗝️
```python
from agentswithopenai import Agent, Runner
from dotenv import load_dotenv
import os

load_dotenv()
```
The AI assistant needs a magic key (API key) to work properly.

This code finds the magic key hidden in a secret file (.env) and unlocks it.

## Step 2: Creating Your AI Assistant 🤖
```python
agent = Agent(
    name="Assistant", 
    instructions="You are a helpful assistant", 
    model="claude-3-5-sonnet-20240620"  # Using Claude model
)
```
This creates your AI friend and:
- Gives it a name: "Assistant"
- Tells it how to behave: "Be helpful"
- Sets which AI brain to use: Claude 3.5 Sonnet

## Step 3: Asking the AI to Write a Haiku ✍️
```python
result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
```
This line:
- Sends your question to the AI
- Waits for it to think and create a haiku
- Stores the answer in a variable called `result`

## Step 4: Showing the AI's Answer 📝
```python
print(result.final_output)
```
This displays the haiku that the AI wrote for you!

## Final Summary 📌
✅ We created an AI assistant using Claude
✅ We gave it instructions to be helpful
✅ We asked it to write a haiku about recursion
✅ We displayed the haiku it created

## Try It Yourself! 🚀
1. Install the required packages:
   ```
   uv add openai-agents dotenv
   ```
2. Create a `.env` file with your API key
3. Run the program:
   ```
   uv run helloworld.py
   ```
4. Try changing the question to ask for different haikus or other creative writing!

## What You'll Learn 🧠
- How to create a basic AI agent
- How to give it instructions
- How to ask it questions
- How to get its response

Happy coding! 🎉
