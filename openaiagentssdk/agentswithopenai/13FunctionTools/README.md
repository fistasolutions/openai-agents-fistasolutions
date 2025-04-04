# 🛠️ Function Tools Example

## What This Code Does (Big Picture)
Imagine teaching your robot friend how to use different gadgets to help you! This code shows how to create custom tools that your AI assistant can use to get weather information, read files, and analyze data.

Now, let's go step by step!

## Step 1: Setting Up the Magic Key 🗝️
```python
import json
import asyncio
from typing_extensions import TypedDict, Any
from agentswithopenai import Agent, FunctionTool, RunContextWrapper, function_tool, set_default_openai_key
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")
set_default_openai_key(openai_api_key)
```
The AI assistant needs a magic key (API key) to work properly.

This code finds the magic key hidden in a secret file (.env) and unlocks it.

## Step 2: Creating a Custom Type for Location 📍
```python
class Location(TypedDict):
    lat: float
    long: float
```
This creates a special template for location information that includes:
- Latitude (a number like 37.7749)
- Longitude (a number like -122.4194)

## Step 3: Creating a Weather Tool 🌦️
```python
@function_tool  
async def fetch_weather(location: Location) -> str:
    """Fetch the weather for a given location."""
    # In real life, we'd fetch the weather from a weather API
    print(f"Fetching weather for location: {location}")
    # Simulate API call delay
    await asyncio.sleep(1)
    return f"The weather at coordinates {location['lat']}, {location['long']} is sunny with a temperature of 72°F."
```
This creates a tool that:
- Takes location coordinates as input
- Pretends to check a weather service
- Returns weather information for that location

## Step 4: Creating a File Reading Tool 📄
```python
@function_tool
def read_file(file_path: str) -> str:
    """Read the contents of a file."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"
```
This creates a tool that:
- Takes a file path as input
- Tries to open and read that file
- Returns the file contents or an error message

## Step 5: Creating a Data Analysis Tool 📊
```python
@function_tool
def analyze_data(text: str) -> dict:
    """Analyze text data and return statistics."""
    words = text.split()
    word_count = len(words)
    char_count = len(text)
    
    # Count word frequencies
    word_freq = {}
    for word in words:
        word = word.lower().strip(".,!?;:()")
        if word:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Find most common words
    most_common = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "word_count": word_count,
        "character_count": char_count,
        "most_common_words": most_common,
        "average_word_length": char_count / word_count if word_count > 0 else 0
    }
```
This creates a tool that:
- Takes text as input
- Counts words and characters
- Finds the most common words
- Calculates average word length
- Returns all these statistics

## Step 6: Creating a Multi-Tool Assistant 🤖
```python
agent = Agent(
    name="Multi-Tool Assistant",
    instructions="""
    You are a helpful assistant with access to various tools.
    - Use the fetch_weather tool to get weather information for coordinates
    - Use the read_file tool to read files from the system
    - Use the analyze_data tool to analyze text data
    
    When the user asks about weather, ask for their coordinates.
    When the user wants to read a file, ask for the file path.
    When the user wants to analyze text, use the analyze_data tool.
    """,
    tools=[fetch_weather, read_file, analyze_data],
)
```
This creates an AI assistant that:
- Knows how to use all three tools
- Understands when to use each tool
- Asks for necessary information before using tools

## Step 7: Running the Program with Different Requests 🏃‍♂️
```python
async def main():
    # Example conversations
    weather_query = "What's the weather like at latitude 37.7749 and longitude -122.4194?"
    file_query = "Can you read the contents of example.txt for me?"
    analysis_query = "Can you analyze this text: 'The quick brown fox jumps over the lazy dog. The dog was too lazy to move.'"
    
    # Run the agent with each query
    result = await Runner.run(agent, weather_query)
    result = await Runner.run(agent, file_query)
    result = await Runner.run(agent, analysis_query)
```
This tests the assistant with different requests:
1. A weather request (uses the fetch_weather tool)
2. A file reading request (uses the read_file tool)
3. A text analysis request (uses the analyze_data tool)

## Final Summary 📌
✅ We created a custom type for location information
✅ We created tools for weather, file reading, and text analysis
✅ We created an AI assistant that knows how to use all these tools
✅ We tested the assistant with different types of requests

## Try It Yourself! 🚀
1. Install the required packages:
   ```
   uv add openai-agents dotenv typing-extensions
   ```
2. Create a `.env` file with your API key
3. Create a sample text file named "example.txt"
4. Run the program:
   ```
   uv run functiontools.py
   ```
5. Try asking about weather, reading files, and analyzing text!

## What You'll Learn 🧠
- How to create custom function tools
- How to define complex input types for tools
- How to create asynchronous tools
- How to handle errors in tools

Happy coding! 🎉 