from typing import Any
from mcp_client import MCPClient
from core.tools import ToolManager

class Chat:
    def __init__(
        self,
        claude_service: Any = None,
        clients: dict[str, MCPClient] = None,
        llm_service: Any = None,
    ):
        service = llm_service or claude_service
        self.llm_service = service
        self.claude_service = service
        self.clients: dict[str, MCPClient] = clients or {}
        self.messages: list[dict] = []

    async def _process_query(self, query: str):
        self.messages.append({"role": "user", "content": query})

    async def run(
        self,
        query: str,
    ) -> str:
        final_text_response = ""

        await self._process_query(query)

        while True:
            response = self.llm_service.chat(
                messages=self.messages,
                tools=await ToolManager.get_all_tools(self.clients),
            )

            self.llm_service.add_assistant_message(self.messages, response)

            if response.stop_reason == "tool_use":
                print(self.llm_service.text_from_message(response))
                tool_result_parts = await ToolManager.execute_tool_requests(
                    self.clients, response
                )

                self.llm_service.add_user_message(
                    self.messages, tool_result_parts
                )
            else:
                final_text_response = self.llm_service.text_from_message(
                    response
                )
                break

        return final_text_response
