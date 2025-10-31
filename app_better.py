"""
Legal Document Alignment Web Application - IMPROVED VERSION
Features side-by-side document view with color-coded alignments
"""

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import json
from dotenv import load_dotenv
import openai
import PyPDF2
from io import BytesIO
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

# Color palette for alignments
COLORS = [
    '#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF',
    '#FFD4E5', '#FFF5BA', '#C9BAFF', '#FFBAF3', '#BAF3FF',
    '#FFE5BA', '#E5BAFF', '#BAFFE5', '#FFB3E6', '#B3E6FF',
    '#FFE6B3', '#E6B3FF', '#B3FFE6', '#FFB3D9', '#B3D9FF'
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

def split_into_sections(text):
    """Split document into sections based on common patterns."""
    # Try to identify sections by numbered patterns
    patterns = [
        r'^(\d+\.[\d\.]*)\s+([^\n]+)',  # 1. or 1.1 style
        r'^([A-Z][^\n]{0,100}):',        # TITLE: style
        r'^(Article\s+\d+)',             # Article N style
        r'^(Section\s+\d+)',             # Section N style
    ]
    
    sections = []
    lines = text.split('\n')
    current_section = {'title': 'Introduction', 'content': '', 'start_line': 0}
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            current_section['content'] += '\n'
            continue
            
        matched = False
        for pattern in patterns:
            match = re.match(pattern, line, re.MULTILINE)
            if match:
                # Save previous section
                if current_section['content'].strip():
                    current_section['end_line'] = i
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    'title': line[:100],
                    'content': line + '\n',
                    'start_line': i
                }
                matched = True
                break
        
        if not matched:
            current_section['content'] += line + '\n'
    
    # Add last section
    if current_section['content'].strip():
        current_section['end_line'] = len(lines)
        sections.append(current_section)
    
    return sections

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index_better.html')

