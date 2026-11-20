from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


class MCPClient:
    """
    Klient MCP — łączy się z serwerem narzędzi przez standardowe wejście/wyjście (stdio).
    Wspiera użycie jako menedżer kontekstu: `async with MCPClient(...) as client`.
    """

    def __init__(self, command: str, args: list[str], env: dict = None):
        self._command = command     # Np. "python" lub "uv"
        self._args = args           # Np. ["mcp_server.py"]
        self._env = env             # Opcjonalne zmienne środowiskowe
        self._session: ClientSession | None = None
        self._exit_stack = AsyncExitStack()

    async def connect(self):
        """Uruchamia serwer MCP jako podproces i nawiązuje sesję."""

        server_params = StdioServerParameters(
            command=self._command,
            args=self._args,
            env=self._env,
        )

        # Otwieramy transport stdio (strumień wejścia i wyjścia do podprocesu)
        read_stream, write_stream = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        # Tworzymy sesję MCP i inicjalizujemy protokół
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await self._session.initialize()

    async def list_tools(self) -> list[types.Tool]:
        """Pobiera listę narzędzi dostępnych na serwerze MCP."""
        result = await self._session.list_tools()
        return result.tools

    async def call_tool(self, tool_name: str, tool_input: dict) -> types.CallToolResult:
        """Wywołuje narzędzie na serwerze MCP i zwraca wynik."""
        return await self._session.call_tool(name=tool_name, arguments=tool_input)

    async def list_prompts(self) -> list[types.Prompt]:
        """Pobiera listę promptów zdefiniowanych na serwerze MCP."""
        # TODO: zaimplementować gdy serwer będzie obsługiwał prompty
        return []

    async def get_prompt(self, prompt_name: str, args: dict) -> list:
        """Pobiera konkretny prompt z serwera MCP."""
        # TODO: zaimplementować gdy serwer będzie obsługiwał prompty
        return []

    async def read_resource(self, uri: str):
        """Odczytuje zasób (np. listę dokumentów) z serwera MCP."""
        # TODO: zaimplementować gdy serwer będzie obsługiwał zasoby
        return []

    # --- Obsługa menedżera kontekstu (with) ---

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *_):
        await self._exit_stack.aclose()
        self._session = None
