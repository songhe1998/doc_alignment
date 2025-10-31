# Chatbot Integration - Quick Start

## 5-Minute Setup

### 1. API is Running ✅
```
http://localhost:5072/api
```

### 2. Simplest Integration (Copy & Paste)

```python
import requests

def align_documents(doc1_text, doc2_text, method="section"):
    """Call the document alignment API."""
    response = requests.post('http://localhost:5072/api/align', json={
        "doc1": {"text": doc1_text, "filename": "doc1.txt"},
        "doc2": {"text": doc2_text, "filename": "doc2.txt"},
        "method": method
    })
    return response.json()

# Use it in your chatbot
result = align_documents(user_doc1, user_doc2)

if result["success"]:
    # Show results to user
    for alignment in result["alignments"]:
        print(f"Section: {alignment['doc1_title']} <-> {alignment['doc2_title']}")
        print(f"Difference: {alignment['differences']}")
```

### 3. Methods Available

| Method | Speed | Best For |
|--------|-------|----------|
| `section` | Fast | Structured documents |
| `topic_template` | Medium | NDAs, Contracts |
| `topic_direct` | Medium | Any documents |

### 4. Response Format

```json
{
  "success": true,
  "alignments_found": 5,
  "alignments": [
    {
      "doc1_title": "Definitions",
      "doc2_title": "Terms",
      "confidence": "high",
      "differences": "..."
    }
  ]
}
```

## That's It!

Your chatbot can now align documents. See `API_USAGE.md` for more details.

## Test It

```bash
python test_api.py
```

