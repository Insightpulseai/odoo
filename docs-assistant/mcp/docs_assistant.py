#!/usr/bin/env python3
"""
MCP Tool for Docs Assistant
Kapa.ai-style documentation Q&A integration for Claude Code
"""

import os
import json
import requests
from typing import List, Optional
from mcp import Client, StdioServerParameters
from mcp.client import create_session
import asyncio

class DocsAssistantMCP:
    """MCP tool for interacting with the Docs Assistant API"""
    
    def __init__(self, api_base_url: str = None, api_key: str = None):
        self.api_base_url = api_base_url or os.getenv("DOCS_ASSISTANT_API_URL", "http://localhost:8000")
        self.api_key = api_key or os.getenv("DOCS_ASSISTANT_API_KEY")
        self.default_project = os.getenv("DOCS_ASSISTANT_PROJECT", "odoo-ce")
        
        if not self.api_key:
            raise ValueError("DOCS_ASSISTANT_API_KEY environment variable is required")
    
    async def ask_docs(self, question: str, project: Optional[str] = None) -> dict:
        """Ask a question to the documentation assistant"""
        project_slug = project or self.default_project
        
        try:
            response = requests.post(
                f"{self.api_base_url}/v1/chat",
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "project_slug": project_slug,
                    "question": question,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "answer": result["answer"],
                    "citations": result["citations"],
                    "metadata": result["metadata"]
                }
            else:
                return {
                    "error": f"API error: {response.status_code} - {response.text}",
                    "answer": "I couldn't connect to the documentation assistant. Please try again later."
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Connection error: {str(e)}",
                "answer": "I couldn't connect to the documentation assistant. Please check if the service is running."
            }
    
    async def search_docs(self, query: str, project: Optional[str] = None, limit: int = 10) -> dict:
        """Search documentation without generating an answer"""
        project_slug = project or self.default_project
        
        try:
            response = requests.post(
                f"{self.api_base_url}/v1/search",
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "project_slug": project_slug,
                    "query": query,
                    "limit": limit
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "results": result["results"],
                    "metadata": result["metadata"]
                }
            else:
                return {
                    "error": f"API error: {response.status_code} - {response.text}",
                    "results": []
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Connection error: {str(e)}",
                "results": []
            }
    
    async def submit_feedback(self, answer_id: str, rating: int, comment: Optional[str] = None) -> dict:
        """Submit feedback for an answer"""
        try:
            response = requests.post(
                f"{self.api_base_url}/v1/feedback",
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "answer_id": answer_id,
                    "rating": rating,
                    "comment": comment
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return {"status": "success", "message": "Feedback submitted"}
            else:
                return {"status": "error", "message": f"Failed to submit feedback: {response.text}"}
                
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Connection error: {str(e)}"}

# MCP Server Implementation
async def main():
    """MCP server main function"""
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "docs_assistant_mcp"]
    )
    
    async with create_session(server_params) as session:
        client = Client(session)
        
        # Register tools
        await client.initialize()
        
        # Tool definitions
        tools = [
            {
                "name": "ask_docs",
                "description": "Ask questions about Odoo, n8n, or other technical documentation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "The question to ask about the documentation"
                        },
                        "project": {
                            "type": "string",
                            "description": "Project slug (default: 'odoo-ce')",
                            "default": "odoo-ce"
                        }
                    },
                    "required": ["question"]
                }
            },
            {
                "name": "search_docs",
                "description": "Search documentation for specific information without generating an answer",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "project": {
                            "type": "string",
                            "description": "Project slug (default: 'odoo-ce')",
                            "default": "odoo-ce"
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of results",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "submit_feedback",
                "description": "Submit feedback for a documentation answer",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "answer_id": {
                            "type": "string",
                            "description": "The answer ID to provide feedback for"
                        },
                        "rating": {
                            "type": "number",
                            "description": "Rating from 1-5",
                            "minimum": 1,
                            "maximum": 5
                        },
                        "comment": {
                            "type": "string",
                            "description": "Optional comment about the answer"
                        }
                    },
                    "required": ["answer_id", "rating"]
                }
            }
        ]
        
        await client.list_tools()
        
        # Handle tool calls
        async for message in client:
            if message.type == "tools/call":
                tool_call = message.content
                assistant = DocsAssistantMCP()
                
                try:
                    if tool_call.name == "ask_docs":
                        result = await assistant.ask_docs(
                            question=tool_call.arguments["question"],
                            project=tool_call.arguments.get("project")
                        )
                        
                    elif tool_call.name == "search_docs":
                        result = await assistant.search_docs(
                            query=tool_call.arguments["query"],
                            project=tool_call.arguments.get("project"),
                            limit=tool_call.arguments.get("limit", 10)
                        )
                        
                    elif tool_call.name == "submit_feedback":
                        result = await assistant.submit_feedback(
                            answer_id=tool_call.arguments["answer_id"],
                            rating=tool_call.arguments["rating"],
                            comment=tool_call.arguments.get("comment")
                        )
                    
                    else:
                        result = {"error": f"Unknown tool: {tool_call.name}"}
                    
                    await client.send_tool_result(tool_call.callId, result)
                    
                except Exception as e:
                    error_result = {"error": f"Tool execution failed: {str(e)}"}
                    await client.send_tool_result(tool_call.callId, error_result)

if __name__ == "__main__":
    asyncio.run(main())

# Example usage for direct Python integration
async def example_usage():
    """Example of how to use the Docs Assistant MCP tool"""
    assistant = DocsAssistantMCP()
    
    # Ask a question about Odoo
    result = await assistant.ask_docs("How do I create a new Odoo module?")
    print("Answer:", result["answer"])
    
    if result.get("citations"):
        print("Sources:")
        for citation in result["citations"]:
            print(f"- {citation['document_title']}: {citation['content_snippet']}")
    
    # Search for specific information
    search_result = await assistant.search_docs("Odoo cron jobs configuration")
    print("Search results:", len(search_result["results"]))

# Quick test function
def test_connection():
    """Test connection to Docs Assistant API"""
    import requests
    
    api_url = os.getenv("DOCS_ASSISTANT_API_URL", "http://localhost:8000")
    api_key = os.getenv("DOCS_ASSISTANT_API_KEY")
    
    if not api_key:
        print("❌ DOCS_ASSISTANT_API_KEY not set")
        return False
    
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Docs Assistant API is healthy")
            return True
        else:
            print(f"❌ Docs Assistant API returned {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not connect to Docs Assistant API: {e}")
        return False

if __name__ == "__main__" and os.getenv("TEST_MODE"):
    test_connection()
