# lesson 6 - Defining resources

## Test MCP server with MCP-Inspector
```bash
uv run mcp dev mcp_server.py
```

1. Go to Resources tab
2. Click `List Resouces`
3. You will see `list_docs` resource.
3. Use this resource to get the list of documents.

## Expected:
```json
{
  "contents": [
    {
      "uri": "docs://documents",
      "mimeType": "application/json",
      "text": "[\n  \"deposition.md\",\n  \"report.pdf\",\n  \"financials.docx\",\n  \"outlook.pdf\",\n  \"plan.md\",\n  \"spec.txt\"\n]"
    }
  ]
}
```

click Get
