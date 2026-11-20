import asyncio
import sys
import os
from contextlib import AsyncExitStack
from dotenv import load_dotenv

from mcp_client import MCPClient
from core.ollama_service import OllamaService
from core.cli_chat import CliChat
from core.cli import CliApp

# Ładujemy zmienne z pliku .env
load_dotenv()

# Konfiguracja modelu Ollama
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:2b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")


async def main():
    # Inicjalizujemy serwis Ollama (połączenie z lokalnym modelem)
    llm = OllamaService(model=OLLAMA_MODEL, host=OLLAMA_HOST)

    # Opcjonalne dodatkowe serwery MCP przekazane jako argumenty wiersza poleceń
    # Np.: python main.py moj_serwer.py
    extra_server_scripts = sys.argv[1:]

    async with AsyncExitStack() as stack:
        # Uruchamiamy domyślny serwer MCP z dokumentami
        doc_client = await stack.enter_async_context(
            MCPClient(command=sys.executable, args=["mcp_server.py"])
        )

        # Słownik wszystkich klientów MCP (serwer dokumentów + opcjonalne dodatkowe)
        clients = {"doc_client": doc_client}

        for i, script in enumerate(extra_server_scripts):
            client = await stack.enter_async_context(
                MCPClient(command=sys.executable, args=[script])
            )
            clients[f"client_{i}"] = client

        # Tworzymy czat i uruchamiamy interfejs CLI
        chat = CliChat(doc_client=doc_client, clients=clients, llm_service=llm)
        cli = CliApp(chat)
        await cli.initialize()
        await cli.run()


if __name__ == "__main__":
    # Na Windows potrzebny jest inny event loop dla asyncio
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
