# 🤖 OpenAI Agents SDK Examples

Welcome to the OpenAI Agents SDK examples! This collection of examples will help you learn how to build AI assistants with different capabilities, from simple to advanced.

## 📚 What's Inside

This repository contains 25 examples that progressively introduce more advanced concepts:

1. **Hello World** - Your first AI assistant
2. **Detail Agent** - Creating agents with specific roles
3. **Basic Config** - Configuring agents with tools
4. **Basic Context** - Adding user context to agents
5. **Basic Output** - Structured data output
6. **Basic Handoffs** - Agents that work together
7. **Basic Dynamic Instructions** - Agents that adapt to users
8. **Basic Cloning** - Creating variations of agents
9. **Running** - Multi-turn conversations
10. **Streaming Raw Response** - Real-time responses
11. **Run Item And Agents Events** - Tracking agent actions
12. **Hosted Tools** - Using OpenAI's built-in tools
13. **Function Tools** - Creating custom tools
14. **Custom Function Tools** - Advanced tool creation
15. **Agents As Tools** - Using agents as tools for other agents
16. **Customizing Handoffs** - Advanced agent collaboration
17. **Customizing Guardrails** - Safety features
18. **Customizing Output** - Complex structured data
19. **Customizing Models** - Using different AI models
20. **Customizing Tracing** - Debugging and monitoring
21. **Customizing Streaming** - Advanced real-time responses
22. **Customizing Agents** - Fully customized assistants
23. **Customizing Runners** - Controlling execution
24. **Customizing Errors** - Error handling
25. **Customizing Middleware** - Adding processing layers

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- UV package manager (recommended)

### Installation

1. Clone this repository
2. Install the OpenAI Agents SDK:
   ```
   uv add openai-agents dotenv
   ```
3. Create a `.env` file in the root directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

### Running the Examples

Navigate to any example directory and run the Python file:

```
cd 01Helloworld
uv run helloworld.py
```

## 🧠 Learning Path

We recommend going through the examples in order, as each one builds on concepts from previous examples:

1. Start with **Hello World** to create your first AI assistant
2. Move on to **Basic Config** to learn about tools
3. Try **Basic Context** to personalize responses
4. Explore **Basic Handoffs** to create collaborative agents
5. Continue with more advanced examples as you get comfortable

## 📝 Documentation

Each example includes:
- A README.md file explaining the concepts
- Commented code showing how to implement the features
- Instructions for running and modifying the example

## 🤝 Contributing

Contributions are welcome! If you have ideas for new examples or improvements to existing ones, please open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

Happy coding! 🎉

## Conclusion

The OpenAI Agents Framework provides a powerful foundation for building sophisticated AI applications. By combining the techniques demonstrated in these examples, you can create systems that are:

- **Intelligent**: Leveraging state-of-the-art language models
- **Specialized**: Using purpose-built agents for different tasks
- **Safe**: Implementing comprehensive guardrails
- **Contextual**: Maintaining state and personalization
- **Scalable**: Adapting to varying workloads
- **Extensible**: Integrating with external systems and tools

We hope this repository helps you build amazing AI applications. Happy coding!

---

## Acknowledgments

- OpenAI for developing the Agents Framework
- The open-source community for contributions and feedback
- All the developers building innovative applications with AI

## Contact

For questions, suggestions, or collaboration opportunities, please open an issue on this repository or contact the maintainers directly.
