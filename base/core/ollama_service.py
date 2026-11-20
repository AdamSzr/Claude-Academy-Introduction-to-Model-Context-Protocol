import json
from typing import Any, Dict, List, Optional
import ollama


class OllamaResponse:
    def __init__(self, raw_response: Any):
        self.raw_response = raw_response
        self.message = getattr(raw_response, "message", None)
        self.tool_calls = (
            getattr(self.message, "tool_calls", None) if self.message else None
        ) or []
        self.stop_reason = (
            "tool_use"
            if self.tool_calls
            else getattr(raw_response, "done_reason", "stop")
        )
        self.content = (
            getattr(self.message, "content", "") if self.message else ""
        )


class OllamaService:
    def __init__(
        self,
        model: str = "qwen3.5:2b",
        host: str = "http://localhost:11434",
    ):
        self.model = model
        self.host = host
        self.client = ollama.Client(host=host)

    def add_user_message(self, messages: list, message: Any):
        if isinstance(message, str):
            messages.append({"role": "user", "content": message})
        elif isinstance(message, dict):
            messages.append(message)
        elif isinstance(message, list):
            for item in message:
                if isinstance(item, dict) and item.get("type") == "tool_result":
                    messages.append(
                        {
                            "role": "tool",
                            "name": item.get("tool_name", ""),
                            "content": str(item.get("content", "")),
                        }
                    )
                elif isinstance(item, dict) and item.get("role") == "tool":
                    messages.append(item)
                else:
                    messages.append({"role": "user", "content": str(item)})
        else:
            messages.append({"role": "user", "content": str(message)})

    def add_assistant_message(self, messages: list, response: Any):
        if hasattr(response, "message"):
            msg = response.message
            tool_calls = getattr(msg, "tool_calls", None)
            if tool_calls:
                formatted_tool_calls = []
                for tc in tool_calls:
                    formatted_tool_calls.append(
                        {
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            }
                        }
                    )
                messages.append(
                    {
                        "role": "assistant",
                        "content": msg.content or "",
                        "tool_calls": formatted_tool_calls,
                    }
                )
            else:
                messages.append(
                    {
                        "role": "assistant",
                        "content": msg.content or "",
                    }
                )
        elif isinstance(response, dict):
            messages.append(response)
        else:
            messages.append({"role": "assistant", "content": str(response)})

    def text_from_message(self, response: Any) -> str:
        if hasattr(response, "message"):
            content = getattr(response.message, "content", "")
            if content:
                return content
            tool_calls = getattr(response.message, "tool_calls", None)
            if tool_calls:
                tool_names = [tc.function.name for tc in tool_calls]
                return f"[Użycie narzędzia: {', '.join(tool_names)}]"
            return ""
        if isinstance(response, str):
            return response
        if isinstance(response, dict):
            return response.get("content", "")
        return str(response)

    def chat(
        self,
        messages: list,
        system: Optional[str] = None,
        temperature: float = 0.7,
        stop_sequences: Optional[list] = None,
        tools: Optional[list] = None,
        **kwargs,
    ) -> OllamaResponse:
        chat_messages = []
        if system:
            chat_messages.append({"role": "system", "content": system})

        for msg in messages:
            if isinstance(msg, dict):
                chat_messages.append(msg)
            else:
                chat_messages.append({"role": "user", "content": str(msg)})

        chat_tools = None
        if tools:
            chat_tools = []
            for t in tools:
                if isinstance(t, dict):
                    if "type" in t and t["type"] == "function":
                        chat_tools.append(t)
                    elif "name" in t:
                        chat_tools.append(
                            {
                                "type": "function",
                                "function": {
                                    "name": t["name"],
                                    "description": t.get("description", ""),
                                    "parameters": t.get("input_schema", {}),
                                },
                            }
                        )
                    else:
                        chat_tools.append(t)
                else:
                    chat_tools.append(t)

        options = {"temperature": temperature}
        if stop_sequences:
            options["stop"] = stop_sequences

        raw = self.client.chat(
            model=self.model,
            messages=chat_messages,
            tools=chat_tools,
            options=options,
        )

        return OllamaResponse(raw)

