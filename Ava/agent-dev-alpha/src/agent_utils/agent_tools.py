import httpx
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional
from livekit.agents import RunContext, function_tool


@dataclass
class Message:
    type: str
    blocking: bool


@dataclass
class Server:
    url: str
    headers: Optional[Dict[str, str]] = None


@dataclass
class RadianceTool:
    id: str
    createdAt: datetime
    updatedAt: datetime
    type: str
    function: dict
    messages: Optional[List[Message]]
    orgId: str
    server: Server


def build_raw_tools(raw_tools: list | None):
    if not raw_tools:
        return None

    def create_http_tool(tool: RadianceTool):
        # Create HTTP tool handler function
        async def http_tool_handler(raw_arguments: dict[str, object], context: RunContext):
            try:
                await context.session.generate_reply(
                    instructions=f'You are about to  call a tool for {tool.get("description")} let the user know it will take a moment to process the request.'
                )

                url = tool.get("server").get("url")
                headers = tool.get("server").get("headers") or {}

                data = {
                    "message": {
                        "toolCalls": [{"function": {"arguments": {**raw_arguments}}}]
                    }
                }

                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.post(url, json=data, headers=headers)

                return response.json()
            except Exception as e:
                print("[Radiance] ---> Error", e)
                return f"Error: {e}"

        # Return the function tool
        return function_tool(http_tool_handler, raw_schema=tool.get('function'))

    # Add dynamic tools to the agent
    return [create_http_tool(tool) for tool in raw_tools if tool.get('type') == 'function']