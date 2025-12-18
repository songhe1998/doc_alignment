"""
Document Alignment API
RESTful API for legal document alignment - designed for chatbot integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv
import openai
import PyPDF2
from io import BytesIO
import base64
from topic_services import (
    run_topic_template_alignment,
    run_topic_direct_alignment,
)
from openai_helper import create_openai_client

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for chatbot integration

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

def extract_text_from_file(file_data, filename):
    """Extract text from uploaded file (TXT or PDF)."""
    if filename.endswith('.txt'):
        return file_data.decode('utf-8')
    elif filename.endswith('.pdf'):
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_data))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Error extracting PDF: {str(e)}")
    else:
        raise ValueError("Unsupported file format")

def extract_text_from_base64(base64_data, filename):
    """Extract text from base64 encoded file."""
    file_data = base64.b64decode(base64_data)
    return extract_text_from_file(file_data, filename)

def section_based_alignment(api_key, doc1_text, doc2_text):
    """Perform section-based alignment."""
    
    # Initialize client with proper configuration
    client = create_openai_client(api_key)
    
    max_len = 12000
    doc1_preview = doc1_text[:max_len]
    doc2_preview = doc2_text[:max_len]
    
    prompt = f"""Compare these two documents and identify aligned sections/topics.

DOCUMENT 1:
{doc1_preview}

DOCUMENT 2:
{doc2_preview}

Analyze both documents and create alignments. Return a JSON array where each object has:
- "doc1_section": section identifier from doc1
- "doc2_section": section identifier from doc2
- "doc1_title": topic/title from doc1
- "doc2_title": topic/title from doc2
- "confidence": "high", "medium", or "low"
- "differences": key differences between these sections

Return ONLY the JSON array, nothing else."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
            temperature=0.3
        )
        
        json_str = response.choices[0].message.content.strip()
        
        if "```json" in json_str:
            json_start = json_str.find("```json") + 7
            json_end = json_str.find("```", json_start)
            json_str = json_str[json_start:json_end].strip()
        elif json_str.startswith("```"):
            json_str = json_str[3:-3].strip()
        
        alignments = json.loads(json_str)
        
        return {
            'method': 'section_based',
            'success': True,
            'alignments_found': len(alignments),
            'alignments': alignments
        }
    except Exception as e:
        return {
            'method': 'section_based',
            'success': False,
            'error': str(e),
            'alignments_found': 0,
            'alignments': []
        }

def _assign_alignment_metadata(alignments):
    for i, alignment in enumerate(alignments):
        alignment.setdefault('id', i)
    return alignments


def topic_template_alignment(api_key, doc1_text, doc2_text):
    """Topic-based alignment using standard legal topics."""
    try:
        result = run_topic_template_alignment(api_key, doc1_text, doc2_text)
        result['method'] = 'topic_template'
        result['success'] = True
        result['alignments'] = _assign_alignment_metadata(result.get('alignments', []))
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'method': 'topic_template',
            'success': False,
            'error': str(e),
            'alignments_found': 0,
            'alignments': []
        }


def topic_direct_alignment(api_key, doc1_text, doc2_text):
    """Topic-based alignment by directly extracting topics."""
    try:
        result = run_topic_direct_alignment(api_key, doc1_text, doc2_text)
        result['method'] = 'topic_direct'
        result['success'] = True
        result['alignments'] = _assign_alignment_metadata(result.get('alignments', []))
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'method': 'topic_direct',
            'success': False,
            'error': str(e),
            'alignments_found': 0,
            'alignments': []
        }


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Document Alignment API',
        'version': '1.0.0'
    })

