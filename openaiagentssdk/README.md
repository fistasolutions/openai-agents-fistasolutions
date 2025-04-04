# 🤖 OpenAI Agents SDK Tutorial 🚀

![AI Agents Banner](https://via.placeholder.com/800x200?text=AI+Agents+SDK+Tutorial)

## 🌟 Welcome to the AI Playground!

Have you ever wanted to create your own AI assistant that can actually *do things* for you? That's exactly what the OpenAI Agents SDK helps you do! Think of it like building a robot friend who can talk to you AND help you complete tasks.

## 🧩 What is the OpenAI Agents SDK?

Imagine you have LEGO blocks to build cool stuff. The OpenAI Agents SDK gives you special AI LEGO blocks to build smart assistants that can:

- 💬 Talk with you like ChatGPT
- 🔧 Use tools to get things done (like searching the web or doing math)
- 🤝 Work with other AI assistants when they need help
- 🛡️ Follow safety rules you set

It's like giving superpowers to AI so it can help you in more useful ways!

## 🎮 Core Building Blocks

### 🧠 Agents
These are smart AI assistants powered by models like GPT-4. You give them instructions, and they follow them!

```python
agent = Agent(
    name="Math Helper", 
    instructions="You help solve math problems step by step"
)
```

### 🔄 Handoffs
When one AI needs another AI's help, it can pass the task over - just like teammates in a relay race!

```python
math_agent = Agent(name="Math Expert", instructions="You solve complex math problems")
writing_agent = Agent(name="Writing Expert", instructions="You write creative stories")

# The writing agent can hand off math problems to the math agent
```

### 🛑 Guardrails
These are safety fences that make sure your AI stays on the right track.

```python
# This guardrail makes sure the input isn't too long
guardrail = InputLengthGuardrail(max_length=1000)
```

### 🔍 Tracing
Like a detective's notebook, tracing helps you see exactly what your AI was thinking!

### 🛠️ Function Tools
These are special abilities you can give your AI - like checking the weather or searching for information.

```python
@tool
def calculate_area(length: float, width: float) -> float:
    """Calculate the area of a rectangle."""
    return length * width
```

## 🚀 Getting Started

### Installation

```bash
# Install the OpenAI Agents SDK
pip install openai-agents

# Set up your OpenAI API key
export OPENAI_API_KEY=sk-your_api_key_here
```

Don't have an API key? Ask a grown-up to help you get one from [OpenAI's website](https://platform.openai.com/api-keys).

## 📚 Examples in This Tutorial

### 1️⃣ Hello World! (`01Helloworld/helloworld.py`)
Your first AI agent that writes a haiku about recursion!

```python
from agentswithopenai import Agent, Runner

agent = Agent(name="Assistant", instructions="You are a helpful assistant")
result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)
```

### 2️⃣ Detail Agent (`02DetailAgent/detailagent.py`)
Create an AI with more specific instructions and personality.

### 3️⃣ Basic Configuration (`03_basicconfig.py`)
Learn how to set up and configure your agents for different tasks.

### 4️⃣ Custom Function Tools (`14CustomFunctionTools/customfunctiontools.py`)
Give your AI special abilities by creating custom tools!

### 5️⃣ Agents as Tools (`15AgentsAsTools/agentsastools.py`)
Make AIs that can call on other AIs for help - teamwork makes the dream work!

## 🏃‍♀️ How to Run the Examples

1. Make sure you've installed the SDK and set your API key
2. Navigate to the example folder you want to try
3. Run the Python file:

```bash
# For example, to run the Hello World example:
cd openaiagentssdk/agentswithopenai/01Helloworld
python helloworld.py
```

## 🎓 What You'll Learn

By the end of this tutorial, you'll know how to:
- Create your own AI assistants with different personalities
- Give your AI special tools to solve problems
- Make multiple AIs work together as a team
- Keep your AI safe and on-task with guardrails
- Debug and improve your AI with tracing

## 🌈 Ready to Start Your AI Adventure?

Jump into the examples folder and start with `01Helloworld`! Each example builds on the last one, teaching you new skills as you go.

Remember: The best way to learn is by experimenting! Try changing the instructions or adding new tools to see what happens.

---

```
  _____  _____   _______ _____  ______ _____ _____ ___    _     
 / ____|/ ____| |__   __|  __ \|  ____/ ____|_   _/ _ \  | |    
| |  __| |  __     | |  | |__) | |__ | |      | || | | | | |    
| | |_ | | |_ |    | |  |  _  /|  __|| |      | || | | | | |    
| |__| | |__| |    | |  | | \ \| |___| |____ _| || |_| | | |____
 \_____|\_____| _  |_|  |_|  \_\______\_____|_____\___/  |______|
               | |                                               
               | |                                               
               | |                                               
               |_|                                               
```

Happy coding! 🎉 