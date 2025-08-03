from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import AgentSession
from livekit.agents.voice.room_io import RoomInputOptions
from livekit.plugins import groq, silero

from models import UserData, StudentDatabase
from simple_agent import StudentInfoAgent
from config import logger


async def entrypoint(ctx: JobContext):
    """Main entry point for the student information voice agent"""
    logger.info("Starting Student Information Voice Agent")
    
    # Initialize database (creates table and dummy data if needed)
    db = StudentDatabase()
    
    # Create simple user data for this session
    user_data = UserData()
    
    # Create the agent
    agent = StudentInfoAgent()
    
    # Create the agent session with Groq services
    session = AgentSession[UserData](
        userdata=user_data,
        stt=groq.STT(model="whisper-large-v3-turbo"),
        llm=groq.LLM(model="llama3-8b-8192"),
        tts=groq.TTS(model="playai-tts", voice="Arista-PlayAI"),
        vad=silero.VAD.load(),
        max_tool_steps=5,
    )
    
    # Start the session
    await session.start(
        agent=agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(),
    )
    
    logger.info("Student voice agent session started successfully")


if __name__ == "__main__":
    # Run the application
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))