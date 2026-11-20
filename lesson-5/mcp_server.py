from mcp.server import MCPServer
from pydantic import Field

# Tworzymy serwer MCP o nazwie "DocumentMCP"
mcp = MCPServer("DocumentMCP", log_level="ERROR")

# Prosta baza dokumentów trzymana w pamięci (słownik: id → treść)
docs = {
    "deposition.md":  "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf":     "The report details the state of a 20m condenser tower.",
    "financials.docx":"These financials outline the project's budget and expenditures",
    "outlook.pdf":    "This document presents the projected future performance of the system",
    "plan.md":        "The plan outlines the steps for the project's implementation.",
    "spec.txt":       "These specifications define the technical requirements for the equipment",
}


@mcp.tool(
    name="read_doc_contents",
    description="Reads the contents of a document and returns it as a string",
)
def read_document(doc_id: str = Field(description="The ID of the document to read.")):
    """Zwraca treść dokumentu o podanym ID."""
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found.")
    return docs[doc_id]


@mcp.tool(
    name="edit_doc_content",
    description="Edit a document by replacing a string in its content with a new string",
)
def edit_document(
    doc_id: str = Field(description="ID of the document to edit"),
    old_str: str = Field(description="Text to replace (must match exactly, including whitespace)"),
    new_str: str = Field(description="New text to insert in place of the old text"),
):
    """Zastępuje fragment treści dokumentu nowym tekstem."""
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found.")
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
    return docs[doc_id]


if __name__ == "__main__":
    mcp.run()
