from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import AgentSession
from livekit.agents.voice.room_io import RoomInputOptions
from livekit.plugins import deepgram, silero ,openai, cartesia
# Import all the modules
from config import MENU
from SpecializedAgent.data import UserData
from SpecializedAgent.ReservationAgent import SpecializedAgent
# from livekit.plugins import noise_cancellation

async def entrypoint(ctx: JobContext):
    # Initialize user data with all agents
    userdata = UserData()
    userdata.agents.update(
        {
            "MainAgent": SpecializedAgent(MENU),
        }
    )
    
    # Create the agent session
    session = AgentSession[UserData](
        userdata=userdata,
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=openai.LLM(model="gpt-4-turbo"),  # Updated to use OpenAI's GPT-4 Turbo
        tts=cartesia.TTS(model="sonic-2", voice="f786b574-daa5-4673-aa0c-cbe3e8534c02"),
        vad=silero.VAD.load(),
        max_tool_steps=5,
    )

    # Start the session with the greeter agent
    await session.start(
        agent=userdata.agents["MainAgent"],
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    # await agent.say("Welcome to our restaurant! How may I assist you today?")
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))