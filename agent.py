from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import AgentSession, Agent, RoomInputOptions, llm
from livekit.plugins import (
    groq,
    noise_cancellation,
    silero,  # For VAD
)
from prompts import INSTRUCTIONS, WELCOME_MESSAGE, LOOKUP_VIN_MESSAGE
from api import AssistantFnc

load_dotenv()

class Assistant(Agent):
    def __init__(self, fnc_ctx: AssistantFnc) -> None:
        super().__init__(instructions=INSTRUCTIONS)
        self.fnc_ctx = fnc_ctx

async def entrypoint(ctx: agents.JobContext):
    await ctx.connect(auto_subscribe=agents.AutoSubscribe.SUBSCRIBE_ALL)
    await ctx.wait_for_participant()
    
    # Initialize your function context
    assistant_fnc = AssistantFnc()
    
    # Create session with Groq components and function calling
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=groq.STT(
            model="whisper-large-v3-turbo",
            language="en",
        ),
        llm=groq.LLM(
            model="llama3-8b-8192"
        ),
        tts=groq.TTS(
            model="playai-tts",
            voice="Arista-PlayAI",
        ),
        fnc_ctx=assistant_fnc,  # Add your function context
    )
    
    await session.start(
        room=ctx.room,
        agent=Assistant(assistant_fnc),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    # Send welcome message
    await session.generate_reply(
        instructions=f"Say this welcome message: {WELCOME_MESSAGE}"
    )
    
    # Set up event handlers similar to the original
    @session.on("user_speech_committed")
    async def on_user_speech_committed(msg: llm.ChatMessage):
        if isinstance(msg.content, list):
            msg.content = "\n".join("[image]" if isinstance(x, llm.ChatImage) else x for x in msg.content)
            
        if assistant_fnc.has_car():
            await handle_query(msg)
        else:
            await find_profile(msg)
    
    async def find_profile(msg: llm.ChatMessage):
        """Handle VIN lookup when no car profile exists"""
        await session.generate_reply(
            instructions=LOOKUP_VIN_MESSAGE(msg.content)
        )
    
    async def handle_query(msg: llm.ChatMessage):
        """Handle general queries when car profile exists"""
        await session.generate_reply(
            instructions=f"User said: {msg.content}. Respond appropriately based on their car profile and your function capabilities."
        )

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))