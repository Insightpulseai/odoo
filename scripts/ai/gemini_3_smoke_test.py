#!/usr/bin/env python3
"""
Gemini 3 Smoke Test
Powered by InsightPulseAI — GenAI SDK Integration

This script verifies the connectivity and response quality of the 
new Google GenAI SDK (google-genai) and Gemini 3.x models.
"""

import os
import sys
from typing import Optional

try:
    from google import genai
except ImportError:
    print("❌ Error: 'google-genai' SDK not found. Have you installed requirements-ai.txt?")
    sys.exit(1)

def run_smoke_test(api_key: Optional[str] = None):
    print("🔍 Starting Gemini 3 Smoke Test...")
    
    # Initialize client (uses GEMINI_API_KEY env var by default)
    try:
        client = genai.Client(api_key=api_key)
        
        # Test model: gemini-3-flash-preview (as per April 2026 documentation)
        model_id = "gemini-3-flash-preview"
        prompt = "Explain the 'Adapt First' doctrine for AI coding assistants in 10 words."
        
        print(f"📡 Sending request to {model_id}...")
        
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        
        if response.text:
            print(f"✅ Response received:\n   \"{response.text.strip()}\"")
            print("🚀 Google GenAI SDK integration verified.")
        else:
            print("⚠️ Response received but text field is empty.")
            
    except Exception as e:
        print(f"❌ Smoke test failed: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("1. Ensure GEMINI_API_KEY is set in your environment.")
        print("2. Check for network connectivity to Gemini API endpoints.")
        print(f"3. Verify that the '{model_id}' model is available in your region.")

if __name__ == "__main__":
    # Allow manual override via command line arg
    target_key = sys.argv[1] if len(sys.argv) > 1 else os.getenv("GEMINI_API_KEY")
    run_smoke_test(target_key)
