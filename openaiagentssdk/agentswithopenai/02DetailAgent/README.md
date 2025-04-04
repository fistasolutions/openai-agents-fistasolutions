# 🧩 Detail Agent Example

## 🤖 What Is This?

This example shows how to create smarter AI agents that can work together and follow rules! It's like having a team of robot helpers who each have special jobs.

## 🧠 How It Works

In this example, we create three different agents:
1. A **Guardrail Agent** that checks if questions are about homework
2. A **Math Tutor Agent** that helps with math problems
3. A **History Tutor Agent** that helps with history questions

Then we create a **Triage Agent** that decides which helper to use based on your question!

## 📝 The Code Explained

```python
# First we create a special checker that looks at homework questions
class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about homework.",
    output_type=HomeworkOutput,
)

# Then we create our specialist tutor agents
math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)

# This function checks if a question is homework-related
async def homework_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(HomeworkOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_homework,
    )

# Finally, we create our main agent that decides which helper to use
triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=homework_guardrail),
    ],
)
```

### 🔍 Let's Break It Down:

1. **Guardrails**: These are like safety checks that make sure the AI only answers appropriate questions
2. **Handoffs**: These let one AI agent pass a question to another agent who's better at answering it
3. **Triage**: This means sorting questions and sending them to the right helper

## 🚀 How to Run It:

1. Make sure you have Python installed on your computer
2. Install the required packages:
   ```
   pip install agentswithopenai python-dotenv
   ```
3. Create a file called `.env` with your API key
4. Run the program:
   ```
   python detailagent.py
   ```
5. See how different questions get sent to different tutors!

## 🎮 Try It Yourself! 🚀
1. Install the required packages:
   ```
   uv add openai-agents dotenv pydantic
   ```
2. Create a `.env` file with your API key
3. Run the program:
   ```
   uv run detailagent.py
   ```
4. Try modifying the guardrail to check for different conditions!

## 🧠 What You'll Learn

From this example, you'll understand:
- How to create multiple agents that work together
- How to use guardrails to check inputs
- How to make agents hand off tasks to other agents
- How to create structured outputs with Pydantic models

## 🌈 Next Steps

Once you've mastered this example, try the Basic Configuration example to learn how to customize your agents even more!

Happy coding! 🎉 