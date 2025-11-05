"""
Legal Document Alignment Web Application
Allows users to compare documents using different alignment methods.
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import json
from dotenv import load_dotenv
import openai
from alignment import LegalDocumentAligner
from topic_alignment import TopicBasedAligner
import PyPDF2
from io import BytesIO

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

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/align', methods=['POST'])
def align_documents():
    """Handle document alignment request."""
    try:
        print(f"\n{'='*80}")
        print(f"🚀 NEW ALIGNMENT REQUEST")
        print(f"{'='*80}")
        
        # Get API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ ERROR: OpenAI API key not configured!")
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        print(f"✅ API key found: {api_key[:10]}...")
        
        # Check if files were uploaded
        if 'doc1' not in request.files or 'doc2' not in request.files:
            print("❌ ERROR: Missing document files!")
            return jsonify({'error': 'Both documents are required'}), 400
        
        doc1 = request.files['doc1']
        doc2 = request.files['doc2']
        method = request.form.get('method', 'section')
        
        print(f"📄 Doc1: {doc1.filename}")
        print(f"📄 Doc2: {doc2.filename}")
        print(f"🎯 Method: {method}")
        
        # Validate files
        if doc1.filename == '' or doc2.filename == '':
            print("❌ ERROR: Empty filename!")
            return jsonify({'error': 'Both documents must be selected'}), 400
        
        if not (allowed_file(doc1.filename) and allowed_file(doc2.filename)):
            print("❌ ERROR: Invalid file type!")
            return jsonify({'error': 'Only TXT and PDF files are allowed'}), 400
        
        # Extract text from files
        print(f"📄 Extracting text from files...")
        doc1_text = extract_text_from_file(doc1.read(), doc1.filename)
        doc2_text = extract_text_from_file(doc2.read(), doc2.filename)
        print(f"✅ Doc1 text: {len(doc1_text)} chars")
        print(f"✅ Doc2 text: {len(doc2_text)} chars")
        
        # Perform alignment based on selected method
        if method == 'section':
            result = section_based_alignment(api_key, doc1_text, doc2_text)
        elif method == 'topic_template':
            result = topic_template_alignment(api_key, doc1_text, doc2_text)
        elif method == 'topic_direct':
            result = topic_direct_alignment(api_key, doc1_text, doc2_text)
        else:
            print(f"❌ ERROR: Invalid method: {method}")
            return jsonify({'error': 'Invalid alignment method'}), 400
        
        print(f"\n✅ ALIGNMENT COMPLETE: {result.get('alignments_found', 0)} alignments found")
        return jsonify(result)
    
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def section_based_alignment(api_key, doc1_text, doc2_text):
    """Perform section-based alignment by passing full docs to LLM."""
    print(f"\n{'='*80}")
    print(f"📋 SECTION-BASED ALIGNMENT (FULL DOCUMENT)")
    print(f"{'='*80}")
    import openai
    
    # Initialize client with explicit settings to avoid proxy issues
    try:
        client = openai.OpenAI(api_key=api_key)
    except TypeError as e:
        # Fallback for older versions or proxy issues
        print(f"⚠️ Client init warning: {e}, trying alternative...")
        import httpx
        client = openai.OpenAI(
            api_key=api_key,
            http_client=httpx.Client()
        )
    
    # Truncate if too long
    max_len = 12000
    doc1_preview = doc1_text[:max_len] if len(doc1_text) > max_len else doc1_text
    doc2_preview = doc2_text[:max_len] if len(doc2_text) > max_len else doc2_text
    
    print(f"📄 Doc1: {len(doc1_text)} chars (using {len(doc1_preview)})")
    print(f"📄 Doc2: {len(doc2_text)} chars (using {len(doc2_preview)})")
    
    prompt = f"""Compare these two documents and identify aligned sections/topics.

DOCUMENT 1:
{doc1_preview}

DOCUMENT 2:
{doc2_preview}

