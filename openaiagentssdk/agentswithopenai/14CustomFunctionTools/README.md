# 🔧 Custom Function Tools Example

## What This Code Does (Big Picture)
Imagine building specialized equipment for your robot friend to solve complex problems! This code shows how to create advanced custom tools that can process data, work with external services, and handle complex inputs and outputs.

Now, let's go step by step!

## Step 1: Setting Up the Magic Key 🗝️
```python
from agentswithopenai import Agent, FunctionTool, Runner, set_default_openai_key
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import statistics
import json

load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")
set_default_openai_key(openai_api_key)
```
The AI assistant needs a magic key (API key) to work properly.

This code finds the magic key hidden in a secret file (.env) and unlocks it.

## Step 2: Creating Complex Data Models 📊
```python
class DataPoint(BaseModel):
    x: float
    y: float
    label: Optional[str] = None

class AnalysisResult(BaseModel):
    mean: float
    median: float
    trend: str
    outliers: List[DataPoint]
```
These create templates for:
- DataPoint: A single point with x and y coordinates and an optional label
- AnalysisResult: Statistics about a set of data points

## Step 3: Creating a Data Analysis Function ⚙️
```python
def analyze_data_points(data_points: List[Dict[str, Any]], analysis_type: str = "basic") -> Dict[str, Any]:
    """Analyze a set of data points and return statistical information"""
    # Convert input dictionaries to DataPoint objects
    points = [DataPoint(**point) for point in data_points]
    
    # Extract y values for statistical analysis
    y_values = [point.y for point in points]
    
    # Calculate basic statistics
    mean_y = statistics.mean(y_values)
    median_y = statistics.median(y_values)
    
    # Determine trend (increasing, decreasing, or flat)
    if len(points) >= 2:
        first_y = points[0].y
        last_y = points[-1].y
        if last_y > first_y:
            trend = "increasing"
        elif last_y < first_y:
            trend = "decreasing"
        else:
            trend = "flat"
    else:
        trend = "insufficient data"
    
    # Find outliers (points more than 2 standard deviations from mean)
    outliers = []
    if len(y_values) >= 2:
        std_dev = statistics.stdev(y_values)
        outliers = [point for point in points if abs(point.y - mean_y) > 2 * std_dev]
    
    # Create and return the analysis result
    result = AnalysisResult(
        mean=mean_y,
        median=median_y,
        trend=trend,
        outliers=outliers
    )
    
    return result.dict()
```
This function:
- Takes a list of data points and an analysis type
- Calculates statistics like mean and median
- Determines if the data is trending up or down
- Identifies outliers (unusual points)
- Returns a structured result

## Step 4: Creating a Custom Function Tool 🛠️
```python
data_analysis_tool = FunctionTool(
    name="analyze_data_points",
    description="Analyze a set of data points and return statistical information",
    input_schema={
        "type": "object",
        "properties": {
            "data_points": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "label": {"type": "string"}
                    },
                    "required": ["x", "y"]
                }
            },
            "analysis_type": {"type": "string", "enum": ["basic", "detailed"]}
        },
        "required": ["data_points"]
    },
    function=analyze_data_points
)
```
This creates a custom tool that:
- Has a specific name and description
- Defines exactly what inputs it accepts
- Specifies which inputs are required
- Links to the analysis function we created

## Step 5: Creating a Data Analyst Agent 🤖
```python
data_analyst_agent = Agent(
    name="Data Analyst",
    instructions="""
    You are a data analysis assistant. When given data points, use the analyze_data_points
    tool to perform statistical analysis and explain the results in a clear, understandable way.
    
    When explaining results:
    1. Describe the overall trend (increasing, decreasing, or flat)
    2. Mention the average (mean) and median values
    3. Point out any outliers and what might cause them
    4. Provide insights about what the data might indicate
    
    Always ask for data points if the user doesn't provide them.
    """,
    tools=[data_analysis_tool]
)
```
This creates an AI assistant that:
- Specializes in data analysis
- Knows how to use the data analysis tool
- Explains results in a clear way
- Asks for data if it's not provided

## Step 6: Running the Program with Sample Data 🏃‍♂️
```python
async def main():
    # Sample data points
    sample_data = [
        {"x": 1, "y": 5, "label": "Start"},
        {"x": 2, "y": 7},
        {"x": 3, "y": 9},
        {"x": 4, "y": 8},
        {"x": 5, "y": 12, "label": "End"}
    ]
    
    # Sample query with data
    query = f"Can you analyze these data points and tell me what they show? {json.dumps(sample_data)}"
    
    # Run the agent
    result = await Runner.run(data_analyst_agent, query)
    print("\nAnalysis Result:")
    print(result.final_output)
```
This runs the assistant with sample data points and asks for an analysis.

## Final Summary 📌
✅ We created complex data models for points and analysis results
✅ We created a function that performs statistical analysis
✅ We created a custom tool with a detailed input schema
✅ We created an AI assistant that uses this tool to analyze data
✅ We tested the assistant with sample data points

## Try It Yourself! 🚀
1. Install the required packages:
   ```
   uv add openai-agents dotenv pydantic
   ```
2. Create a `.env` file with your API key
3. Run the program:
   ```
   uv run customfunctiontools.py
   ```
4. Try with different sets of data points!

## What You'll Learn 🧠
- How to create tools with complex input/output types
- How to define detailed JSON schemas for tools
- How to perform data analysis in custom tools
- How to create agents that explain technical results clearly

Happy coding! 🎉 