"""
Vercel serverless function for /api/ask endpoint
Kapa-style docs copilot with citation-first answers
"""
import os
import sys
from pathlib import Path

# Add tools/docs-crawler to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "docs-crawler"))

from api_ask import lambda_handler


def handler(request):
    """
    Vercel function handler

    Request body (JSON):
    {
      "question": "How do I...",
      "top_k": 6,
      "source_type": "odoo_docs",
      "visibility": "internal"
    }

    Response:
    {
      "question": str,
      "answer": str,
      "citations": [...],
      "confidence": float,
      "search_method": "hybrid",
      "model": "gpt-4o-mini",
      "tokens_used": int
    }
    """
    # Convert Vercel request to Lambda event format
    event = {
        'body': request.get_json(force=True, silent=True) or request.get_data(as_text=True)
    }

    # Call Lambda handler
    response = lambda_handler(event, None)

    return {
        'statusCode': response.get('statusCode', 200),
        'headers': response.get('headers', {}),
        'body': response.get('body', '{}')
    }
