from mcp.types import PromptMessage
from core.chat import Chat
from mcp_client import MCPClient


class CliChat(Chat):
    """
    Rozszerzona wersja czatu dla interfejsu CLI.
    Dodaje obsługę zasobów (@dokument) i komend (/ prompt).
    """

    def __init__(self, doc_client: MCPClient, clients: dict, llm_service):
        super().__init__(llm_service=llm_service, clients=clients)
        # Klient MCP obsługujący dokumenty i prompty
        self.doc_client = doc_client

    # --- Metody pomocnicze do pobierania danych z serwera MCP ---

    async def list_prompts(self):
        return await self.doc_client.list_prompts()

    async def list_docs_ids(self):
        return await self.doc_client.read_resource("docs://documents")

    async def get_doc_content(self, doc_id: str) -> str:
        return await self.doc_client.read_resource(f"docs://documents/{doc_id}")

    # --- Obsługa wiadomości użytkownika ---

    async def _extract_mentioned_docs(self, query: str) -> str:
        """
        Szuka w zapytaniu wzmianek @dokument i pobiera ich treść.
        Np. 'Co jest w @report.pdf?' → pobiera treść report.pdf.
        """
        # Wyciągamy słowa zaczynające się od "@"
        mentions = {word[1:] for word in query.split() if word.startswith("@")}
        if not mentions:
            return ""

        doc_ids = await self.list_docs_ids()
        context = ""
        for doc_id in doc_ids:
            if doc_id in mentions:
                content = await self.get_doc_content(doc_id)
                context += f'\n<document id="{doc_id}">\n{content}\n</document>\n'

        return context

    async def _handle_slash_command(self, query: str) -> bool:
        """
        Obsługuje komendy zaczynające się od '/'.
        Np. '/summarize report.pdf' → pobiera prompt z serwera i dodaje do historii.
        Zwraca True jeśli komenda została obsłużona.
        """
        if not query.startswith("/"):
            return False

        parts = query.split()
        command = parts[0][1:]  # Usuwa "/" z początku
        doc_id = parts[1] if len(parts) > 1 else ""

        prompt_messages = await self.doc_client.get_prompt(command, {"doc_id": doc_id})
        self.messages += _convert_prompt_messages(prompt_messages)
        return True

    async def _prepare_query(self, query: str):
        """
        Przygotowuje zapytanie użytkownika:
        - Jeśli zaczyna się od '/' — obsługuje jako komendę
        - W przeciwnym razie buduje pełny prompt z kontekstem dokumentów
        """
        if await self._handle_slash_command(query):
            return

        # Pobieramy treść dokumentów wspomnianych przez @
        context = await self._extract_mentioned_docs(query)

        prompt = f"""
Odpowiedz na pytanie użytkownika.

Pytanie: {query}

Kontekst (dokumenty wymienione przez @):
{context if context else "(brak — użyj dostępnych narzędzi jeśli potrzebujesz danych)"}

Zasady:
- Jeśli treść dokumentu jest w kontekście powyżej, użyj jej bezpośrednio.
- Jeśli dokumentu nie ma w kontekście, użyj dostępnych narzędzi aby go pobrać.
- Odpowiedz zwięźle i na temat. Nie wspominaj o kontekście ani narzędziach.
"""
        self.messages.append({"role": "user", "content": prompt})


# --- Funkcje pomocnicze ---

def _convert_prompt_messages(prompt_messages: list[PromptMessage]) -> list[dict]:
    """Konwertuje listę PromptMessage z MCP na format wiadomości dla modelu."""
    result = []
    for msg in prompt_messages:
        role = "user" if msg.role == "user" else "assistant"
        # Obsługujemy zarówno obiektowy jak i słownikowy format treści
        content = msg.content
        text = getattr(content, "text", None) or (content.get("text", "") if isinstance(content, dict) else "")
        result.append({"role": role, "content": text})
    return result
