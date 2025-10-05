import uuid

from livekit import agents
from dotenv import load_dotenv
from livekit.agents import (
    Agent, AgentSession, RoomInputOptions, WorkerOptions)
from livekit.agents.llm import RawFunctionTool, FunctionTool
from livekit.plugins import (noise_cancellation, silero)
from livekit.plugins.turn_detector.english import EnglishModel  

from agent_utils.default_agent import default_bp
from agent_utils.agent_tools import build_raw_tools
from agent_utils.background_audio import play_background_audio
from agent_utils.first_message_config import first_message_mode
from agent_utils.system_messages import setup_agent_context
from agent_utils.provider_instances import create_provider_instances
from agent_utils.agent_blueprint_loader import load_agent_metadata
from agent_utils.function_tools import patient_lookup, book_appointment


load_dotenv()



class Assistant(Agent):
    def __init__(self, metadata: dict = None, tools: list[FunctionTool | RawFunctionTool] | None = None) -> None:
        # Add patient lookup and appointment booking tools to any existing tools
        if tools:
            all_tools = [patient_lookup, book_appointment] + tools
        else:
            all_tools = [patient_lookup, book_appointment]
            
        super().__init__(instructions="You are a helpful voice AI medical assistant." , tools=all_tools)
        self.metadata = metadata or {}

    async def on_enter(self) -> None:
        # Setup agent context with role and content messages
        await setup_agent_context(self, self.metadata)
        # Execute first message behavior
        await first_message_mode(self.session, self.metadata)


def prewarm(proc: agents.JobProcess):
    proc.userdata["vad"] = silero.VAD.load()
    proc.userdata["metadata"] = default_bp
    # Generate a conversation id
    proc.userdata["conversation_id"] = str(uuid.uuid4())

async def entrypoint(ctx: agents.JobContext):

    metadata = load_agent_metadata()
    # Connect to the room
    await ctx.connect()

    # Wait for a SIP participant
    participant = await ctx.wait_for_participant()

    # Create provider instances
    Providers = create_provider_instances(metadata)
    if not Providers:
        raise RuntimeError(
            "[Randiance][Error] ---> Failed to create provider instances")

    # Create agent session
    session = AgentSession(
        stt=Providers['stt'],
        llm=Providers['llm'],
        tts=Providers['tts'],
        turn_detection=EnglishModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )
    # Start agent session
    await session.start(
        room=ctx.room,
        agent=Assistant(
            metadata=metadata,
            tools=build_raw_tools(metadata.get('tools', [])),
        ),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
     # Play background audio
    await play_background_audio(session)
# Worker options
options = WorkerOptions(
    prewarm_fnc=prewarm,
    entrypoint_fnc=entrypoint,
)
if __name__ == "__main__":
    agents.cli.run_app(options)