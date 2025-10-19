"""Client wrapper that talks to the local Everly MCP server."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import anyio
from mcp.client.session_group import ClientSessionGroup
from mcp.client.stdio import StdioServerParameters
from mcp.types import CallToolResult, TextContent


PROJECT_ROOT = Path(__file__).resolve().parent
MCP_SERVER_PATH = PROJECT_ROOT / "mcp_server.py"


def _content_blocks_to_text(result: CallToolResult) -> str:
    if result.isError:
        return "❌ MCP server reported an error."

    texts: list[str] = []
    for block in result.content:
        if isinstance(block, TextContent):
            texts.append(block.text)
        else:
            text = getattr(block, "text", None)
            if text:
                texts.append(str(text))
    return "\n".join(texts).strip()


async def _call_tool_async(tool_name: str, arguments: dict[str, Any] | None) -> CallToolResult:
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(MCP_SERVER_PATH)],
        cwd=str(PROJECT_ROOT),
    )

    async with ClientSessionGroup() as group:
        session = await group.connect_to_server(params)
        try:
            result = await group.call_tool(tool_name, arguments or {})
        finally:
            await group.disconnect_from_server(session)
    return result


def _call_tool(tool_name: str, arguments: dict[str, Any] | None) -> str:
    try:
        result = anyio.run(_call_tool_async, tool_name, arguments)
    except Exception as exc:  # pragma: no cover - error surface for UI
        return f"Error calling MCP tool '{tool_name}': {exc}"

    return _content_blocks_to_text(result) or "Tool returned no content."


@dataclass
class EverlyAgent:
    """Facade offering high-level actions backed by MCP tools."""

    def analyze_screenshot_with_question(self, question: str) -> str:
        if not question:
            return "Please provide a question to analyze."

        return _call_tool("screenshot_analysis", {"question": question})

    def schedule_workout(self, date_text: str) -> str:
        return _call_tool("schedule_workout", {"date": date_text})

    def send_message_to_client(self, message: str) -> str:
        return _call_tool("send_message_to_client", {"message": message})


floating_app_agent = EverlyAgent()


