import json
from typing import Optional, Literal, List, Any, Dict
from mcp.types import CallToolResult, Tool, TextContent
from mcp_client import MCPClient


class ToolManager:
    @classmethod
    async def get_all_tools(cls, clients: dict[str, MCPClient]) -> list[dict]:
        """Gets all tools from the provided clients."""
        tools = []
        for client in clients.values():
            tool_models = await client.list_tools()
            for t in tool_models:
                input_schema = (
                    getattr(t, "input_schema", None)
                    or getattr(t, "inputSchema", None)
                    or {}
                )
                tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": t.name,
                            "description": t.description or "",
                            "parameters": input_schema,
                        },
                        "name": t.name,
                        "description": t.description or "",
                        "input_schema": input_schema,
                    }
                )
        return tools

    @classmethod
    async def _find_client_with_tool(
        cls, clients: list[MCPClient], tool_name: str
    ) -> Optional[MCPClient]:
        """Finds the first client that has the specified tool."""
        for client in clients:
            tools = await client.list_tools()
            tool = next((t for t in tools if t.name == tool_name), None)
            if tool:
                return client
        return None

    @classmethod
    def _build_tool_result_part(
        cls,
        tool_use_id: str,
        tool_name: str,
        text: str,
        status: Literal["success"] | Literal["error"],
    ) -> dict:
        """Builds a tool result part dictionary."""
        return {
            "tool_use_id": tool_use_id,
            "tool_name": tool_name,
            "type": "tool_result",
            "content": text,
            "is_error": status == "error",
        }

    @classmethod
    async def execute_tool_requests(
        cls, clients: dict[str, MCPClient], response: Any
    ) -> List[dict]:
        """Executes a list of tool requests against the provided clients."""
        tool_requests = []

        # Check for Ollama tool_calls
        tool_calls = getattr(response, "tool_calls", None)
        if tool_calls is None and hasattr(response, "message"):
            tool_calls = getattr(response.message, "tool_calls", None)

        if tool_calls:
            for i, tc in enumerate(tool_calls):
                func = getattr(tc, "function", None)
                if func:
                    tool_requests.append(
                        {
                            "id": getattr(tc, "id", f"call_{i}"),
                            "name": func.name,
                            "input": func.arguments,
                        }
                    )
        # Check for Anthropic-style content blocks
        elif hasattr(response, "content") and isinstance(response.content, list):
            for block in response.content:
                if getattr(block, "type", None) == "tool_use":
                    tool_requests.append(
                        {
                            "id": getattr(block, "id", ""),
                            "name": getattr(block, "name", ""),
                            "input": getattr(block, "input", {}),
                        }
                    )

        tool_result_blocks: list[dict] = []
        for tool_request in tool_requests:
            tool_use_id = tool_request["id"]
            tool_name = tool_request["name"]
            tool_input = tool_request["input"]

            client = await cls._find_client_with_tool(
                list(clients.values()), tool_name
            )

            if not client:
                tool_result_part = cls._build_tool_result_part(
                    tool_use_id, tool_name, "Could not find that tool", "error"
                )
                tool_result_blocks.append(tool_result_part)
                continue

            try:
                tool_output: CallToolResult | None = await client.call_tool(
                    tool_name, tool_input
                )
                items = []
                if tool_output:
                    items = tool_output.content
                content_list = [
                    item.text for item in items if isinstance(item, TextContent)
                ]
                content_text = (
                    content_list[0]
                    if len(content_list) == 1
                    else json.dumps(content_list)
                )

                is_err = False
                if tool_output:
                    is_err = bool(
                        getattr(
                            tool_output,
                            "is_error",
                            getattr(tool_output, "isError", False),
                        )
                    )

                tool_result_part = cls._build_tool_result_part(
                    tool_use_id,
                    tool_name,
                    content_text,
                    "error" if is_err else "success",
                )
            except Exception as e:
                error_message = f"Error executing tool '{tool_name}': {e}"
                print(error_message)
                tool_result_part = cls._build_tool_result_part(
                    tool_use_id,
                    tool_name,
                    json.dumps({"error": error_message}),
                    "error",
                )

            tool_result_blocks.append(tool_result_part)
        return tool_result_blocks
