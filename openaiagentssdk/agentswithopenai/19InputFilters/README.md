# 🧠 Customizing Models Example

## What This Code Does (Big Picture)
Imagine being able to choose exactly which AI brain your robot friend uses! This code shows how to customize which AI models your assistants use, how to set specific parameters for each model, and how to compare the results from different models.

Now, let's go step by step!

## Step 1: Setting Up the Magic Key 🗝️
```python
from agentswithopenai import Agent, Runner, ModelSettings, set_default_openai_key
from dotenv import load_dotenv
import asyncio
import os
import time

load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")
set_default_openai_key(openai_api_key)
```
The AI assistants need a magic key (API key) to work properly.

This code finds the magic key hidden in a secret file (.env) and unlocks it.

## Step 2: Creating Model Settings for Different Models ⚙️
```python
# GPT-3.5 Turbo settings
gpt35_settings = ModelSettings(
    model="gpt-3.5-turbo",
    temperature=0.7,
    max_tokens=500
)

# GPT-4 settings
gpt4_settings = ModelSettings(
    model="gpt-4",
    temperature=0.7,
    max_tokens=500
)

# GPT-4 with different parameters
gpt4_creative_settings = ModelSettings(
    model="gpt-4",
    temperature=1.0,  # Higher temperature for more creative responses
    max_tokens=1000,  # More tokens for longer responses
    top_p=0.9,
    frequency_penalty=0.5,
    presence_penalty=0.5
)

# Claude settings (if available)
claude_settings = ModelSettings(
    model="claude-3-5-sonnet-20240620",
    temperature=0.7,
    max_tokens=500
)
```
These create settings for different AI models:
- GPT-3.5 Turbo: A faster, more economical model
- GPT-4: A more powerful, advanced model
- GPT-4 Creative: The same model but with settings for more creative responses
- Claude: An alternative model from Anthropic (if available)

## Step 3: Creating Agents with Different Models 🤖
```python
gpt35_agent = Agent(
    name="GPT-3.5 Agent",
    instructions="You are a helpful assistant powered by GPT-3.5 Turbo. Provide concise, accurate responses.",
    model_settings=gpt35_settings
)

gpt4_agent = Agent(
    name="GPT-4 Agent",
    instructions="You are a helpful assistant powered by GPT-4. Provide detailed, nuanced responses.",
    model_settings=gpt4_settings
)

gpt4_creative_agent = Agent(
    name="GPT-4 Creative Agent",
    instructions="You are a creative assistant powered by GPT-4. Generate imaginative, original content.",
    model_settings=gpt4_creative_settings
)

claude_agent = Agent(
    name="Claude Agent",
    instructions="You are a helpful assistant powered by Claude. Provide thoughtful, balanced responses.",
    model_settings=claude_settings
)
```
This creates four different AI assistants:
- One using GPT-3.5 Turbo for faster, more economical responses
- One using GPT-4 for more detailed, nuanced responses
- One using GPT-4 with creative settings for more imaginative content
- One using Claude for an alternative perspective (if available)

## Step 4: Running the Program with Different Queries 🏃‍♂️
```python
async def main():
    # Test queries
    factual_query = "Explain how photosynthesis works in plants"
    creative_query = "Write a short story about a robot discovering emotions"
    complex_query = "What are the ethical implications of artificial intelligence in healthcare?"
    
    # Compare models on factual query
    print("\n--- Factual Query: Photosynthesis ---")
    
    start_time = time.time()
    result = await Runner.run(gpt35_agent, factual_query)
    gpt35_time = time.time() - start_time
    print(f"\nGPT-3.5 Response (took {gpt35_time:.2f} seconds):")
    print(result.final_output)
    
    start_time = time.time()
    result = await Runner.run(gpt4_agent, factual_query)
    gpt4_time = time.time() - start_time
    print(f"\nGPT-4 Response (took {gpt4_time:.2f} seconds):")
    print(result.final_output)
    
    # Compare models on creative query
    print("\n--- Creative Query: Robot Story ---")
    
    start_time = time.time()
    result = await Runner.run(gpt4_agent, creative_query)
    print(f"\nGPT-4 Standard Response:")
    print(result.final_output)
    
    start_time = time.time()
    result = await Runner.run(gpt4_creative_agent, creative_query)
    print(f"\nGPT-4 Creative Response:")
    print(result.final_output)
```
This tests different models with various types of queries:
1. A factual query about photosynthesis
2. A creative query asking for a short story
3. A complex query about ethics in AI

It also measures and compares:
- Response times for different models
- Quality and style differences between models
- How parameter settings affect creativity

## Step 5: Creating a Model Comparison Function 📊
```python
async def compare_models(query, agents, show_timing=True):
    """Compare responses from multiple agents on the same query"""
    print(f"\n--- Query: {query} ---")
    
    results = {}
    for agent in agents:
        start_time = time.time()
        result = await Runner.run(agent, query)
        elapsed_time = time.time() - start_time
        
        print(f"\n{agent.name} Response" + (f" (took {elapsed_time:.2f} seconds)" if show_timing else "") + ":")
        print(result.final_output)
        
        results[agent.name] = {
            "output": result.final_output,
            "time": elapsed_time
        }
    
    return results
```
This function:
- Takes a query and a list of agents
- Runs the query on each agent
- Measures response time for each
- Displays the results side by side for comparison

## Step 6: Running Comprehensive Comparisons 🔍
```python
# Run comprehensive comparisons
all_agents = [gpt35_agent, gpt4_agent, gpt4_creative_agent]
if "claude" in claude_settings.model.lower():
    all_agents.append(claude_agent)

test_queries = [
    "Explain quantum computing in simple terms",
    "Write a haiku about artificial intelligence",
    "What are three ways to improve productivity?",
    "Debate the pros and cons of remote work"
]

for query in test_queries:
    await compare_models(query, all_agents)
```
This runs a comprehensive comparison:
- Using multiple test queries
- Testing all available models
- Showing side-by-side comparisons of responses
- Measuring performance differences

## Final Summary 📌
✅ We created custom settings for different AI models
✅ We created agents that use different models and parameters
✅ We compared models on factual, creative, and complex queries
✅ We measured response times and quality differences
✅ We created a function for comprehensive model comparisons

## Try It Yourself! 🚀
1. Install the required packages:
   ```
   uv add openai-agents dotenv
   ```
2. Create a `.env` file with your API key
3. Run the program:
   ```
   uv run customizingmodels.py
   ```
4. Try comparing models with your own questions!

## What You'll Learn 🧠
- How to configure different AI models
- How to adjust parameters like temperature and token limits
- How to compare performance between models
- How to choose the right model for different tasks

Happy coding! 🎉 