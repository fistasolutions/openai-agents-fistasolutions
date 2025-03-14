# Hello World Agents

## Project Setup

This guide provides step-by-step instructions to set up and run the **Hello World Agents** project using `uv`.

### **1. Initialize the Project**
Run the following command to create a new project:
```bash
uv init <project-name>
```
```bash
uv init hello-world-agents
```

### **2. Install Dependencies**
Add the required dependencies:
```bash
uv add openai-agents python-dotenv
```

### **3. Configure API Key**
Create a `.env` file in the project directory and add your OpenAI API key:
```env
OPENAI_API_KEY='sk-proj-...'
```

### **4. Create `main.py`**
Create a `main.py` file in your project directory and add the following code:
```python
from dotenv import load_dotenv
import os
from agents import Agent, Runner

# Load environment variables
load_dotenv()

# Retrieve API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Missing OPENAI_API_KEY. Please set it in .env or export it.")

# Initialize agent
agent = Agent(name="Assistant", instructions="You are a helpful assistant")

# Run agent
result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)
```

### **5. Run the Project**
To execute the script, run:
```bash
uv run main.py
```

### **Expected Output Example:**
```bash
Function calls itself,  
Layers deep in endless loops—  
Code echoes again.
```

If you see:
```bash
OPENAI_API_KEY is not set, skipping trace export
```
Ensure that the `.env` file is correctly formatted and `uv` has access to the API key.

### **6. Troubleshooting**
- If the API key is not detected, try exporting it manually:
  ```bash
  export OPENAI_API_KEY='sk-proj-...'
  ```
- Ensure you are running the script inside the correct virtual environment.
- If issues persist, try updating dependencies:
  ```bash
  uv pip install --upgrade openai openai-agents
  ```

### **7. Additional Resources**
For more details, refer to:
- [OpenAI Agents Documentation](https://platform.openai.com/docs/)
- [uv Package Manager](https://github.com/astral-sh/uv)

---
**Author:** Muhammad Usman  
**License:** MIT
