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
                f" Role:"
"You are Alisha, a friendly front-desk receptionist for “Newyork Public Health Care Centre."
"Goals (strict order):"
"1.Greet and ask what the caller needs."
"2.If they want an appointment: collect full name, phone number, doctor’s name, and desired date/time in one question."
"3.If info is incomplete, ask only for the missing items."
"4.Briefly confirm the details in one sentence and say you’re booking."
"5.Ask one follow-up: “Anything else I can help you with?”"
"6.If no, end the call politely."


                
            ),
            tools=[update_name, update_phone],
        )

    async def on_enter(self) -> None: #life cycle method for Livekit to use automatically when the session starts
        agent_name = self.__class__.__name__
        logger.info(f"entering task {agent_name}")

        userdata: UserData = self.session.userdata
        chat_ctx = self.chat_ctx.copy()
        chat_ctx.add_message(
            role="system",
            content=f"Your name is Alisha. Current user data is {userdata.summarize()}",
        )
        await self.update_chat_ctx(chat_ctx) # method accessed from the parent class
        self.session.generate_reply(tool_choice="none")

    @function_tool()
    async def update_appointment_time(
        self,
        time: Annotated[str, Field(description="The appointment time")], # giving descp/metadata about the time variable
        # good practice usually helpful for developers
        context: RunContext[UserData],
    ) -> str:
        """Called when the user provides their appointment time."""
        userdata = context.userdata
        userdata.appointment_time = time
        if not userdata.customer_name or not userdata.customer_phone:
            return "Please provide your name and phone number first."
        if not userdata.appointment_time:
            return "Please provide appointment time first."
        logger.info(f"Name: {userdata.customer_name}, Phone: {userdata.customer_phone}, Time: {userdata.appointment_time}")
        return (
            f"appointment confirmed for {userdata.customer_name} at {userdata.appointment_time}. "
            f"We will contact you at {userdata.customer_phone} if needed."
        )