# ClaudeAcademy-MCP

## Course:
https://academy.claude.com/courses/introduction-to-model-context-protocol

## Completion badge:
https://academy.claude.com/badges/795c66e2-f77e-432d-a13d-267309116527

## Course Overview
A practical, 9-lesson course for Python engineers on using the Model Context Protocol (MCP) to connect Claude to external tools and data sources without writing boilerplate integration code or manual JSON schemas. Through a hands-on project, you build a complete document management system featuring both an MCP server and an MCP client.

### Key Topics & Skills Covered:

MCP Architecture & Communication: How MCP decouples tool execution into specialized servers, its transport-agnostic messaging, and the end-to-end request-response flow between users, clients, external services, and Claude.

Building MCP Servers (Python SDK): Defining tools with Python decorators, type hints, and Field descriptions instead of raw JSON schemas, plus testing and debugging via the browser-based MCP Server Inspector.

Exposing Data & Workflows: Implementing read-only Resources (both static URIs and parameterized templates) and pre-crafted Prompts (e.g., for document formatting).

Building MCP Clients & UI Integration: Consuming server capabilities on the client side, handling JSON/text MIME types, and applying real-world patterns like UI autocomplete and chat context injection.

Architectural Decision-Making: Knowing when to use Tools (model-controlled), Resources (app-controlled), and Prompts (user-controlled).

### Course Structure (9 Lessons):

Introduction (2 lessons): MCP architecture and its core value proposition.

Hands-on with MCP servers (2 lessons): Building a tool-equipped server with the Python SDK and testing it in the Inspector.

Connecting with MCP clients (5 lessons): Building the client side, implementing resources and prompts, and wiring up the full application flow.


## Choosing the Right Primitive

Here's a quick decision guide:

- Need to give Claude new capabilities? Use tools
- Need to get data into your app for UI or context? Use resources
- Want to create predefined workflows for users? Use prompts

You can see all three primitives in action in Claude's official interface. The workflow buttons demonstrate prompts, the Google Drive integration shows resources in action, and when Claude executes code or performs calculations, it's using tools behind the scenes.

These are high-level guidelines to help you choose the right primitive for your specific use case. Each serves a different part of your application stack - tools serve the model, resources serve your app, and prompts serve your users.