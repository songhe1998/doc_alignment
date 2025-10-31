# Document Alignment API - Usage Guide

## Overview
RESTful API for legal document alignment. Perfect for chatbot integration!

## Base URL
```
http://localhost:5072/api
```

## Endpoints

### 1. Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Document Alignment API",
  "version": "1.0.0"
}
```

---

### 2. Get Available Methods
```http
GET /api/methods
```

**Response:**
```json
{
  "methods": [
    {
      "id": "section",
      "name": "Section-Based Alignment",
      "description": "Aligns documents by matching section numbers and titles",
      "speed": "fast"
    },
    {
      "id": "topic_template",
      "name": "Topic-Based (Template)",
      "description": "Uses standard legal topics as a template for alignment",
      "speed": "medium"
    },
    {
      "id": "topic_direct",
      "name": "Topic-Based (Direct)",
      "description": "Extracts topics directly from documents and aligns semantically",
      "speed": "medium"
    }
  ]
}
```

---

### 3. Align Documents (Main Endpoint)
```http
POST /api/align
```

## Request Formats

### Option A: File Upload (multipart/form-data)

**Headers:**
```
Content-Type: multipart/form-data
```

**Form Data:**
- `doc1`: File (PDF or TXT)
- `doc2`: File (PDF or TXT)
- `method`: String (`section`, `topic_template`, or `topic_direct`)
- `api_key`: String (optional, uses env var if not provided)

**Example using cURL:**
```bash
curl -X POST http://localhost:5072/api/align \
  -F "doc1=@nda_1.pdf" \
  -F "doc2=@nda_2.pdf" \
  -F "method=section"
```

---

### Option B: JSON with Text Content (application/json)

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "doc1": {
    "text": "Full text of document 1...",
    "filename": "doc1.txt"
  },
  "doc2": {
    "text": "Full text of document 2...",
    "filename": "doc2.txt"
  },
  "method": "section",
  "api_key": "your-openai-key" 
}
```

**Example using cURL:**
```bash
curl -X POST http://localhost:5072/api/align \
  -H "Content-Type: application/json" \
  -d '{
    "doc1": {
      "text": "NON-DISCLOSURE AGREEMENT\n\nThis agreement...",
      "filename": "nda1.txt"
    },
    "doc2": {
      "text": "MUTUAL NDA\n\nThis mutual agreement...",
      "filename": "nda2.txt"
    },
    "method": "section"
  }'
```

---

### Option C: JSON with Base64 Encoded Files (application/json)

**Body:**
```json
{
  "doc1": {
    "content": "base64_encoded_pdf_content_here",
    "filename": "doc1.pdf"
  },
  "doc2": {
    "content": "base64_encoded_pdf_content_here",
    "filename": "doc2.pdf"
  },
  "method": "topic_direct"
}
```

---

## Response Format

**Success Response:**
```json
{
  "success": true,
  "method": "section_based",
  "alignments_found": 5,
  "doc1_name": "nda_1.pdf",
  "doc2_name": "nda_2.pdf",
  "alignments": [
    {
      "doc1_section": "1",
      "doc2_section": "1",
      "doc1_title": "Definitions",
      "doc2_title": "Terms",
      "confidence": "high",
      "differences": "Doc1 includes more detailed definitions..."
    },
    {
      "doc1_section": "2",
      "doc2_section": "2",
      "doc1_title": "Confidentiality Obligations",
      "doc2_title": "Disclosure Restrictions",
      "confidence": "high",
      "differences": "Both have similar obligations but Doc2 is more restrictive..."
    }
  ]
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message here"
}
```

---

## Chatbot Integration Examples

### Example 1: Python Chatbot Integration

```python
import requests

def align_documents_for_chatbot(doc1_text, doc2_text, method="section"):
    """
    Call document alignment API from chatbot.
    
    Args:
        doc1_text: Full text of first document
        doc2_text: Full text of second document
        method: Alignment method (section, topic_template, topic_direct)
    
    Returns:
        dict: Alignment results
    """
    url = "http://localhost:5072/api/align"
    
    payload = {
        "doc1": {
            "text": doc1_text,
            "filename": "document1.txt"
        },
        "doc2": {
            "text": doc2_text,
            "filename": "document2.txt"
        },
        "method": method
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# Usage in chatbot
user_doc1 = "NON-DISCLOSURE AGREEMENT\n\nThis agreement..."
user_doc2 = "MUTUAL NDA\n\nThis mutual agreement..."

result = align_documents_for_chatbot(user_doc1, user_doc2, method="section")

if result["success"]:
    print(f"Found {result['alignments_found']} alignments:")
    for alignment in result["alignments"]:
        print(f"  - {alignment['doc1_title']} <-> {alignment['doc2_title']}")
        print(f"    Confidence: {alignment['confidence']}")
        print(f"    Differences: {alignment['differences']}\n")
else:
    print(f"Error: {result['error']}")
```

---

### Example 2: JavaScript/Node.js Chatbot Integration

