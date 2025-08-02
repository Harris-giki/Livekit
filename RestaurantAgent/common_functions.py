from typing import Annotated
from pydantic import Field
from livekit.agents.llm import function_tool
from livekit.agents.voice import Agent, RunContext
# Run-context is a generic class from livekit that can hold the session-related data 
from SpecializedAgent.data import UserData

@function_tool()
async def update_name(
    name: Annotated[str, Field(description="The customer's name")],
    context:RunContext[UserData]
) -> str:
    """Called when the user provides their name."""
    userdata = context.userdata
    userdata.customer_name = name
    return f"The name is updated to {name}"


@function_tool()
async def update_phone(
    phone: Annotated[str, Field(description="The customer's phone number")],
    context: RunContext[UserData],
) -> str:
    """Called when the user provides their phone number."""
    userdata = context.userdata
    userdata.customer_phone = phone
    return f"The phone number is updated to {phone}"


@function_tool()
async def to_greeter(context: RunContext[UserData]) -> Agent:
    """Called when user asks any unrelated questions or requests
    any other services not in your job description.
    Sends the user to the main reservation agent."""
    reservation_agent = context.userdata.agents.get("MainAgent")  # or "reservation" if that's the key
    if reservation_agent is None:
        return "Reservation agent not available."
    await context.session.switch_agent(reservation_agent)
    return reservation_agent