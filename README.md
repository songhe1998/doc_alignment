# Legal Document Alignment System 📄⚖️

An AI-powered system that automatically aligns and compares legal documents, identifying section mappings and content differences using OpenAI's GPT-4o.

## 🚀 Features

### Core Capabilities
- **🔄 Automated Document Generation**: Creates synthetic legal document pairs for testing
- **🔍 Section Extraction**: Automatically identifies and extracts document sections (e.g., "1.1", "2.3", etc.)  
- **🔗 Intelligent Section Alignment**: Uses LLM to map corresponding sections between documents
- **📊 Content Comparison**: Detailed analysis of differences between aligned sections
- **📈 Automated Evaluation**: LLM-powered assessment of alignment quality with scoring

### Evaluation Metrics
- **Section Alignment Accuracy** (0-10): How well sections are matched
- **Content Comparison Quality** (0-10): Quality of difference detection
- **Overall Completeness** (0-10): Coverage of document alignment
- **Processing Time**: Performance tracking
- **Coverage Ratio**: Percentage of sections successfully aligned

## 📋 System Performance

Based on automated evaluation results:

| Metric | Average Score | Performance |
|--------|--------------|-------------|
| Overall Score | **7.50/10** | Good |  
| Section Alignment | **8.50/10** | Excellent |
| Content Quality | **6.75/10** | Good |
| Coverage Ratio | **65.49%** | Good |
| Processing Time | **~2.3 min/pair** | Reasonable |

## 🛠️ Usage

### Prerequisites
```bash
pip install openai
```

### Single Document Alignment
```bash
python alignment.py
```
Runs detailed alignment on one document pair with full output.

### Batch Evaluation
```bash
# Small batch (3 pairs)
python alignment.py evaluate 3

# Medium batch (8 pairs)  
python alignment.py evaluate 8

# Large batch (15 pairs)
python alignment.py evaluate 15
```

### Interactive Demo
```bash
python demo.py
```
Provides an interactive menu for different evaluation modes.

## 📊 Sample Output

### Alignment Results
```
📊 SECTION ALIGNMENT TABLE
================================================================================
Doc Section  Template Section Doc Title                 Template Title           
--------------------------------------------------------------------------------
1.1          1.1              Software                  Software                 
2.1          2.1              Grant of License          Grant of License         
3.1          2.3              License Fee               License Fee
```

### Content Differences
```
📝 In Document but NOT in Template:
   • The document section uses 'refers to' instead of 'means'
   • The phrase 'commits to paying' instead of 'agrees to pay'

📝 In Template but NOT in Document:  
   • The template section uses 'means' instead of 'refers to'
   • The phrase 'as set forth in Exhibit B' is used
```

### Evaluation Report
```
📈 PERFORMANCE STATISTICS
------------------------------------------------------------
Average Section Alignment Accuracy: 8.50/10 (σ=0.71)
Average Content Comparison Quality: 6.75/10 (σ=0.35) 
Average Overall Completeness:      7.25/10 (σ=0.35)
Average Overall Score:             7.50/10 (σ=0.47)

⭐ SCORE DISTRIBUTION
------------------------------------------------------------
Good              (7.0-7.9):  2 pairs (100.0%)

🎯 RECOMMENDATIONS
------------------------------------------------------------
• System shows good potential. Focus on top improvement areas above.
```

## 🏗️ Architecture

### Core Components
1. **LegalDocumentAligner**: Main class handling document processing
2. **Section Extraction**: Regex-based parsing of document structure  
3. **LLM Alignment**: GPT-4o powered section mapping
4. **Content Comparison**: Detailed difference analysis
5. **Evaluation Pipeline**: Automated quality assessment
6. **Reporting System**: Comprehensive statistics and visualizations

### Data Classes
- `SectionMapping`: Represents section alignments with confidence scores
- `ContentDifference`: Stores identified content differences
- `AlignmentResult`: Complete alignment results for a document pair
- `EvaluationScore`: Quality assessment scores and comments

## 🔧 Configuration

### API Key
The system uses the provided OpenAI API key. Modify the key in `main()` function if needed.

### Model Settings
- **Model**: GPT-4o
- **Temperature**: 0.3 (focused responses)
- **Max Tokens**: 3000 (for large section lists)

## 🎯 Use Cases

### Legal Document Analysis
- **Contract Comparison**: Compare different versions of legal contracts
- **Template Alignment**: Align documents against standard templates
- **Change Detection**: Identify modifications between document versions
- **Compliance Checking**: Ensure documents match required templates

### System Evaluation
- **Performance Testing**: Batch evaluation with statistical analysis
- **Quality Assessment**: LLM-powered evaluation of alignment accuracy
- **Benchmarking**: Compare different alignment approaches
- **Error Analysis**: Identify areas for improvement

## 🎯 Topic-Based Alignment (NEW!)

A new intelligent alignment approach that uses semantic understanding:

### How It Works
1. **Identifies document type** (NDA, License Agreement, etc.) using LLM
2. **Researches standard topics** for that document type
3. **Extracts topics** from both documents
4. **Aligns by topics** rather than section numbers
5. **Compares content** for each topic

### Usage
```bash
# Run topic-based alignment
python topic_alignment.py

# Run interactive demo
python topic_demo.py
```

### Advantages
- ✅ Works with different document structures
- ✅ Semantic understanding of legal concepts
- ✅ Adapts to document type
- ✅ Identifies missing essential topics
- ✅ Higher-level insights

See [TOPIC_ALIGNMENT_README.md](TOPIC_ALIGNMENT_README.md) for detailed documentation.

## 📈 Future Enhancements

- Support for custom document formats (PDF, DOCX)
- Real-time alignment API
- Web-based interface
- Advanced similarity metrics
- Multi-language support
- Custom evaluation criteria

## 🤝 Contributing

The system is designed for extensibility:
1. Add new document types in `generate_legal_document()`
2. Enhance section parsing in `extract_sections()`
3. Improve alignment logic in `align_sections()`
4. Extend evaluation metrics in `evaluate_alignment_quality()`

---

**Built with ❤️ using OpenAI GPT-4o**




# doc_alignment
