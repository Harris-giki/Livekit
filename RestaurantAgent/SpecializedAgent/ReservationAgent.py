from typing import Annotated
from pydantic import Field
from livekit.agents.llm import function_tool
from livekit.agents.voice import Agent
from livekit.plugins import groq
from common_functions import RunContext_T, update_name, update_phone
from RestaurantAgent.SpecializedAgent.data import UserData
from config import logger

class SpecializedAgent(Agent):
    def __init__(self, menu: str) -> None:
        super().__init__(
            instructions=(
                f"You are a friendly restaurant receptionist and reservation agent. The menu is: {menu}\n"
                "Your job is to greet callers, help them make reservations, collect their name, phone number, and reservation time, "
                "and confirm details. If they want takeaway, guide them to the takeaway agent."
            ),
            tools=[update_name, update_phone],
            llm=groq.LLM(model="llama3-8b-8192", parallel_tool_calls=False),
            tts=groq.TTS(model="playai-tts", voice="Arista-PlayAI"),
        )
        self.menu = menu

    async def on_enter(self) -> None:
        agent_name = self.__class__.__name__
        logger.info(f"entering task {agent_name}")

        userdata: UserData = self.session.userdata
        chat_ctx = self.chat_ctx.copy()
        chat_ctx.add_message(
            role="system",
            content=f"You are {agent_name} agent. Current user data is {userdata.summarize()}",
        )
        await self.update_chat_ctx(chat_ctx)
        self.session.generate_reply(tool_choice="none")

    @function_tool()
    async def update_reservation_time(
        self,
        time: Annotated[str, Field(description="The reservation time")],
        context: RunContext_T,
    ) -> str:
        """Called when the user provides their reservation time.
        Confirm the time with the user before calling the function."""
        userdata = context.userdata
        userdata.reservation_time = time
        return f"The reservation time is updated to {time}"

    @function_tool()
    async def confirm_reservation(self, context: RunContext_T) -> str:
        """Called when the user confirms the reservation."""
        userdata = context.userdata
        if not userdata.customer_name or not userdata.customer_phone:
            return "Please provide your name and phone number first."
        if not userdata.reservation_time:
            return "Please provide reservation time first."
        return (
            f"Reservation confirmed for {userdata.customer_name} at {userdata.reservation_time}. "
            f"We will contact you at {userdata.customer_phone} if needed."
        )