@app.route('/api/align', methods=['POST'])
def align_documents():
    """
    Main alignment endpoint.
    
    Accepts either:
    1. Multipart form data with file uploads
    2. JSON with base64 encoded documents
    
    Request (multipart/form-data):
    - doc1: file
    - doc2: file
    - method: string (section|topic_template|topic_direct)
    - api_key: string (optional, uses env var if not provided)
    
    Request (application/json):
    {
        "doc1": {
            "content": "base64_encoded_content",
            "filename": "doc1.pdf"
        },
        "doc2": {
            "content": "base64_encoded_content",
            "filename": "doc2.pdf"
        },
        "method": "section|topic_template|topic_direct",
        "api_key": "optional_openai_key"
    }
    
    Response:
    {
        "success": true,
        "method": "section_based",
        "alignments_found": 5,
        "alignments": [...],
        "doc1_name": "nda_1.pdf",
        "doc2_name": "nda_2.pdf"
    }
    """
    try:
        # Get API key
        api_key = request.form.get('api_key') or request.json.get('api_key') if request.is_json else None
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'OpenAI API key not provided'
            }), 400
        
        # Handle file uploads (multipart/form-data)
        if request.files:
            if 'doc1' not in request.files or 'doc2' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'Both doc1 and doc2 files are required'
                }), 400
            
            doc1_file = request.files['doc1']
            doc2_file = request.files['doc2']
            method = request.form.get('method', 'section')
            
            doc1_name = doc1_file.filename
            doc2_name = doc2_file.filename
            
            doc1_text = extract_text_from_file(doc1_file.read(), doc1_name)
            doc2_text = extract_text_from_file(doc2_file.read(), doc2_name)
        
        # Handle JSON with base64 encoded documents
        elif request.is_json:
            data = request.json
            
            if 'doc1' not in data or 'doc2' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Both doc1 and doc2 are required'
                }), 400
            
            doc1_name = data['doc1'].get('filename', 'document1.txt')
            doc2_name = data['doc2'].get('filename', 'document2.txt')
            
            # Check if content is already text or base64
            if 'content' in data['doc1']:
                doc1_content = data['doc1']['content']
                if doc1_name.endswith('.txt') and not doc1_content.startswith('data:'):
                    doc1_text = doc1_content
                else:
                    doc1_text = extract_text_from_base64(doc1_content, doc1_name)
            elif 'text' in data['doc1']:
                doc1_text = data['doc1']['text']
            else:
                return jsonify({
                    'success': False,
                    'error': 'doc1 must have "content" or "text" field'
                }), 400
            
            if 'content' in data['doc2']:
                doc2_content = data['doc2']['content']
                if doc2_name.endswith('.txt') and not doc2_content.startswith('data:'):
                    doc2_text = doc2_content
                else:
                    doc2_text = extract_text_from_base64(doc2_content, doc2_name)
            elif 'text' in data['doc2']:
                doc2_text = data['doc2']['text']
            else:
                return jsonify({
                    'success': False,
                    'error': 'doc2 must have "content" or "text" field'
                }), 400
            
            method = data.get('method', 'section')
        else:
            return jsonify({
                'success': False,
                'error': 'Request must be multipart/form-data or application/json'
            }), 400
        
        # Perform alignment
        if method == 'section' or method == 'section_based':
            result = section_based_alignment(api_key, doc1_text, doc2_text)
        elif method == 'topic_template':
            result = topic_template_alignment(api_key, doc1_text, doc2_text)
        elif method == 'topic_direct':
            result = topic_direct_alignment(api_key, doc1_text, doc2_text)
        else:
            return jsonify({
                'success': False,
                'error': f'Invalid method: {method}. Must be section, topic_template, or topic_direct'
            }), 400
        
        # Add document names to result
        result['doc1_name'] = doc1_name
        result['doc2_name'] = doc2_name
        
        return jsonify(result)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/methods', methods=['GET'])
def get_methods():
    """
    Get available alignment methods.
    
    Response:
    {
        "methods": [
            {
                "id": "section",
                "name": "Section-Based Alignment",
                "description": "Aligns documents by matching section numbers and titles"
            },
            ...
        ]
    }
    """
    return jsonify({
        'methods': [
            {
                'id': 'section',
                'name': 'Section-Based Alignment',
                'description': 'Aligns documents by matching section numbers and titles',
                'speed': 'fast'
            },
            {
                'id': 'topic_template',
                'name': 'Topic-Based (Template)',
                'description': 'Uses standard legal topics as a template for alignment',
                'speed': 'medium'
            },
            {
                'id': 'topic_direct',
                'name': 'Topic-Based (Direct)',
                'description': 'Extracts topics directly from documents and aligns semantically',
                'speed': 'medium'
            }
        ]
    })

if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5072))
    print(f"""
╔════════════════════════════════════════════════════════════╗
║            Document Alignment API                          ║
║                                                            ║
║  API Server: http://0.0.0.0:{port}                       ║
║  Endpoints:                                               ║
║    GET  /api/health   - Health check                      ║
║    GET  /api/methods  - List alignment methods            ║
║    POST /api/align    - Align two documents               ║
╚════════════════════════════════════════════════════════════╝
""")
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
