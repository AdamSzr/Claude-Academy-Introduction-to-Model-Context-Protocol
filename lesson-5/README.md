# lesson 5 - Implementing a client

https://academy.claude.com/courses/introduction-to-model-context-protocol/implementing-a-client

## Test MCP Client with MCP-Inspector
```bash
uv run mcp_client.py
```
Expected result
```
[Tool(name='read_doc_contents', title=None, description='Reads the contents of a document and return it as a string', input_schema={'properties': {'doc_id': {'description': 'The ID of the document to read.', 'title': 'Doc Id', 'type': 'string'}}, 'required': ['doc_id'], 'type': 'object', 'title': 'read_documentArguments'}, execution=None, output_schema=None, icons=None, annotations=None, meta=None), Tool(name='edit_doc_content', title=None, description='Edit a document by replacing a string in the documents content with a new string', input_schema={'properties': {'doc_id': {'description': 'Id of the document that will be edited', 'title': 'Doc Id', 'type': 'string'}, 'old_str': {'description': 'The text to replace. Must match exacly, incliding whitespace.', 'title': 'Old Str', 'type': 'string'}, 'new_str': {'description': 'The new text to insert in place of the old text.', 'title': 'New Str', 'type': 'string'}}, 'required': ['doc_id', 'old_str', 'new_str'], 'type': 'object', 'title': 'edit_documentArguments'}, execution=None, output_schema=None, icons=None, annotations=None, meta=None)]
```

### Run the MCP application
```bash
python3 main.py
```

### Ask:
`What is the content of the document report.pdf?`

If everything is ok, you should see the following output:
```
"The report details the state of a 20m condenser tower."
```