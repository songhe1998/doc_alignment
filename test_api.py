"""
Test script for Document Alignment API
Demonstrates how a chatbot would call the API
"""

import requests
import json

API_BASE_URL = "http://localhost:5072/api"

def test_health():
    """Test health check endpoint."""
    print("=" * 80)
    print("TEST 1: Health Check")
    print("=" * 80)
    
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_get_methods():
    """Test get methods endpoint."""
    print("=" * 80)
    print("TEST 2: Get Available Methods")
    print("=" * 80)
    
    response = requests.get(f"{API_BASE_URL}/methods")
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Available Methods:")
    for method in result['methods']:
        print(f"  - {method['id']}: {method['name']}")
        print(f"    {method['description']}")
        print(f"    Speed: {method['speed']}\n")

def test_align_with_text():
    """Test alignment with text documents."""
    print("=" * 80)
    print("TEST 3: Align Documents (Text)")
    print("=" * 80)
    
    doc1_text = """
NON-DISCLOSURE AGREEMENT

This Agreement is entered into as of [Date].

1. Definitions
   "Confidential Information" means all technical and business information.
   
2. Obligations
   The Receiving Party agrees to hold Confidential Information in strict confidence.
   
3. Term
   This Agreement shall remain in effect for 2 years.
"""

    doc2_text = """
MUTUAL NDA

Agreement made on [Date].

Section 1: Terms
   Confidential info includes proprietary data and materials.
   
Section 2: Confidentiality
   Both parties shall maintain confidentiality of disclosed information.
   
Section 3: Duration
   Valid for 24 months from execution.
"""
    
    payload = {
        "doc1": {
            "text": doc1_text,
            "filename": "nda1.txt"
        },
        "doc2": {
            "text": doc2_text,
            "filename": "nda2.txt"
        },
        "method": "section"
    }
    
    print("Sending request to API...")
    response = requests.post(f"{API_BASE_URL}/align", json=payload)
    print(f"Status Code: {response.status_code}")
    
    result = response.json()
    
    if result.get('success'):
        print(f"\n✅ SUCCESS!")
        print(f"Method: {result['method']}")
        print(f"Alignments Found: {result['alignments_found']}")
        print(f"Documents: {result['doc1_name']} <-> {result['doc2_name']}\n")
        
        print("Alignments:")
        for i, alignment in enumerate(result['alignments'], 1):
            print(f"\n  {i}. {alignment.get('doc1_title', 'N/A')} <-> {alignment.get('doc2_title', 'N/A')}")
            print(f"     Sections: {alignment.get('doc1_section', 'N/A')} <-> {alignment.get('doc2_section', 'N/A')}")
            print(f"     Confidence: {alignment.get('confidence', 'N/A')}")
            if 'differences' in alignment:
                print(f"     Differences: {alignment['differences'][:100]}...")
    else:
        print(f"\n❌ ERROR: {result.get('error')}")
    print()

def test_align_with_files():
    """Test alignment with PDF files."""
    print("=" * 80)
    print("TEST 4: Align Documents (PDF Files)")
    print("=" * 80)
    
    try:
        with open('nda_1.pdf', 'rb') as f1, open('nda_2.pdf', 'rb') as f2:
            files = {
                'doc1': f1,
                'doc2': f2
            }
            data = {
                'method': 'topic_direct'
            }
            
            print("Uploading PDFs to API...")
            response = requests.post(f"{API_BASE_URL}/align", files=files, data=data)
            print(f"Status Code: {response.status_code}")
            
            result = response.json()
            
            if result.get('success'):
                print(f"\n✅ SUCCESS!")
                print(f"Method: {result['method']}")
                print(f"Alignments Found: {result['alignments_found']}")
                print(f"\nFirst 3 topics:")
                for i, alignment in enumerate(result['alignments'][:3], 1):
                    print(f"\n  {i}. {alignment.get('topic_name', 'N/A')}")
                    doc1_secs = alignment.get('doc1_sections', [])
                    doc2_secs = alignment.get('doc2_sections', [])
                    print(f"     Doc1 sections: {len(doc1_secs)}")
                    print(f"     Doc2 sections: {len(doc2_secs)}")
            else:
                print(f"\n❌ ERROR: {result.get('error')}")
    except FileNotFoundError:
        print("⚠️  PDF files not found. Skipping file upload test.")
    print()

def chatbot_example():
    """Example of how a chatbot would use the API."""
    print("=" * 80)
    print("CHATBOT INTEGRATION EXAMPLE")
    print("=" * 80)
    
    # Simulate chatbot receiving two documents from user
    print("\n🤖 Chatbot: I'll analyze these two documents for you...")
    print("🤖 Chatbot: This will take about 10-20 seconds...\n")
    
    doc1 = """NON-DISCLOSURE AGREEMENT
This Agreement is made on [Date].
1. Definitions: Confidential Information means proprietary data.
2. Obligations: Receiving Party shall maintain confidentiality.
3. Term: This agreement is valid for 2 years."""
    
    doc2 = """MUTUAL NDA
Agreement dated [Date].
Section 1: Terms - Confidential info includes trade secrets.
Section 2: Restrictions - Both parties must keep info confidential.
Section 3: Duration - Valid for 24 months."""
    
    # Chatbot calls API
    try:
        response = requests.post(
            f"{API_BASE_URL}/align",
            json={
                "doc1": {"text": doc1, "filename": "user_nda.txt"},
                "doc2": {"text": doc2, "filename": "user_contract.txt"},
                "method": "section"
            },
            timeout=60
        )
        
        result = response.json()
        
        if result.get('success'):
            # Chatbot presents results to user
            print(f"🤖 Chatbot: I found {result['alignments_found']} aligned sections!")
            print(f"🤖 Chatbot: Here's what I discovered:\n")
            
            for i, alignment in enumerate(result['alignments'][:3], 1):
                print(f"   {i}. Section '{alignment.get('doc1_title')}' in your first document")
                print(f"      aligns with '{alignment.get('doc2_title')}' in your second document")
                print(f"      Confidence: {alignment.get('confidence')}")
                print(f"      Key difference: {alignment.get('differences', 'N/A')[:80]}...\n")
            
            print(f"🤖 Chatbot: Would you like me to explain any specific section?")
        else:
            print(f"🤖 Chatbot: Sorry, I encountered an error: {result.get('error')}")
    
    except requests.exceptions.RequestException as e:
        print(f"🤖 Chatbot: Sorry, I couldn't connect to the alignment service: {e}")
    
    print()

if __name__ == "__main__":
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║       Document Alignment API - Test Script                ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    # Check if API is running
    try:
        requests.get(f"{API_BASE_URL}/health", timeout=2)
        print("✅ API server is running!\n")
    except requests.exceptions.RequestException:
        print("❌ API server is not running!")
        print("Please start it first: python api.py\n")
        exit(1)
    
    # Run tests
    test_health()
    test_get_methods()
    test_align_with_text()
    test_align_with_files()
    chatbot_example()
    
    print("=" * 80)
    print("ALL TESTS COMPLETED!")
    print("=" * 80)

