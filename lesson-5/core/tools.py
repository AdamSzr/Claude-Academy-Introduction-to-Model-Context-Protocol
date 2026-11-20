import json
from mcp.types import TextContent
from mcp_client import MCPClient


async def get_all_tools(clients: dict) -> list[dict]:
    """Pobiera listę wszystkich narzędzi ze wszystkich klientów MCP."""

    tools = []
    for client in clients.values():
        for t in await client.list_tools():
            tools.append({
                "name": t.name,
                "description": t.description or "",
                # Schemat parametrów narzędzia (format JSON Schema)
                "input_schema": t.input_schema or {},
            })
    return tools


async def _find_client_for_tool(clients: dict, tool_name: str) -> MCPClient | None:
    """Znajduje klienta MCP, który posiada narzędzie o danej nazwie."""

    for client in clients.values():
        tools = await client.list_tools()
        if any(t.name == tool_name for t in tools):
            return client
    return None


async def execute_tool_calls(clients: dict, response) -> list[dict]:
    """
    Wykonuje wszystkie wywołania narzędzi z odpowiedzi modelu.
    Zwraca listę wyników gotowych do dodania do historii rozmowy.
    """

    results = []

    for i, tc in enumerate(response.tool_calls):
        tool_name = tc.function.name
        tool_input = tc.function.arguments
        tool_id = getattr(tc, "id", f"call_{i}")

        # Szukamy serwera MCP który ma to narzędzie
        client = await _find_client_for_tool(clients, tool_name)

        if not client:
            results.append({
                "tool_use_id": tool_id,
                "tool_name": tool_name,
                "content": f"Narzędzie '{tool_name}' nie zostało znalezione.",
            })
            continue

        try:
            # Wywołujemy narzędzie na serwerze MCP
            tool_output = await client.call_tool(tool_name, tool_input)

            # Wyciągamy tekstową treść z wyniku
            texts = [item.text for item in tool_output.content if isinstance(item, TextContent)]
            content = texts[0] if len(texts) == 1 else json.dumps(texts)

        except Exception as e:
            content = f"Błąd podczas wykonywania narzędzia '{tool_name}': {e}"
            print(content)

        results.append({
            "tool_use_id": tool_id,
            "tool_name": tool_name,
            "content": content,
        })

    return results