Analyze both documents and create alignments. Return a JSON array where each object has:
- "doc1_section": section identifier from doc1 (e.g., "Section 1", "Clause 2")
- "doc2_section": section identifier from doc2
- "doc1_title": topic/title from doc1
- "doc2_title": topic/title from doc2
- "confidence": "high", "medium", or "low"
- "differences": key differences between these sections (string)

Return ONLY the JSON array, nothing else."""

    try:
        print(f"🤖 Calling OpenAI for alignment...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
            temperature=0.3
        )
        
        json_str = response.choices[0].message.content.strip()
        print(f"✅ Received response")
        
        # Clean JSON
        if "```json" in json_str:
            json_start = json_str.find("```json") + 7
            json_end = json_str.find("```", json_start)
            json_str = json_str[json_start:json_end].strip()
        elif json_str.startswith("```"):
            json_str = json_str[3:-3].strip()
        
        import json
        alignments = json.loads(json_str)
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

def topic_template_alignment(api_key, doc1_text, doc2_text):
    """Topic-based alignment using standard legal topics as a template."""
    print(f"\n{'='*80}")
    print(f"🏷️  TOPIC-TEMPLATE ALIGNMENT (TOPIC → SECTIONS)")
    print(f"{'='*80}")
    import openai
    import json
    
    # Initialize client with explicit settings to avoid proxy issues
    try:
        client = openai.OpenAI(api_key=api_key)
    except TypeError as e:
        # Fallback for older versions or proxy issues
        print(f"⚠️ Client init warning: {e}, trying alternative...")
        import httpx
        client = openai.OpenAI(
            api_key=api_key,
            http_client=httpx.Client()
        )
    
    # Truncate if needed
    max_len = 12000
    doc1 = doc1_text[:max_len]
    doc2 = doc2_text[:max_len]
    
    print(f"📄 Doc1: {len(doc1_text)} chars (using {len(doc1)})")
    print(f"📄 Doc2: {len(doc2_text)} chars (using {len(doc2)})")
    
    # First, identify document type and get standard topics
    print(f"🔍 Step 1: Identifying document type...")
    
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
        print(f"⚠️ Could not identify type, using 'Legal Document': {e}")
        doc_type = "Legal Document"
    
    # Now get standard topics for this document type and map sections
    prompt = f"""This is a {doc_type}. Identify the standard topics that typically appear in such documents, then map which sections from each document cover each topic.

DOCUMENT 1:
{doc1}

DOCUMENT 2:
{doc2}

For a {doc_type}, identify 8-12 standard legal topics, then show which sections cover each topic.

Return a JSON array where each object represents ONE topic:
{{
  "topic_name": "Standard topic name for this type of document",
  "topic_description": "What this topic typically covers in a {doc_type}",
  "doc1_sections": ["Section X: Title", ...] or [] if not present,
  "doc2_sections": ["Section Y: Title", ...] or [] if not present,
  "doc1_summary": "How doc1 addresses this topic" or "",
  "doc2_summary": "How doc2 addresses this topic" or "",
  "key_differences": "Main differences between the two documents for this topic",
  "is_standard": true if this is a typical topic for a {doc_type}, false if unique
}}

