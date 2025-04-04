# 📊 Customizing Output Example

## What This Code Does (Big Picture)
Imagine teaching your robot friend to organize information in exactly the way you want it! This code shows how to create custom output formats for your AI assistant, so it returns data in a structured way that's easy to work with in your programs.

Now, let's go step by step!

## Step 1: Setting Up the Magic Key 🗝️
```python
from agentswithopenai import Agent, Runner, set_default_openai_key
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any
from dotenv import load_dotenv
import asyncio
import os
import json

load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")
set_default_openai_key(openai_api_key)
```
The AI assistant needs a magic key (API key) to work properly.

This code finds the magic key hidden in a secret file (.env) and unlocks it.

## Step 2: Creating Simple Output Models 📋
```python
class WeatherForecast(BaseModel):
    temperature: float
    conditions: str
    chance_of_rain: float
    wind_speed: float
    humidity: float

class MovieRecommendation(BaseModel):
    title: str
    year: int
    genre: str
    director: str
    rating: float
    description: str
```
These create templates for:
- WeatherForecast: Weather information with temperature, conditions, etc.
- MovieRecommendation: Movie details with title, year, director, etc.

## Step 3: Creating Complex Nested Output Models 📑
```python
class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"

class ContactInfo(BaseModel):
    email: str
    phone: Optional[str] = None
    address: Address

class Person(BaseModel):
    name: str
    age: int
    occupation: str
    contact: ContactInfo
    skills: List[str]
    years_experience: Dict[str, int]
```
These create more complex templates with nested information:
- Address: Street, city, state, etc.
- ContactInfo: Email, phone, and address
- Person: Name, age, occupation, contact info, skills, and experience

## Step 4: Creating Union Types for Multiple Outputs 🔀
```python
class SearchResult(BaseModel):
    query: str
    results: List[Union[MovieRecommendation, WeatherForecast, Person]]
    total_results: int
    search_time: float
```
This creates a template that can contain different types of results:
- The query that was searched
- A list of results that could be movies, weather, or people
- Statistics about the search

## Step 5: Creating Agents with Different Output Types 🤖
```python
weather_agent = Agent(
    name="Weather Forecaster",
    instructions="You are a weather forecasting assistant. Provide accurate weather forecasts for the requested location.",
    output_type=WeatherForecast,
)

movie_agent = Agent(
    name="Movie Recommender",
    instructions="You are a movie recommendation assistant. Suggest movies based on user preferences.",
    output_type=MovieRecommendation,
)

person_agent = Agent(
    name="Person Information",
    instructions="You are an assistant that creates fictional person profiles for demonstration purposes.",
    output_type=Person,
)

search_agent = Agent(
    name="Search Engine",
    instructions="""
    You are a search engine assistant. Based on the query, return appropriate search results.
    For weather queries, return WeatherForecast objects.
    For movie queries, return MovieRecommendation objects.
    For person queries, return Person objects.
    """,
    output_type=SearchResult,
)
```
This creates four different AI assistants:
- One that returns weather forecasts
- One that returns movie recommendations
- One that creates fictional person profiles
- One that returns search results with mixed content types

## Step 6: Running the Program with Different Queries 🏃‍♂️
```python
async def main():
    # Test the weather agent
    weather_result = await Runner.run(weather_agent, "What's the weather like in San Francisco today?")
    weather_data = weather_result.final_output_as(WeatherForecast)
    
    # Test the movie agent
    movie_result = await Runner.run(movie_agent, "Recommend a sci-fi movie from the 1980s")
    movie_data = movie_result.final_output_as(MovieRecommendation)
    
    # Test the person agent
    person_result = await Runner.run(person_agent, "Create a profile for a software engineer")
    person_data = person_result.final_output_as(Person)
    
    # Test the search agent
    search_result = await Runner.run(search_agent, "Find information about the weather in New York and recommend a movie for a rainy day")
    search_data = search_result.final_output_as(SearchResult)
    
    # Access specific fields programmatically
    print(f"Temperature in San Francisco: {weather_data.temperature}°F")
    print(f"Recommended movie: {movie_data.title} ({movie_data.year})")
    print(f"Person's name: {person_data.name}, Occupation: {person_data.occupation}")
    print(f"Search found {search_data.total_results} results in {search_data.search_time} seconds")
```
This tests each agent with appropriate queries and shows how to:
1. Get structured data from each agent
2. Access specific fields from the structured data
3. Work with complex nested data structures

## Step 7: Saving and Loading Structured Data 💾
```python
# Save structured data to JSON
with open("weather_data.json", "w") as f:
    f.write(weather_data.json(indent=2))

with open("person_data.json", "w") as f:
    f.write(person_data.json(indent=2))

# Load structured data from JSON
with open("weather_data.json", "r") as f:
    loaded_weather = WeatherForecast.parse_raw(f.read())

print(f"Loaded weather data: {loaded_weather.conditions}, {loaded_weather.temperature}°F")
```
This shows how to:
- Save structured data to JSON files
- Load structured data from JSON files
- Work with the loaded data

## Final Summary 📌
✅ We created simple and complex output models
✅ We created agents that return structured data
✅ We created a search agent that returns mixed result types
✅ We showed how to access specific fields programmatically
✅ We demonstrated saving and loading structured data

## Try It Yourself! 🚀
1. Install the required packages:
   ```
   uv add openai-agents dotenv pydantic
   ```
2. Create a `.env` file with your API key
3. Run the program:
   ```
   uv run customizingoutput.py
   ```
4. Try creating your own output models for different types of data!

## What You'll Learn 🧠
- How to define structured output types with Pydantic
- How to create agents that return structured data
- How to work with nested data structures
- How to save and load structured data

Happy coding! 🎉 