import asyncio
from dataclasses import dataclass
from typing import List, Optional, Dict
import json
import os
from dotenv import load_dotenv
from agents import Agent, RunContextWrapper, Runner, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig

# Load the environment variables from the .env file
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# Check if the API key is present; if not, raise an error
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

# Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

# Define a data class to hold user information
@dataclass
class UserInfo:
    name: str
    uid: int
    email: Optional[str] = None
    subscription_tier: str = "free"
    preferences: Dict[str, str] = None
    purchase_history: List[Dict] = None

    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {}
        if self.purchase_history is None:
            self.purchase_history = []

# Define function tools that use the context
@function_tool
async def fetch_user_profile(wrapper: RunContextWrapper[UserInfo]) -> str:
    """Fetch the user's profile information."""
    user = wrapper.context
    return f"""
User Profile:
- Name: {user.name}
- User ID: {user.uid}
- Email: {user.email or 'Not provided'}
- Subscription: {user.subscription_tier}
"""

@function_tool
async def fetch_user_preferences(wrapper: RunContextWrapper[UserInfo]) -> str:
    """Fetch the user's preferences."""
    user = wrapper.context
    if not user.preferences:
        return "No preferences have been set for this user."
    
    prefs = "\n".join([f"- {k}: {v}" for k, v in user.preferences.items()])
    return f"User Preferences:\n{prefs}"

@function_tool
async def fetch_purchase_history(wrapper: RunContextWrapper[UserInfo]) -> str:
    """Fetch the user's purchase history."""
    user = wrapper.context
    if not user.purchase_history:
        return "No purchase history found for this user."
    
    history = "\n".join([f"- {p.get('item', 'Unknown item')}: ${p.get('price', 0.0)} on {p.get('date', 'Unknown date')}" for p in user.purchase_history])
    return f"Purchase History:\n{history}"

@function_tool
async def get_subscription_features(wrapper: RunContextWrapper[UserInfo]) -> str:
    """Get the features available for the user's subscription tier."""
    user = wrapper.context
    
    features = {
        "free": [
            "Basic access to platform",
            "Limited storage (5GB)",
            "Standard support",
            "Access to community forums"
        ],
        "basic": [
            "Full access to platform",
            "Increased storage (50GB)",
            "Priority email support",
            "No advertisements",
            "Monthly newsletter"
        ],
        "premium": [
            "Full access to all features",
            "Unlimited storage",
            "24/7 priority support",
            "Early access to new features",
            "Exclusive content",
            "Personalized recommendations"
        ]
    }
    
    tier = user.subscription_tier.lower()
    if tier not in features:
        return f"Unknown subscription tier: {user.subscription_tier}"
    
    feature_list = "\n".join([f"- {f}" for f in features[tier]])
    return f"Features for {user.subscription_tier.capitalize()} tier:\n{feature_list}"

@function_tool
async def update_user_preference(wrapper: RunContextWrapper[UserInfo], key: str, value: str) -> str:
    """Update a user preference setting."""
    user = wrapper.context
    
    # Update the preference
    user.preferences[key] = value
    
    return f"Successfully updated preference: {key} = {value}"

# Create an agent with UserInfo context
user_context_agent = Agent[UserInfo](
    name="User Context Agent",
    instructions="""
    You are a personalized assistant that provides tailored responses based on user context.
    
    Use the available tools to:
    1. Retrieve user profile information
    2. Access user preferences
    3. View purchase history
    4. Provide information about subscription features
    5. Update user preferences when requested
    
    Tailor your responses based on the user's subscription tier:
    - For free users: Be helpful but mention premium features they could access by upgrading
    - For basic users: Provide more detailed assistance and occasionally highlight premium features
    - For premium users: Provide comprehensive, white-glove service with no upselling
    
    Always be friendly, helpful, and personalized in your interactions.
    """,
    tools=[
        fetch_user_profile,
        fetch_user_preferences,
        fetch_purchase_history,
        get_subscription_features,
        update_user_preference
    ],
    model=model
)

# Function to demonstrate basic context usage
async def demo_basic_context():
    print("=== Basic Context Demo ===")
    
    # Create a simple user
    user = UserInfo(
        name="Alice",
        uid=12345,
        email="alice@example.com",
        subscription_tier="premium",
        preferences={"theme": "dark", "notifications": "enabled"},
        purchase_history=[
            {"item": "Annual Subscription", "price": 99.99, "date": "2023-01-15"},
            {"item": "Premium Add-on", "price": 29.99, "date": "2023-02-20"}
        ]
    )
    
    # Run a query with the user context
    result = await Runner.run(
        user_context_agent,
        "Tell me about myself and my subscription",
        context=user,
        run_config=config
    )
    
    print("\nResponse:")
    print(result.final_output)

# Function to create sample users
def create_sample_users():
    users = {}
    
    # Free tier user
    users[1] = UserInfo(
        name="Bob Smith",
        uid=1,
        email="bob@example.com",
        subscription_tier="free",
        preferences={"language": "English", "theme": "light"}
    )
    
    # Basic tier user
    users[2] = UserInfo(
        name="Carol Johnson",
        uid=2,
        email="carol@example.com",
        subscription_tier="basic",
        preferences={"language": "Spanish", "theme": "auto", "notifications": "disabled"},
        purchase_history=[
            {"item": "Basic Subscription", "price": 49.99, "date": "2023-03-10"}
        ]
    )
    
    # Premium tier user
    users[3] = UserInfo(
        name="David Chen",
        uid=3,
        email="david@example.com",
        subscription_tier="premium",
        preferences={"language": "Chinese", "theme": "dark", "notifications": "enabled", "auto_renewal": "enabled"},
        purchase_history=[
            {"item": "Premium Subscription", "price": 99.99, "date": "2023-01-05"},
            {"item": "Data Backup Add-on", "price": 19.99, "date": "2023-01-15"},
            {"item": "Advanced Analytics", "price": 29.99, "date": "2023-02-20"}
        ]
    )
    
    return users

# Function to interact with a user
async def interact_with_user(user: UserInfo, query: str) -> UserInfo:
    print(f"\n=== Interaction with {user.name} ({user.subscription_tier} tier) ===")
    print(f"Query: {query}")
    
    result = await Runner.run(
        user_context_agent,
        query,
        context=user,
        run_config=config
    )
    
    print("Response:")
    print(result.final_output)
    
    # Return the potentially modified user
    return user

async def main():
    # Run the basic context demo
    await demo_basic_context()
    
    # Create sample users
    users = create_sample_users()
    
    # Sample queries for different users
    queries = [
        "What's in my user profile?",
        "What are my current preferences?",
        "Show me my purchase history.",
        "What features do I have with my subscription?",
        "Update my theme preference to 'blue'.",
        "What are all my preferences now?"
    ]
    
    # Run interactions for each user with each query
    for uid, user in users.items():
        for query in queries:
            user = await interact_with_user(user, query)
    
    # Interactive mode
    print("\n=== Interactive Mode ===")
    print("Select a user to interact with:")
    for uid, user in users.items():
        print(f"{uid}: {user.name} ({user.subscription_tier} tier)")
    
    while True:
        try:
            uid_input = input("\nEnter user ID (or 'exit' to quit): ")
            if uid_input.lower() == 'exit':
                break
            
            uid = int(uid_input)
            if uid not in users:
                print(f"User ID {uid} not found. Please try again.")
                continue
            
            query = input("Enter your query: ")
            if query.lower() == 'exit':
                break
            
            users[uid] = await interact_with_user(users[uid], query)
            
        except ValueError:
            print("Please enter a valid user ID.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 