IMPORTANT:
- Use standard topics common to {doc_type}s (e.g., for NDAs: Confidential Info Definition, Disclosure Restrictions, Return Obligations, etc.)
- Include all standard topics even if only in one document
- Use actual section numbers from the documents
- Return ONLY the JSON array."""

    try:
        print(f"🤖 Step 2: Mapping standard topics to sections...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,
            temperature=0.3
        )
        
        raw = response.choices[0].message.content.strip()
        print(f"✅ Got response: {len(raw)} chars")
        
        # Clean JSON
        if "```json" in raw:
            start = raw.find("```json") + 7
            end = raw.find("```", start)
            raw = raw[start:end].strip()
        elif raw.startswith("```"):
            raw = raw[3:-3].strip()
        
        # Parse
        topics = json.loads(raw)
        print(f"✅ Parsed {len(topics)} standard topics")
        
        # Format results
        alignments = []
        standard_count = 0
        for i, topic in enumerate(topics):
            # Get all fields with defaults
            topic_name = str(topic.get('topic_name') or f'Topic {i+1}')
            topic_desc = str(topic.get('topic_description') or '')
            doc1_secs = topic.get('doc1_sections') or []
            doc2_secs = topic.get('doc2_sections') or []
            doc1_summary = str(topic.get('doc1_summary') or '')
            doc2_summary = str(topic.get('doc2_summary') or '')
            differences = str(topic.get('key_differences') or '')
            is_standard = topic.get('is_standard', True)
            
            if is_standard:
                standard_count += 1
            
            # Ensure sections are lists of strings
            if not isinstance(doc1_secs, list):
                doc1_secs = [str(doc1_secs)]
            doc1_secs = [str(s) for s in doc1_secs]
            
            if not isinstance(doc2_secs, list):
                doc2_secs = [str(doc2_secs)]
            doc2_secs = [str(s) for s in doc2_secs]
            
            # Determine presence and similarity
            in_doc1 = len(doc1_secs) > 0
            in_doc2 = len(doc2_secs) > 0
            
            if in_doc1 and in_doc2:
                similarity = 'high'
            elif in_doc1 or in_doc2:
                similarity = 'low'
            else:
                similarity = 'none'
            
            alignment = {
                'topic_name': topic_name,
                'topic_description': topic_desc,
                'doc1_sections': doc1_secs,
                'doc2_sections': doc2_secs,
                'doc1_summary': doc1_summary,
                'doc2_summary': doc2_summary,
                'similarity': similarity,
                'differences': differences,
                'in_doc1': in_doc1,
                'in_doc2': in_doc2,
                'is_standard': is_standard
            }
            
            alignments.append(alignment)
            
            marker = '⭐' if is_standard else '  '
            print(f"  {marker} {i+1}. {topic_name}")
            print(f"      Doc1: {len(doc1_secs)} sections | Doc2: {len(doc2_secs)} sections")
        
        print(f"✅ SUCCESS: {len(alignments)} topics ({standard_count} standard)")
        return {
            'method': 'Topic-Based Alignment (With Template)',
            'document_type': doc_type,
            'standard_topics': standard_count,
            'alignments_found': len(alignments),
            'alignments': alignments
        }
        
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {
            'method': 'Topic-Based Alignment (With Template)',
            'document_type': doc_type,
            'standard_topics': 0,
            'alignments_found': 0,
            'alignments': [],
            'error': str(e)
        }

def topic_direct_alignment(api_key, doc1_text, doc2_text):
    """Topic-based alignment by identifying which sections belong to each topic."""
    print(f"\n{'='*80}")
    print(f"🎯 TOPIC-DIRECT (TOPIC → SECTIONS MAPPING)")
    print(f"{'='*80}")
    import openai
    import json
    
    # Initialize client with explicit settings to avoid proxy issues
    try:
        client = openai.OpenAI(api_key=api_key)
    except TypeError as e:
        # Fallback for older versions or proxy issues
        print(f"⚠️ Client init warning: {e}, trying alternative...")
        import httpx
        client = openai.OpenAI(
            api_key=api_key,
            http_client=httpx.Client()
        )
    
    # Truncate if needed
    max_len = 12000
    doc1 = doc1_text[:max_len]
    doc2 = doc2_text[:max_len]
    
    print(f"📄 Doc1: {len(doc1_text)} chars (using {len(doc1)})")
    print(f"📄 Doc2: {len(doc2_text)} chars (using {len(doc2)})")
    
    prompt = f"""Analyze these two legal documents and identify 6-10 main topics that appear across both documents.

DOCUMENT 1:
{doc1}

DOCUMENT 2:
{doc2}

