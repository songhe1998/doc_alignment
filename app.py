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
from topic_services import (
    run_topic_template_alignment,
    run_topic_direct_alignment,
)
from openai_helper import create_openai_client

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
    """Split document into sections and track offsets for highlighting."""
    patterns = [
        (r'^(\d+\.[\d\.]*)\s+([^\n]+)', 'numbered'),
        (r'^([A-Z][^\n]{0,100}):', 'title'),
        (r'^(Article\s+\d+)', 'article'),
        (r'^(Section\s+\d+)', 'section_word'),
    ]
    
    sections = []
    lines = text.split('\n')
    # Track character offsets for each line
    line_offsets = []
    pos = 0
    for line in lines:
        line_offsets.append(pos)
        pos += len(line) + 1  # +1 accounts for stripped newline
    
    def make_section(title, start_line, start_char, section_id):
        return {
            'title': title[:100],
            'content': '',
            'start_line': start_line,
            'start_char': start_char,
            'section_id': section_id,
        }
    
    def normalize_section_id(text_value):
        text_value = (text_value or '').strip()
        if not text_value:
            return ''
        return re.sub(r'\s+', ' ', text_value).strip()
    
    current_section = make_section('Introduction', 0, 0, 'introduction')
    
    for i, raw_line in enumerate(lines):
        line = raw_line.strip()
        if not line:
            current_section['content'] += '\n'
            continue
        
        matched = False
        for pattern, pattern_type in patterns:
            match = re.match(pattern, line, re.MULTILINE)
            if match:
                if current_section['content'].strip():
                    current_section['end_line'] = i
                    current_section['end_char'] = line_offsets[i]
                    sections.append(current_section)
                
                section_id = ''
                title_text = line
                if pattern_type == 'numbered':
                    section_id = match.group(1)
                elif pattern_type == 'article':
                    section_id = match.group(1)
                elif pattern_type == 'section_word':
                    section_id = match.group(1)
                elif pattern_type == 'title':
                    section_id = match.group(1)
                
                section_id = normalize_section_id(section_id or title_text)
                current_section = make_section(title_text, i, line_offsets[i], section_id)
                current_section['content'] = line + '\n'
                matched = True
                break
        
        if not matched:
            current_section['content'] += line + '\n'
    
    if current_section['content'].strip():
        current_section['end_line'] = len(lines)
        current_section['end_char'] = len(text)
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
    
    # Initialize client with proper configuration
    client = create_openai_client(api_key)
    
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
            model="gpt-4o",  # GPT-4 Omni - most capable model
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
            temperature=0  # More deterministic for consistent section identification
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

def _assign_alignment_colors(alignments):
    """Add color/id metadata for UI visualization."""
    for i, alignment in enumerate(alignments):
        alignment.setdefault('id', i)
        alignment['color'] = COLORS[i % len(COLORS)]
    return alignments


def topic_template_alignment(api_key, doc1_text, doc2_text, doc1_sections, doc2_sections):
    """Topic-based alignment using standard legal topics."""
    print(f"\n{'='*80}")
    print(f"🏷️  TOPIC-TEMPLATE ALIGNMENT")
    print(f"{'='*80}")

    result = run_topic_template_alignment(api_key, doc1_text, doc2_text)
    result['alignments'] = _assign_alignment_colors(result.get('alignments', []))
    print(f"✅ Found {result.get('alignments_found', 0)} topics")
    return result


def topic_direct_alignment(api_key, doc1_text, doc2_text, doc1_sections, doc2_sections):
    """Topic-based alignment by identifying topics and mapping sections."""
    print(f"\n{'='*80}")
    print(f"🎯 TOPIC-DIRECT ALIGNMENT")
    print(f"{'='*80}")

    result = run_topic_direct_alignment(api_key, doc1_text, doc2_text)
    result['alignments'] = _assign_alignment_colors(result.get('alignments', []))
    print(f"✅ Found {result.get('alignments_found', 0)} topics")
    return result


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
