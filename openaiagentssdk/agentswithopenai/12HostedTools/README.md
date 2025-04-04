# 🔧 Hosted Tools Example

## What This Code Does (Big Picture)
Imagine giving your robot friend superpowers to search the internet and look through documents! This code shows how to use OpenAI's built-in tools that let your AI assistant search the web for current information and find relevant content in your documents.

Now, let's go step by step!

## Step 1: Setting Up the Magic Key 🗝️
```python
from agentswithopenai import Agent, FileSearchTool, Runner, WebSearchTool, set_default_openai_key
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")
vector_store_id = os.environ.get("VECTOR_STORE_ID", "your_vector_store_id_here")
```
The AI assistant needs a magic key (API key) to work properly, plus a special ID for where your documents are stored.

This code finds these keys hidden in a secret file (.env) and unlocks them.

## Step 2: Creating a Research Assistant with Hosted Tools 🤖
```python
research_agent = Agent(
    name="Research Assistant",
    instructions="""
    You are a helpful research assistant that can search the web and retrieve information 
    from documents to provide comprehensive answers.
    
    When answering questions:
    1. Use the WebSearchTool to find current information from the internet
    2. Use the FileSearchTool to find relevant information from stored documents
    3. Combine information from both sources to provide a complete answer
    4. Always cite your sources
    5. If the information is not available or unclear, be honest about limitations
    """,
    tools=[
        WebSearchTool(),
        FileSearchTool(
            max_num_results=3,
            vector_store_ids=[vector_store_id],
        ),
    ],
)
```
This creates an AI assistant that:
- Can search the web for current information
- Can search through your documents for relevant content
- Combines information from both sources
- Cites its sources properly

## Step 3: Running the Research Assistant 🏃‍♂️
```python
async def main():
    # Example query
    query = "Which coffee shop should I go to, taking into account my preferences and the weather today in SF?"
    
    try:
        result = await Runner.run(research_agent, query)
        print("\nResponse:")
        print(result.final_output)
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: To use WebSearchTool and FileSearchTool, you need:")
        print("1. Proper API keys configured")
        print("2. A valid vector store ID for FileSearchTool")
        print("3. Access to the OpenAI hosted tools")
```
This runs the research assistant with a sample question that requires:
1. Current information (today's weather in SF)
2. Personal information (your preferences, which might be in your documents)

## Step 4: Creating an Interactive Research Mode 💬
```python
print("\n=== Interactive Research Mode ===")
print("Type 'exit' to quit")

while True:
    user_input = input("\nYou: ")
    if user_input.lower() == 'exit':
        break
    
    try:
        result = await Runner.run(research_agent, user_input)
        print("\nResearch results:")
        print(result.final_output)
    except Exception as e:
        print(f"\nError: {e}")
```
This creates an interactive mode where:
- You can ask research questions
- The AI searches the web and your documents
- It combines information to give you comprehensive answers
- You can type "exit" to quit

## Final Summary 📌
✅ We created a research assistant with web search capabilities
✅ We gave it access to search through our documents
✅ We instructed it to combine information from multiple sources
✅ We created an interactive research mode for asking questions
✅ We added error handling for when the tools aren't properly configured

## Try It Yourself! 🚀
1. Install the required packages:
   ```
   uv add openai-agents dotenv
   ```
2. Create a `.env` file with your API key and vector store ID
3. Run the program:
   ```
   uv run hostedtools.py
   ```
4. Ask research questions that require current and stored information!

## What You'll Learn 🧠
- How to use OpenAI's hosted tools
- How to combine information from multiple sources
- How to create a research assistant
- How to work with vector stores for document search

Happy coding! 🎉 