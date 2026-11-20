from core.tools import get_all_tools, execute_tool_calls


class Chat:
    """
    Bazowa klasa czatu — zarządza pętlą rozmowy z modelem.
    Obsługuje wielokrotne wywołania narzędzi (agentic loop).
    """

    def __init__(self, llm_service, clients: dict):
        self.llm = llm_service          # Serwis komunikacji z modelem (Ollama)
        self.clients = clients          # Słownik klientów MCP (serwery narzędzi)
        self.messages = []              # Historia rozmowy (user / assistant / tool)

    async def _prepare_query(self, query: str):
        """Przygotowuje zapytanie użytkownika — może być nadpisane w podklasie."""
        self.messages.append({"role": "user", "content": query})

    async def run(self, query: str) -> str:
        """
        Uruchamia pętlę agentową:
        1. Wysyła wiadomość do modelu
        2. Jeśli model chce użyć narzędzia — wykonuje je i wysyła wynik z powrotem
        3. Powtarza do momentu gdy model wyśle finalną odpowiedź tekstową
        """

        await self._prepare_query(query)
        tools = await get_all_tools(self.clients)

        while True:
            response = self.llm.chat(messages=self.messages, tools=tools)
            self.llm.add_assistant_message(self.messages, response)

            if response.stop_reason == "tool_use":
                # Model chce wywołać narzędzie — wykonujemy je i dodajemy wynik do historii
                print(self.llm.get_text(response))
                tool_results = await execute_tool_calls(self.clients, response)
                self.llm.add_tool_results(self.messages, tool_results)
            else:
                # Model zakończył — zwracamy finalną odpowiedź
                return self.llm.get_text(response)
