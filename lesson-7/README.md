# lesson 6 - Defining resources

## Test MCP server with MCP-Inspector
```bash
uv run mcp dev mcp_server.py
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

### Accessing resources

you should be able to run `python3 main.py` and ask 

```bash
What is the content of the document @<resource-name>?
```