@app.route('/align', methods=['POST'])
def align_documents():
    """Handle document alignment request with improved visualization."""
    try:
        print(f"\n{'='*80}")
        print(f"🚀 NEW ALIGNMENT REQUEST (BETTER VERSION)")
        print(f"{'='*80}")
        
        # Get API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        # Check if files were uploaded
        if 'doc1' not in request.files or 'doc2' not in request.files:
            return jsonify({'error': 'Both documents are required'}), 400
        
        doc1 = request.files['doc1']
        doc2 = request.files['doc2']
        method = request.form.get('method', 'section')
        
        print(f"📄 Doc1: {doc1.filename}")
        print(f"📄 Doc2: {doc2.filename}")
        print(f"🎯 Method: {method}")
        
        # Validate files
        if not (allowed_file(doc1.filename) and allowed_file(doc2.filename)):
            return jsonify({'error': 'Only TXT and PDF files are allowed'}), 400
        
        # Extract text from files
        doc1_text = extract_text_from_file(doc1.read(), doc1.filename)
        doc2_text = extract_text_from_file(doc2.read(), doc2.filename)
        print(f"✅ Doc1: {len(doc1_text)} chars")
        print(f"✅ Doc2: {len(doc2_text)} chars")
        
        # Split documents into sections
        doc1_sections = split_into_sections(doc1_text)
        doc2_sections = split_into_sections(doc2_text)
        print(f"✅ Doc1: {len(doc1_sections)} sections")
        print(f"✅ Doc2: {len(doc2_sections)} sections")
        
        # Perform alignment based on selected method
        if method == 'section':
            result = section_based_alignment(api_key, doc1_text, doc2_text, doc1_sections, doc2_sections)
        elif method == 'topic_template':
            result = topic_template_alignment(api_key, doc1_text, doc2_text, doc1_sections, doc2_sections)
        elif method == 'topic_direct':
            result = topic_direct_alignment(api_key, doc1_text, doc2_text, doc1_sections, doc2_sections)
        else:
            return jsonify({'error': 'Invalid alignment method'}), 400
        
        # Add full documents and sections for visualization
        result['doc1_text'] = doc1_text
        result['doc2_text'] = doc2_text
        result['doc1_sections'] = doc1_sections
        result['doc2_sections'] = doc2_sections
        result['doc1_name'] = doc1.filename
        result['doc2_name'] = doc2.filename
        
        print(f"✅ COMPLETE: {result.get('alignments_found', 0)} alignments")
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def section_based_alignment(api_key, doc1_text, doc2_text, doc1_sections, doc2_sections):
    """Perform section-based alignment with color mapping."""
    print(f"\n{'='*80}")
    print(f"📋 SECTION-BASED ALIGNMENT")
    print(f"{'='*80}")
    import openai
    
    # Initialize client
    try:
        client = openai.OpenAI(api_key=api_key)
    except TypeError as e:
        import httpx
        client = openai.OpenAI(api_key=api_key, http_client=httpx.Client())
    
    # Truncate if too long
    max_len = 12000
    doc1_preview = doc1_text[:max_len]
    doc2_preview = doc2_text[:max_len]
    
    prompt = f"""Compare these two documents and identify aligned sections/topics.

DOCUMENT 1:
{doc1_preview}

DOCUMENT 2:
{doc2_preview}

Analyze both documents and create alignments. For each alignment, specify which section titles or numbers are being matched.

Return a JSON array where each object has:
- "doc1_section": section identifier from doc1 (e.g., "1. Definition" or "Introduction")
- "doc2_section": section identifier from doc2
- "topic": the common topic/subject
- "confidence": "high", "medium", or "low"
- "differences": key differences between these sections (string)

Return ONLY the JSON array, nothing else."""

    try:
        print(f"🤖 Calling OpenAI...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
            temperature=0.3
        )
        
        json_str = response.choices[0].message.content.strip()
        
        # Clean JSON
        if "```json" in json_str:
            json_start = json_str.find("```json") + 7
            json_end = json_str.find("```", json_start)
            json_str = json_str[json_start:json_end].strip()
        elif json_str.startswith("```"):
            json_str = json_str[3:-3].strip()
        
        alignments = json.loads(json_str)
        
        # Add colors and section mappings
        for i, alignment in enumerate(alignments):
            alignment['color'] = COLORS[i % len(COLORS)]
            alignment['id'] = i
        
        print(f"✅ Found {len(alignments)} alignments")
        
        return {
            'method': 'Section-Based Alignment',
            'alignments_found': len(alignments),
            'alignments': alignments
        }
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {
            'method': 'Section-Based Alignment',
            'alignments_found': 0,
            'alignments': [],
            'error': str(e)
        }

