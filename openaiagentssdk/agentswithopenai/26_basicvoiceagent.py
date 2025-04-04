import asyncio
import random
import os
from dotenv import load_dotenv

# Try to import optional dependencies, but provide helpful error messages if they're missing
try:
    import numpy as np
    import sounddevice as sd
    VOICE_DEPENDENCIES_AVAILABLE = True
except ImportError:
    VOICE_DEPENDENCIES_AVAILABLE = False
    print("Voice dependencies not found. Please install required packages:")
    print("pip install numpy sounddevice")

# Check if voice module is available
try:
    from agents.voice import AudioInput, SingleAgentVoiceWorkflow, VoicePipeline
    VOICE_MODULE_AVAILABLE = True
except ImportError:
    VOICE_MODULE_AVAILABLE = False
    print("The agents.voice module is not available in your installation.")
    print("This demo will run in text-only mode.")

from agentswithopenai import (
    Agent,
    function_tool,
    set_default_openai_key,
)

# Load environment variables
load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")
set_default_openai_key(openai_api_key)

# Define a simple weather tool
@function_tool
def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    print(f"[debug] get_weather called with city: {city}")
    choices = ["sunny", "cloudy", "rainy", "snowy"]
    return f"The weather in {city} is {random.choice(choices)}."

def create_voice_agents():
    """Create and return the voice agents, only importing voice-specific modules when needed."""
    if not VOICE_MODULE_AVAILABLE:
        return None
        
    try:
        from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
        
        # Define a Spanish-speaking agent for handoff
        spanish_agent = Agent(
            name="Spanish Assistant",
            handoff_description="A Spanish-speaking assistant for Spanish language interactions.",
            instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
            You are a helpful voice assistant who speaks Spanish fluently.
            
            When speaking with users:
            - Always respond in Spanish
            - Be polite, friendly, and concise
            - If asked about the weather, use the weather tool
            - Keep your responses conversational and natural for voice interaction
            
            Remember that you are in a voice conversation, so maintain a friendly tone.
            """,
            model="gpt-4o",
            tools=[get_weather],
        )
        
        # Define the main voice agent
        voice_agent = Agent(
            name="Voice Assistant",
            instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
            You are a helpful voice assistant designed for natural conversation.
            
            When speaking with users:
            - Be polite, friendly, and concise
            - Keep responses brief and conversational
            - If asked about the weather, use the weather tool
            - If the user speaks in Spanish, hand off to the Spanish Assistant
            
            Remember that you are in a voice conversation, so maintain a friendly tone
            and avoid lengthy explanations unless specifically requested.
            """,
            model="gpt-4o",
            handoffs=[spanish_agent],
            tools=[get_weather],
        )
        
        return {
            "voice_agent": voice_agent,
            "spanish_agent": spanish_agent,
        }
    except ImportError as e:
        print(f"Error creating voice agents: {e}")
        return None

async def run_voice_demo():
    """Run the voice assistant demo if dependencies are available."""
    if not VOICE_DEPENDENCIES_AVAILABLE:
        print("\nCannot run voice demo: Missing numpy or sounddevice packages.")
        print("Please install the following packages:")
        print("pip install numpy sounddevice")
        return
    
    if not VOICE_MODULE_AVAILABLE:
        print("\nCannot run voice demo: The agents.voice module is not available.")
        print("This feature may require a different version of the agents package.")
        return
    
    voice_components = create_voice_agents()
    if not voice_components:
        print("\nCannot run voice demo: Failed to create voice agents.")
        return
    
    voice_agent = voice_components["voice_agent"]
    
    print("=== Voice Assistant Demo ===")
    print("This demo requires a microphone and speakers.")
    print("Speak into your microphone to interact with the voice assistant.")
    print("The assistant can provide weather information and speak Spanish.")
    print("Press Ctrl+C to exit.")
    
    try:
        # Create the voice pipeline with our agent
        pipeline = VoicePipeline(workflow=SingleAgentVoiceWorkflow(voice_agent))
        
        # Create an audio buffer (3 seconds at 24kHz)
        buffer = np.zeros(24000 * 3, dtype=np.int16)
        audio_input = AudioInput(buffer=buffer)
        
        # Run the pipeline
        result = await pipeline.run(audio_input)
        
        # Set up audio playback
        player = sd.OutputStream(samplerate=24000, channels=1, dtype=np.int16)
        player.start()
        
        # Process and play audio stream events
        print("\nListening... Speak now.")
        async for event in result.stream():
            if event.type == "voice_stream_event_audio":
                # Play the audio response
                player.write(event.data)
            elif event.type == "voice_stream_event_transcript":
                # Print the transcript
                print(f"You said: {event.data}")
            elif event.type == "voice_stream_event_response":
                # Print the assistant's response
                print(f"Assistant: {event.data}")
    
    except KeyboardInterrupt:
        print("\nExiting voice assistant demo.")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: This demo requires the 'sounddevice' and 'numpy' packages.")
        print("Install them with: pip install sounddevice numpy")
        print("You also need a working microphone and speakers.")

async def run_text_demo():
    """Run a text-based version of the demo when voice dependencies aren't available."""
    try:
        from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
    except ImportError:
        RECOMMENDED_PROMPT_PREFIX = ""
        print("Note: Could not import RECOMMENDED_PROMPT_PREFIX, using default instructions.")
    
    # Create a text-based assistant with similar capabilities
    spanish_agent = Agent(
        name="Spanish Assistant",
        handoff_description="A Spanish-speaking assistant for Spanish language interactions.",
        instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
        You are a helpful assistant who speaks Spanish fluently.
        
        When speaking with users:
        - Always respond in Spanish
        - Be polite, friendly, and concise
        - If asked about the weather, use the weather tool
        """,
        model="gpt-4o",
        tools=[get_weather],
    )
    
    text_agent = Agent(
        name="Text Assistant",
        instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
        You are a helpful assistant designed for natural conversation.
        
        When speaking with users:
        - Be polite, friendly, and concise
        - If asked about the weather, use the weather tool
        - If the user speaks in Spanish, hand off to the Spanish Assistant
        """,
        model="gpt-4o",
        handoffs=[spanish_agent],
        tools=[get_weather],
    )
    
    from agentswithopenai import Runner
    
    print("=== Text Assistant Demo ===")
    if not VOICE_MODULE_AVAILABLE or not VOICE_DEPENDENCIES_AVAILABLE:
        print("Voice capabilities not available, running text-based version instead.")
    print("You can ask about the weather or speak in Spanish.")
    print("Type 'exit' to quit.")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            break
        
        result = await Runner.run(text_agent, user_input)
        print(f"Assistant: {result.final_output}")

async def main():
    """Main function that decides which demo to run based on available dependencies."""
    if VOICE_DEPENDENCIES_AVAILABLE and VOICE_MODULE_AVAILABLE:
        await run_voice_demo()
    else:
        print("\nRunning text-based demo instead of voice demo due to missing dependencies.")
        await run_text_demo()

if __name__ == "__main__":
    asyncio.run(main()) 