```javascript
async function alignDocuments(doc1Text, doc2Text, method = 'section') {
  const response = await fetch('http://localhost:5072/api/align', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      doc1: {
        text: doc1Text,
        filename: 'document1.txt'
      },
      doc2: {
        text: doc2Text,
        filename: 'document2.txt'
      },
      method: method
    })
  });
  
  return await response.json();
}

// Usage in chatbot
const doc1 = "NON-DISCLOSURE AGREEMENT\n\nThis agreement...";
const doc2 = "MUTUAL NDA\n\nThis mutual agreement...";

const result = await alignDocuments(doc1, doc2, 'section');

if (result.success) {
  console.log(`Found ${result.alignments_found} alignments:`);
  result.alignments.forEach(alignment => {
    console.log(`  ${alignment.doc1_title} <-> ${alignment.doc2_title}`);
    console.log(`  Confidence: ${alignment.confidence}`);
    console.log(`  Differences: ${alignment.differences}\n`);
  });
} else {
  console.error(`Error: ${result.error}`);
}
```

---

### Example 3: File Upload from Chatbot

```python
import requests

def align_pdf_files(pdf_path1, pdf_path2, method="section"):
    """Upload PDF files for alignment."""
    url = "http://localhost:5072/api/align"
    
    files = {
        'doc1': open(pdf_path1, 'rb'),
        'doc2': open(pdf_path2, 'rb')
    }
    
    data = {
        'method': method
    }
    
    response = requests.post(url, files=files, data=data)
    return response.json()

# Usage
result = align_pdf_files('nda_1.pdf', 'nda_2.pdf', method='topic_direct')
print(result)
```

---

## Response Examples by Method

### Section-Based Alignment Response
```json
{
  "success": true,
  "method": "section_based",
  "alignments_found": 4,
  "doc1_name": "nda1.pdf",
  "doc2_name": "nda2.pdf",
  "alignments": [
    {
      "doc1_section": "1",
      "doc2_section": "Section 1",
      "doc1_title": "Definitions",
      "doc2_title": "Interpretation",
      "confidence": "high",
      "differences": "Doc1 defines 10 terms while Doc2 defines 8..."
    }
  ]
}
```

### Topic-Template Alignment Response
```json
{
  "success": true,
  "method": "topic_template",
  "document_type": "NDA",
  "alignments_found": 8,
  "doc1_name": "nda1.pdf",
  "doc2_name": "nda2.pdf",
  "alignments": [
    {
      "topic_name": "Confidential Information Definition",
      "doc1_sections": ["Section 1: Definitions"],
      "doc2_sections": ["Clause 1.1: Terms"],
      "doc1_summary": "Defines confidential info as proprietary data...",
      "doc2_summary": "Similar definition with additional exclusions...",
      "differences": "Doc2 has broader exclusions for public information",
      "is_standard": true
    }
  ]
}
```

### Topic-Direct Alignment Response
```json
{
  "success": true,
  "method": "topic_direct",
  "alignments_found": 7,
  "doc1_name": "nda1.pdf",
  "doc2_name": "nda2.pdf",
  "alignments": [
    {
      "topic_name": "Disclosure Restrictions",
      "doc1_sections": ["Section 2: Obligations", "Section 3: Use Limitations"],
      "doc2_sections": ["Clause 2: Confidentiality Obligations"],
      "doc1_summary": "Prohibits disclosure except to employees...",
      "doc2_summary": "Similar restrictions but includes contractors...",
      "differences": "Doc2 allows disclosure to contractors under certain conditions"
    }
  ]
}
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request (missing parameters, invalid method) |
| 500 | Internal Server Error (processing failed) |

---

## Environment Variables

Set these in your `.env` file:

```env
OPENAI_API_KEY=your-openai-api-key-here
API_PORT=5072
```

---

## Starting the API Server

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API server
python api.py
```

The API will start on `http://localhost:5072`

---

## CORS

The API has CORS enabled by default, so you can call it from web-based chatbots or browser applications.

---

## Rate Limiting

Currently, there's no rate limiting. For production use, consider adding:
- Rate limiting middleware
- Authentication
- Request validation
- Logging and monitoring

---

## Best Practices for Chatbot Integration

1. **Handle Errors Gracefully**
   ```python
   try:
       result = align_documents(doc1, doc2)
       if result["success"]:
           # Process alignments
       else:
           # Show error to user
   except requests.exceptions.RequestException as e:
       # Handle network errors
   ```

2. **Show Progress to Users**
   - Alignment can take 5-30 seconds
   - Show a "Analyzing documents..." message

3. **Cache Results**
   - If users might request the same alignment multiple times
   - Cache by document content hash

4. **Validate Documents**
   - Check file size before uploading
   - Ensure documents have extractable text

5. **Choose the Right Method**
   - `section`: Fast, good for structured documents
   - `topic_template`: Best for known document types (NDAs, contracts)
   - `topic_direct`: Most flexible, works with any documents

---

## Testing

Test the API is working:

```bash
# Health check
curl http://localhost:5072/api/health

# Get methods
curl http://localhost:5072/api/methods

# Test alignment (with text)
curl -X POST http://localhost:5072/api/align \
  -H "Content-Type: application/json" \
  -d '{
    "doc1": {"text": "Test document 1", "filename": "test1.txt"},
    "doc2": {"text": "Test document 2", "filename": "test2.txt"},
    "method": "section"
  }'
```

---

## Support

For issues or questions:
- Check server logs for errors
- Ensure OpenAI API key is valid
- Verify documents contain extractable text

