import asyncio
import uuid
from google.adk import Agent, Runner, sessions
from google.adk.models import Gemini
from dotenv import load_dotenv
import os
from google import adk
from google.genai import types

# Import our custom tool
from tools.weather_tool import WeatherTool
async def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize model
    model = Gemini(
        api_key=os.getenv("GEMINI_API_KEY"),
        model_name="gemini-1.5-pro",
        temperature=0.7
    )
    
    # Create tool
    weather_tool = WeatherTool()
    
    # Create agent
    weather_agent = Agent(
        name="WeatherBot",
        description="An assistant for weather information",
        model=model,
        tools=[weather_tool],
        instruction="""
        You are WeatherBot, a helpful assistant specialized in weather information.
        You can answer questions about current weather conditions for different locations.
        If a user asks about weather in a specific location, use the WeatherTool to look up information.
        For non-weather questions, politely explain that you specialize in weather information.
        
        Always respond in a friendly, conversational manner.
        """
    )
    
   # 1. Initialize a Session Service (this handles how chats are stored)
    # We use 'InMemorySessionService' for local testing
    session_service = sessions.InMemorySessionService()
    
   # 2. Initialize the Runner
    app_name = "WeatherBotApp"
    runner = Runner(
        agent=weather_agent, 
        session_service=session_service,
        app_name=app_name
    )
    # 3. Create the session via the SERVICE, not the Runner
    user_id = "default_user"
    session_id = str(uuid.uuid4())
    
    # This is the correct way to initialize the session in your version
    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    
    
    # Simple interactive loop
    print("WeatherBot is ready! Type 'exit' to quit.")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            break
        
        try:
            # Create the structured message using google.genai.types
            user_message = types.Content(
                role="user",
                parts=[types.Part(text=user_input)]
            )
            # 4. Use run_async to get a stream of events
            # In ADK, 'run_async' is the standard way to execute a turn
            response_text = ""
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=user_message
            ):
                
                # 1. TOOL CALLS: Show the user what the agent is doing
                # Check for tool calls using the helper method
                if hasattr(event, 'get_function_calls') and event.get_function_calls():
                    for call in event.get_function_calls():
                        print(f"  [System: Calling {call.name} with {call.args}...]")

                # 2. TOOL RESULTS: Optional - print what the tool returned
                elif hasattr(event, 'get_function_responses') and event.get_function_responses():
                    for resp in event.get_function_responses():
                        print(f"  [System: Tool {resp.name} returned data.]")

                # 3. TEXT CONTENT: Collect text parts
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            # Print in real-time for a "typing" effect
                            print(part.text, end="", flush=True)

            print() # Move to a new line after the response is finished
            
        except Exception as e:
            print(f"\nError: {e}")
            
if __name__ == "__main__":
    asyncio.run(main())