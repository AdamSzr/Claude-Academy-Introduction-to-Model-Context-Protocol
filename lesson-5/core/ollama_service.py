import ollama


class OllamaResponse:
    """Opakowuje surową odpowiedź z biblioteki ollama w wygodny obiekt."""

    def __init__(self, raw):
        self.message = raw.message

        # Lista wywołań narzędzi (może być pusta)
        self.tool_calls = getattr(self.message, "tool_calls", None) or []

        # Treść tekstowa odpowiedzi (może być pusta gdy model wywołuje narzędzie)
        self.content = self.message.content or ""

        # Powód zatrzymania: "tool_use" gdy model chce użyć narzędzia, "stop" gdy skończył
        self.stop_reason = "tool_use" if self.tool_calls else raw.done_reason


class OllamaService:
    """Serwis do komunikacji z lokalnym modelem przez Ollama."""

    def __init__(self, model: str = "qwen3.5:2b", host: str = "http://localhost:11434"):
        self.model = model
        self.client = ollama.Client(host=host)

    def chat(self, messages: list, tools: list = None, system: str = None) -> OllamaResponse:
        """Wysyła wiadomości do modelu i zwraca odpowiedź."""

        chat_messages = []

        # Opcjonalny system prompt (instrukcja globalna dla modelu)
        if system:
            chat_messages.append({"role": "system", "content": system})

        chat_messages.extend(messages)

        # Konwersja narzędzi MCP do formatu Ollama (OpenAI function-calling)
        chat_tools = None
        if tools:
            chat_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t.get("description", ""),
                        "parameters": t.get("input_schema", {}),
                    },
                }
                for t in tools
            ]

        raw = self.client.chat(model=self.model, messages=chat_messages, tools=chat_tools)
        return OllamaResponse(raw)

    def add_assistant_message(self, messages: list, response: OllamaResponse):
        """Dodaje odpowiedź asystenta do historii rozmowy."""

        msg: dict = {"role": "assistant", "content": response.content}

        # Jeśli model wywołał narzędzia, dołączamy ich listę do wiadomości
        if response.tool_calls:
            msg["tool_calls"] = [
                {"function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in response.tool_calls
            ]

        messages.append(msg)

    def add_tool_results(self, messages: list, tool_results: list):
        """Dodaje wyniki wywołań narzędzi do historii rozmowy."""

        # Każdy wynik narzędzia to osobna wiadomość z rolą "tool"
        for result in tool_results:
            messages.append({
                "role": "tool",
                "name": result["tool_name"],
                "content": result["content"],
            })

    def get_text(self, response: OllamaResponse) -> str:
        """Zwraca czytelny tekst z odpowiedzi modelu."""

        if response.content:
            return response.content

        # Gdy model nie wygenerował tekstu, tylko wywołał narzędzie — podaj info
        if response.tool_calls:
            names = [tc.function.name for tc in response.tool_calls]
            return f"[Użycie narzędzia: {', '.join(names)}]"

        return ""
