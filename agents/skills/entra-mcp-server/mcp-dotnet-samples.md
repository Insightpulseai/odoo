# Microsoft MCP .NET Samples — Reference

> Source: https://github.com/microsoft/mcp-dotnet-samples
> Relevance: MCP server implementation patterns for .NET/Azure integration

## Available Samples

| Sample | Purpose | Relevance |
|--------|---------|-----------|
| **Awesome Copilot** | Retrieves GitHub Copilot customization files | Copilot integration pattern |
| **Markdown to HTML** | Converts markdown to HTML via MCP | Simple MCP server template |
| **Outlook Email** | Sends emails through Outlook via MCP | Mail integration pattern — relevant for Zoho/Outlook host lane |
| **To-do List** | Manages to-do items via MCP | CRUD MCP server pattern |

## Why this matters for IPAI

These samples demonstrate how to build **.NET MCP servers** that can:

- Integrate with Microsoft services (Outlook, Copilot)
- Run alongside the Enterprise MCP Server (Entra)
- Be installed directly in VS Code / Visual Studio
- Follow the open MCP protocol standard

## Potential IPAI MCP servers to build

| Server | Purpose | Pattern from |
|--------|---------|-------------|
| `ipai-odoo-mcp` | Expose Odoo record operations as MCP tools | To-do List sample |
| `ipai-mail-mcp` | Send/read mail via Zoho/Outlook | Outlook Email sample |
| `ipai-copilot-mcp` | Serve IPAI Copilot customizations | Awesome Copilot sample |

## Resources

- [MCP Official Documentation](https://modelcontextprotocol.io)
- [MCP GitHub Repository](https://github.com/modelcontextprotocol)
- [Azure AI Community Discord](https://discord.gg/azure-ai)