def topic_template_alignment(api_key, doc1_text, doc2_text, doc1_sections, doc2_sections):
    """Topic-based alignment using standard legal topics."""
    print(f"\n{'='*80}")
    print(f"🏷️  TOPIC-TEMPLATE ALIGNMENT")
    print(f"{'='*80}")
    import openai
    
    try:
        client = openai.OpenAI(api_key=api_key)
    except TypeError:
        import httpx
        client = openai.OpenAI(api_key=api_key, http_client=httpx.Client())
    
    max_len = 12000
    doc1 = doc1_text[:max_len]
    doc2 = doc2_text[:max_len]
    
    # Identify document type
    type_prompt = f"""What type of legal document is this? Return one word (e.g., NDA, Contract, License, Agreement, etc.)

Document:
{doc1[:2000]}

Return ONLY the document type, nothing else."""

    try:
        type_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": type_prompt}],
            max_tokens=50,
            temperature=0.3
        )
        doc_type = type_response.choices[0].message.content.strip().replace('.', '')
        print(f"✅ Document type: {doc_type}")
    except Exception as e:
        print(f"⚠️ Could not identify type: {e}")
        doc_type = "Legal Document"
    
    # Get standard topics and map sections
    prompt = f"""This is a {doc_type}. Identify standard topics and map sections from each document.

DOCUMENT 1:
{doc1}

DOCUMENT 2:
{doc2}

Return a JSON array where each object represents ONE topic:
{{
  "topic_name": "Standard topic name",
  "doc1_sections": ["Section X: Title", ...] or [] if not present,
  "doc2_sections": ["Section Y: Title", ...] or [] if not present,
  "doc1_summary": "How doc1 addresses this topic",
  "doc2_summary": "How doc2 addresses this topic",
  "differences": "Main differences",
  "is_standard": true/false
}}

Return ONLY the JSON array."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,
            temperature=0.3
        )
        
        raw = response.choices[0].message.content.strip()
        
        # Clean JSON
        if "```json" in raw:
            start = raw.find("```json") + 7
            end = raw.find("```", start)
            raw = raw[start:end].strip()
        elif raw.startswith("```"):
            raw = raw[3:-3].strip()
        
        topics = json.loads(raw)
        
        # Add colors
        for i, topic in enumerate(topics):
            topic['color'] = COLORS[i % len(COLORS)]
            topic['id'] = i
        
        print(f"✅ Found {len(topics)} topics")
        
        return {
            'method': 'Topic-Based Alignment (Template)',
            'document_type': doc_type,
            'alignments_found': len(topics),
            'alignments': topics
        }
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {
            'method': 'Topic-Based Alignment (Template)',
            'document_type': doc_type,
            'alignments_found': 0,
            'alignments': [],
            'error': str(e)
        }

def topic_direct_alignment(api_key, doc1_text, doc2_text, doc1_sections, doc2_sections):
    """Topic-based alignment by identifying topics and mapping sections."""
    print(f"\n{'='*80}")
    print(f"🎯 TOPIC-DIRECT ALIGNMENT")
    print(f"{'='*80}")
    import openai
    
    try:
        client = openai.OpenAI(api_key=api_key)
    except TypeError:
        import httpx
        client = openai.OpenAI(api_key=api_key, http_client=httpx.Client())
    
    max_len = 12000
    doc1 = doc1_text[:max_len]
    doc2 = doc2_text[:max_len]
    
    prompt = f"""Analyze these two documents and identify 6-10 main topics.

DOCUMENT 1:
{doc1}

DOCUMENT 2:
{doc2}

For each topic, identify which sections from each document relate to it.

Return a JSON array where each object represents ONE topic:
{{
  "topic_name": "Name of the topic",
  "doc1_sections": ["Section X: Title", ...] or [],
  "doc2_sections": ["Section Y: Title", ...] or [],
  "doc1_summary": "Summary of how doc1 handles this",
  "doc2_summary": "Summary of how doc2 handles this",
  "differences": "Key differences"
}}

Return ONLY the JSON array."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,
            temperature=0.3
        )
        
        raw = response.choices[0].message.content.strip()
        
        # Clean JSON
        if "```json" in raw:
            start = raw.find("```json") + 7
            end = raw.find("```", start)
            raw = raw[start:end].strip()
        elif raw.startswith("```"):
            raw = raw[3:-3].strip()
        
        topics = json.loads(raw)
        
        # Add colors
        for i, topic in enumerate(topics):
            topic['color'] = COLORS[i % len(COLORS)]
            topic['id'] = i
        
        print(f"✅ Found {len(topics)} topics")
        
        return {
            'method': 'Direct Topic-Based Alignment',
            'alignments_found': len(topics),
            'alignments': topics
        }
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {
            'method': 'Direct Topic-Based Alignment',
            'alignments_found': 0,
            'alignments': [],
            'error': str(e)
        }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5071))
    print(f"""
╔════════════════════════════════════════════════════════════╗
║     Legal Document Alignment Tool (IMPROVED VERSION)      ║
║                                                            ║
║  Features: Side-by-side view with color-coded alignment   ║
║  Server: http://0.0.0.0:{port}                           ║
╚════════════════════════════════════════════════════════════╝
""")
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)



