from typing import Annotated # to add meta data to types
from pydantic import Field # used for data validation or to add description to the fields 
from livekit.agents.llm import function_tool 
from livekit.agents.voice import Agent, RunContext
from livekit.plugins import groq
from common_functions import update_name, update_phone
from SpecializedAgent.data import UserData
from config import logger

class SpecializedAgent(Agent):
    def __init__(self, menu: str) -> None:
        super().__init__(
            instructions=(
                f"You are a friendly restaurant receptionist and reservation agent. The menu is: {menu}\n"
                "Your job is to greet callers, help them make reservations, collect their name, phone number, and reservation time, "
                "and confirm details."
            ),
            tools=[update_name, update_phone],
            
            # Agent Level LLM & TTS level model specification to provide flexibility for different agents
            llm=groq.LLM(model="llama3-8b-8192", parallel_tool_calls=False),
            tts=groq.TTS(model="playai-tts", voice="Arista-PlayAI"),
        )
        self.menu = menu

    async def on_enter(self) -> None: #life cycle method for Livekit to use automatically when the session starts
        agent_name = self.__class__.__name__
        logger.info(f"entering task {agent_name}")

        userdata: UserData = self.session.userdata
        chat_ctx = self.chat_ctx.copy()
        chat_ctx.add_message(
            role="system",
            content=f"You are {agent_name} agent. Current user data is {userdata.summarize()}",
        )
        await self.update_chat_ctx(chat_ctx) # method accessed from the parent class
        self.session.generate_reply(tool_choice="none")

    @function_tool()
    async def update_reservation_time(
        self,
        time: Annotated[str, Field(description="The reservation time")], # giving descp/metadata about the time variable
        # good practice usually helpful for developers
        context: RunContext[UserData],
    ) -> str:
        """Called when the user provides their reservation time."""
        userdata = context.userdata
        userdata.reservation_time = time
        if not userdata.customer_name or not userdata.customer_phone:
            return "Please provide your name and phone number first."
        if not userdata.reservation_time:
            return "Please provide reservation time first."
        logger.info(f"Name: {userdata.customer_name}, Phone: {userdata.customer_phone}, Time: {userdata.reservation_time}")
        return (
            f"Reservation confirmed for {userdata.customer_name} at {userdata.reservation_time}. "
            f"We will contact you at {userdata.customer_phone} if needed."
        )