from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import AgentSession
from livekit.agents.voice.room_io import RoomInputOptions
from livekit.plugins import groq, silero

# Import all the modules
from config import MENU
from models import UserData
from greeter_agent import Greeter
from reservation_agent import Reservation
from takeaway_agent import Takeaway
from checkout_agent import Checkout

# from livekit.plugins import noise_cancellation


async def entrypoint(ctx: JobContext):
    # Initialize user data with all agents
    userdata = UserData()
    userdata.agents.update(
        {
            "greeter": Greeter(MENU),
            "reservation": Reservation(),
            "takeaway": Takeaway(MENU),
            "checkout": Checkout(MENU),
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
        # to use realtime model, replace the stt, llm, tts and vad with the following
        # llm=openai.realtime.RealtimeModel(voice="alloy"),
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