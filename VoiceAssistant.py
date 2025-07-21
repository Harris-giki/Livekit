from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    groq,
    noise_cancellation,
    silero,  # For VAD
)

load_dotenv()

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful voice AI assistant. Keep your responses conversational and concise.")

async def entrypoint(ctx: agents.JobContext):
    # Create session with Groq components
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=groq.STT(
            model="whisper-large-v3-turbo",
        ),
        llm=groq.LLM(
            model="llama3-8b-8192"
        ),
        tts=groq.TTS(
            model="playai-tts",  
            voice="Arista-PlayAI",
        ),
    )
    
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    await ctx.connect()
    
    # Generate initial greeting
    await session.generate_reply(
        instructions="Greet the user warmly and offer your assistance."
    )

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))