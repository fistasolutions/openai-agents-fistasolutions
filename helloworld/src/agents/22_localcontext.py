import asyncio
from dataclasses import dataclass
from typing import List, Optional, Dict
import json

from agents import Agent, RunContextWrapper, Runner, function_tool, set_default_openai_key
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")

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
        return "No purchase history available for this user."
    
    purchases = []
    for purchase in user.purchase_history:
        purchases.append(f"- {purchase['date']}: {purchase['item']} (${purchase['amount']})")
    
    return f"Purchase History:\n" + "\n".join(purchases)

@function_tool
async def update_user_preference(wrapper: RunContextWrapper[UserInfo], category: str, value: str) -> str:
    """Update a user preference.
    
    Args:
        category: The preference category to update
        value: The new value for the preference
    """
    user = wrapper.context
    user.preferences[category] = value
    return f"Updated {category} preference to '{value}' for user {user.name}."

@function_tool
async def check_subscription_features(wrapper: RunContextWrapper[UserInfo]) -> str:
    """Check what features are available with the user's subscription."""
    user = wrapper.context
    
    if user.subscription_tier == "free":
        return """
Free Tier Features:
- Basic content access
- Standard support
- Limited to 5 searches per day
- No advanced features
"""
    elif user.subscription_tier == "premium":
        return """
Premium Tier Features:
- Full content access
- Priority support
- Unlimited searches
- Advanced analytics
- Custom exports
"""
    elif user.subscription_tier == "enterprise":
        return """
Enterprise Tier Features:
- All Premium features
- Dedicated account manager
- Custom integrations
- Team collaboration tools
- Advanced security features
- SLA guarantees
"""
    else:
        return f"Unknown subscription tier: {user.subscription_tier}"

# Create an agent that uses the context
def create_personalized_agent(user_info: UserInfo) -> Agent[UserInfo]:
    return Agent[UserInfo](
        name="Personalized Assistant",
        instructions=f"""
        You are a personalized assistant for {user_info.name}.
        
        Use the available tools to access and update user information.
        Always be helpful, friendly, and personalized in your responses.
        
        When the user asks about their profile, preferences, or purchases,
        use the appropriate tool to fetch the most up-to-date information.
        
        When they want to update preferences, use the update_user_preference tool.
        
        Refer to the user by name and tailor your responses based on their
        subscription tier and preferences when relevant.
        """,
        tools=[
            fetch_user_profile,
            fetch_user_preferences,
            fetch_purchase_history,
            update_user_preference,
            check_subscription_features,
        ],
    )

# Create sample users with different profiles
def create_sample_users() -> Dict[int, UserInfo]:
    users = {}
    
    # Free tier user
    john = UserInfo(
        name="John Smith",
        uid=101,
        email="john.smith@example.com",
        subscription_tier="free",
        preferences={
            "theme": "light",
            "notifications": "email",
            "language": "English"
        },
        purchase_history=[
            {"date": "2023-01-15", "item": "Basic Tutorial", "amount": 9.99}
        ]
    )
    users[john.uid] = john
    
    # Premium tier user
    sarah = UserInfo(
        name="Sarah Johnson",
        uid=202,
        email="sarah.j@example.com",
        subscription_tier="premium",
        preferences={
            "theme": "dark",
            "notifications": "push",
            "language": "Spanish",
            "dashboard": "analytics"
        },
        purchase_history=[
            {"date": "2023-02-10", "item": "Premium Subscription", "amount": 49.99},
            {"date": "2023-03-05", "item": "Advanced Course", "amount": 29.99},
            {"date": "2023-04-20", "item": "Data Export Add-on", "amount": 19.99}
        ]
    )
    users[sarah.uid] = sarah
    
    # Enterprise tier user
    acme = UserInfo(
        name="Acme Corporation",
        uid=303,
        email="admin@acmecorp.com",
        subscription_tier="enterprise",
        preferences={
            "theme": "branded",
            "notifications": "slack",
            "language": "English",
            "dashboard": "team",
            "security": "enhanced",
            "reports": "weekly"
        },
        purchase_history=[
            {"date": "2023-01-01", "item": "Enterprise License", "amount": 999.99},
            {"date": "2023-01-01", "item": "Custom Integration", "amount": 2500.00},
            {"date": "2023-03-15", "item": "Team Training", "amount": 1200.00},
            {"date": "2023-05-10", "item": "Security Add-on", "amount": 499.99}
        ]
    )
    users[acme.uid] = acme
    
    return users

async def interact_with_user(user_info: UserInfo, query: str):
    print(f"\n=== Interaction for {user_info.name} (UID: {user_info.uid}) ===")
    print(f"Query: {query}")
    
    # Create a personalized agent for this user
    agent = create_personalized_agent(user_info)
    
    # Run the agent with the user's context
    result = await Runner.run(
        starting_agent=agent,
        input=query,
        context=user_info,
    )
    
    print("\nResponse:")
    print(result.final_output)
    
    # Return the updated user info (in case it was modified)
    return user_info

async def demo_basic_context():
    print("=== Basic Context Demo ===")
    
    # Create a simple user
    user_info = UserInfo(name="John", uid=123)
    
    # Create a simple agent
    agent = Agent[UserInfo](
        name="Basic Assistant",
        instructions="You are a helpful assistant. Use the tools to provide information about the user.",
        tools=[fetch_user_age],
    )
    
    # Run the agent with context
    result = await Runner.run(
        starting_agent=agent,
        input="What is the age of the user?",
        context=user_info,
    )
    
    print("\nResponse:")
    print(result.final_output)

# Define a simple function tool for the basic demo
@function_tool
async def fetch_user_age(wrapper: RunContextWrapper[UserInfo]) -> str:
    """Fetch the user's age."""
    return f"User {wrapper.context.name} is 47 years old"

async def main():
    set_default_openai_key(openai_api_key)
    
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