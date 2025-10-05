from livekit.agents.job import get_job_context
from livekit.agents import (
    AgentSession,
    AudioConfig,
    BackgroundAudioPlayer,
    BuiltinAudioClip,
)


async def play_background_audio(session: AgentSession):
    # Get the job context
    ctx = get_job_context()

    # Initialize the background audio player
    background_audio = BackgroundAudioPlayer(
        ambient_sound=AudioConfig(BuiltinAudioClip.OFFICE_AMBIENCE, volume=0.8)
    )

    # Start the background audio player
    await background_audio.start(room=ctx.room, agent_session=session)