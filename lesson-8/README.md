## Lesson 8 - Defining prompts

Implement in mcp_server.py

```python
@mcp.prompt(
  name="format",
  description="Rewrites the contents of the document in Markdown format."
)
def format_document(doc_id:str = Field(description="Id of the document to format")) -> list[base.Message]:
  prompt = f"""
  Your goal is to reformat a document to be written with markdown syntax.

  The id of the document you need to reformat is:
  <document_id>
  {doc_id}
  </document_id>

  Add in headers, bullet points, tables, etc as necessary. Feel free to add in structure.
  Use the 'edit_document' tool to edit the document. After the document has been reformatted...
  """
  return [ base.UserMessage(prompt) ]
```

### Test the result

1. Run server
```bash
uv run mcp dev mcp_server.py
```

2. Go to prompts tab
3. Get the available prompts, should be only one named "format"

4. Use the prompt with doc_id="outlook.pdf" and see the result:

```json
{
  "description": "Rewrites the contents of the document in Markdown format.",
  "messages": [
    {
      "role": "user",
      "content": {
        "type": "text",
        "text": "Your goal is to reformat a document to be written with markdown syntax.\n\nThe id of the document you need to reformat is:\n<document_id>\noutlook.pdf\n</document_id>\n\nAdd in headers, bullet points, tables, etc as necessary. Feel free to add in structure.\nUse the 'edit_document' tool to edit the document. After the document has been reformatted..."
      }
    }
  ]
}
```