For each main topic, identify which sections/clauses from each document relate to that topic.

Return a JSON array where each object represents ONE topic:
{{
  "topic_name": "Name of the topic (e.g., 'Confidentiality Obligations')",
  "topic_description": "Brief description of what this topic covers",
  "doc1_sections": ["Section 1: Title", "Section 2: Title", ...] or [] if not present,
  "doc2_sections": ["Section 1: Title", "Section 2: Title", ...] or [] if not present,
  "doc1_content_summary": "Summary of how doc1 handles this topic" or "",
  "doc2_content_summary": "Summary of how doc2 handles this topic" or "",
  "key_differences": "Main differences in how each document addresses this topic"
}}

IMPORTANT: 
- Identify topics that appear in BOTH documents (high priority)
- Also include topics unique to one document (mark with empty [] for the other)
- Use actual section numbers/identifiers from the documents
- Return ONLY the JSON array, nothing else."""

    try:
        print(f"🤖 Calling GPT-4o to identify topics and map sections...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,
            temperature=0.3
        )
        
        raw = response.choices[0].message.content.strip()
        print(f"✅ Got response: {len(raw)} chars")
        print(f"📝 First 300 chars: {raw[:300]}")
        
        # Clean JSON
        if "```json" in raw:
            start = raw.find("```json") + 7
            end = raw.find("```", start)
            raw = raw[start:end].strip()
        elif raw.startswith("```"):
            raw = raw[3:-3].strip()
        
        # Parse
        topics = json.loads(raw)
        print(f"✅ Parsed {len(topics)} topics")
        
        # Format results with guaranteed fields
        alignments = []
        for i, topic in enumerate(topics):
            # Get all fields with defaults
            topic_name = str(topic.get('topic_name') or f'Topic {i+1}')
            topic_desc = str(topic.get('topic_description') or '')
            doc1_secs = topic.get('doc1_sections') or []
            doc2_secs = topic.get('doc2_sections') or []
            doc1_summary = str(topic.get('doc1_content_summary') or '')
            doc2_summary = str(topic.get('doc2_content_summary') or '')
            differences = str(topic.get('key_differences') or '')
            
            # Ensure sections are lists of strings
            if not isinstance(doc1_secs, list):
                doc1_secs = [str(doc1_secs)]
            doc1_secs = [str(s) for s in doc1_secs]
            
            if not isinstance(doc2_secs, list):
                doc2_secs = [str(doc2_secs)]
            doc2_secs = [str(s) for s in doc2_secs]
            
            # Determine presence
            in_doc1 = len(doc1_secs) > 0
            in_doc2 = len(doc2_secs) > 0
            
            if in_doc1 and in_doc2:
                similarity = 'high'
            elif in_doc1 or in_doc2:
                similarity = 'low'
            else:
                similarity = 'none'
            
            alignment = {
                'topic_name': topic_name,
                'topic_description': topic_desc,
                'doc1_sections': doc1_secs,
                'doc2_sections': doc2_secs,
                'doc1_summary': doc1_summary,
                'doc2_summary': doc2_summary,
                'similarity': similarity,
                'differences': differences,
                'in_doc1': in_doc1,
                'in_doc2': in_doc2
            }
            
            alignments.append(alignment)
            
            print(f"  {i+1}. {topic_name}")
            print(f"      Doc1: {len(doc1_secs)} sections | Doc2: {len(doc2_secs)} sections")
        
        print(f"✅ SUCCESS: {len(alignments)} topics formatted")
        return {
            'method': 'Direct Topic-Based Alignment (Topic → Sections)',
            'alignments_found': len(alignments),
            'alignments': alignments
        }
        
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {
            'method': 'Direct Topic-Based Alignment (Topic → Sections)',
            'alignments_found': 0,
            'alignments': [],
            'error': str(e)
        }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5071))
    # Disable reloader to avoid watchdog compatibility issues
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
