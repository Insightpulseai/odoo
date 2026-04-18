import os
import sys

try:
    from azure.identity import DefaultAzureCredential
    from azure.ai.documentintelligence import DocumentIntelligenceClient
except ImportError:
    print("Error: Required packages are not installed.")
    print("Please run: pip install azure-ai-documentintelligence azure-identity")
    sys.exit(1)

def test_document_intelligence_entra():
    endpoint = os.getenv("AZURE_DI_ENDPOINT", "https://ipai-copilot-resource.cognitiveservices.azure.com/")

    print(f"Connecting to Endpoint: {endpoint}")
    print("Using Microsoft Entra ID (DefaultAzureCredential) for authentication...")
    
    credential = DefaultAzureCredential()
    client = DocumentIntelligenceClient(endpoint=endpoint, credential=credential)
    
    sample_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-layout.pdf"
    
    print(f"Submitting test document from: {sample_url}")
    
    # Corrected syntax based on inspect.signature
    body = {
        "urlSource": sample_url
    }
    
    try:
        poller = client.begin_analyze_document(
            model_id="prebuilt-layout",
            body=body
        )
        
        print("Analyzing (this may take a few seconds)...")
        result = poller.result()
        
        print("\n--- TEST SUCCESSFUL ---")
        print(f"Extracted {len(result.pages)} page(s).")
        
        for page in result.pages:
            words_count = len(page.words) if (hasattr(page, 'words') and page.words) else 0
            lines_count = len(page.lines) if (hasattr(page, 'lines') and page.lines) else 0
            print(f"Page {page.page_number} has {words_count} words and {lines_count} lines.")
            
    except Exception as e:
        print("\n--- TEST FAILED ---")
        print(f"Type: {type(e).__name__}")
        print(f"Error: {str(e)}")
        if "AuthenticationFailed" in str(e) or "Forbidden" in str(e):
             print("\nTroubleshooting:")
             print("1. Ensure you have run 'az login' locally.")
             print("2. Ensure your account has 'Cognitive Services User' role at the resource level.")

if __name__ == "__main__":
    test_document_intelligence_entra()
