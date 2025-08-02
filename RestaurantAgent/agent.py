from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import AgentSession
from livekit.agents.voice.room_io import RoomInputOptions
from livekit.plugins import groq, silero

# Import all the modules
from config import MENU
from RestaurantAgent.data import UserData
from specialized_agents.specializedagent import SpecializedAgent
# from livekit.plugins import noise_cancellation

async def entrypoint(ctx: JobContext):
    # Initialize user data with all agents
    userdata = UserData()
    userdata.agents.update(
        {
            "greeter": SpecializedAgent(MENU),
        }
    )
    
    # Create the agent session
    session = AgentSession[UserData](
        userdata=userdata,
        stt=groq.STT(model="whisper-large-v3-turbo"),
        llm=groq.LLM(model="llama3-8b-8192"), 
        tts=groq.TTS(model="playai-tts", voice="Arista-PlayAI"),
        vad=silero.VAD.load(),
        max_tool_steps=5,
    )

    # Start the session with the greeter agent
    await session.start(
        agent=userdata.agents["greeter"],
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    # await agent.say("Welcome to our restaurant! How may I assist you today?")
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))