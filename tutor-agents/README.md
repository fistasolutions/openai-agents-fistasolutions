# Tutor Agents - Gaurdrail

## Project Description
This project implements an AI-powered tutoring system using agents. The system determines whether a question is related to homework and routes it to the appropriate tutor agent (Math or History). It uses OpenAI API and relies on `python-dotenv` to manage environment variables.

## Prerequisites
Ensure you have the following installed:
```sh
# Python >= 3.12
python --version

## Installation
```sh
# Clone the repository (if applicable)
git clone <repository-url>
cd tutor-agents

# Install dependencies
uv add openai-agents pydantic python-dotenv
```

## Environment Setup
```sh
# Create a .env file
echo "OPENAI_API_KEY='your-api-key-here'" > .env
```
Ensure the `.env` file contains:
```env
OPENAI_API_KEY='your-api-key-here'
```

## Running the Project
```sh
uv run main.py
```

## How It Works

- The `triage_agent` decides whether a question is homework-related.
- If it's a math-related query, it is forwarded to `math_tutor_agent`.
- If it's a history-related query, it is forwarded to `history_tutor_agent`.
- Responses are printed to the console.

## License
```sh
# MIT License
```

