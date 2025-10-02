# Topic-Based Document Alignment System

## Overview

A sophisticated document alignment approach that uses **semantic topic understanding** rather than structural section matching. This system identifies the document type, researches standard topics for that type, and aligns documents based on conceptual topics rather than section numbers.

## Key Innovation

Unlike traditional section-by-section alignment, topic-based alignment:
- **Understands document semantics**: Identifies what the document is about, not just its structure
- **Adapts to document types**: Different alignment strategies for NDAs vs. License Agreements vs. Employment Contracts
- **Handles structural differences**: Aligns by meaning even when section numbering differs completely
- **Leverages legal knowledge**: Uses AI understanding of legal concepts and standard practices

## How It Works

### 1. **Document Type Identification** 🔍
```
Input: Legal document text
↓
LLM Analysis: Examines language, structure, and content
↓
Output: Document type (e.g., "Software License Agreement")
        Confidence level (high/medium/low)
        Key identifying characteristics
```

**Example:**
```json
{
  "document_type": "Software License Agreement",
  "confidence": "high",
  "key_characteristics": [
    "Contains grant of license provisions",
    "Defines software and licensee terms",
    "Includes payment and termination clauses"
  ]
}
```

### 2. **Standard Topics Research** 📚
```
Input: Document type
↓
LLM Knowledge Base: Retrieves standard legal topics for this document type
↓
Output: List of typical topics with:
        - Topic name
        - Description
        - Typical section titles
        - Importance level (essential/common/optional)
```

**Example for Software License Agreement:**
```json
[
  {
    "topic_name": "Definitions",
    "description": "Terms and definitions used throughout the agreement",
    "typical_sections": ["Definitions", "Terms", "Interpretation"],
    "importance": "essential"
  },
  {
    "topic_name": "Grant of Rights",
    "description": "License grant and scope of permitted use",
    "typical_sections": ["Grant of License", "License Grant", "Permitted Use"],
    "importance": "essential"
  },
  {
    "topic_name": "Payment Terms",
    "description": "Fees, payment schedule, and related obligations",
    "typical_sections": ["Payment", "License Fee", "Compensation"],
    "importance": "essential"
  }
]
```

### 3. **Topic Extraction** 🏷️
```
For each document:
  Input: Document sections + Standard topics
  ↓
  LLM Analysis: Maps sections to topics
  ↓
  Output: Which topics appear in this document
          Which sections cover each topic
```

**Example:**
```
Original Document Topics:
  • Definitions → sections 1, 1.1, 1.2, 1.3, 1.4, 1.5
  • Grant of Rights → sections 2.1, 2.2
  • Restrictions → sections 3.1, 3.2, 3.3
  • Payment Terms → sections 4.1, 4.2, 4.3

Variant Document Topics:
  • Definitions → sections 1.1, 1.2, 1.3, 1.4, 1.5
  • Grant of Rights → sections 2.1, 2.2, 2.3
  • Usage Limitations → sections 3.1, 3.2
  • Compensation → sections 4.1, 4.2, 4.3, 4.4
```

### 4. **Topic-Based Alignment** 🔗
```
Input: Topics from both documents
↓
Matching: Find topics that appear in both
↓
Content Comparison: LLM compares how each topic is handled
↓
Output: Topic alignments with:
        - Matched sections
        - Confidence level
        - Content differences
```

**Example:**
```
Topic: Payment Terms
  Original sections: 4.1, 4.2, 4.3
  Variant sections: 4.1, 4.2, 4.3, 4.4
  Confidence: high
  Differences: "Variant adds late payment penalties (section 4.4) 
               and extends payment period from 30 to 45 days"
```

## Architecture

### Core Components

```
TopicBasedAligner
├── identify_document_type()       # Step 1: What type of document?
├── research_standard_topics()     # Step 2: What topics are typical?
├── extract_sections()             # Parse document structure
├── identify_topics_in_document()  # Step 3: What topics are present?
├── align_topics()                 # Step 4: Match topics between docs
└── _compare_topic_content()       # Compare content for each topic
```

### Data Structures

```python
@dataclass
class DocumentTypeInfo:
    document_type: str              # "Software License Agreement"
    confidence: str                 # "high", "medium", "low"
    key_characteristics: List[str]  # Identifying features

@dataclass
class TopicInfo:
    topic_name: str                 # "Payment Terms"
    description: str                # What this topic covers
    typical_sections: List[str]     # Common section titles
    importance: str                 # "essential", "common", "optional"

@dataclass
class DocumentTopics:
    document_id: str                # "original" or "variant"
    topics: List[Tuple[str, List[str]]]  # (topic_name, [section_numbers])

@dataclass
class TopicAlignment:
    topic_name: str                 # The aligned topic
    original_sections: List[str]    # Sections in original
    variant_sections: List[str]     # Sections in variant
    alignment_confidence: str       # "high", "medium", "low"
    content_differences: str        # Summary of differences
```

## Usage

### Basic Usage

```python
from topic_alignment import TopicBasedAligner

# Initialize aligner
aligner = TopicBasedAligner(api_key="your-openai-api-key")

# Run topic-based alignment
result = aligner.run_topic_alignment(original_doc, variant_doc)

# Access results
print(f"Document Type: {result.document_type.document_type}")
print(f"Standard Topics: {len(result.standard_topics)}")
print(f"Topic Alignments: {len(result.topic_alignments)}")
```

### Running the Demo

```bash
# Make sure you have test documents
python topic_demo.py
```

### Command Line

```bash
# Run with default test documents
python topic_alignment.py
```

## Example Output

```
🚀 Starting Topic-Based Document Alignment Pipeline

📋 Step 1: Identifying document type...
   ✅ Document Type: Software License Agreement (confidence: high)
   Key characteristics: Contains grant of license provisions, Defines software terms, Includes termination clauses

🔍 Step 2: Researching standard topics for Software License Agreement...
   ✅ Found 12 standard topics
      • Definitions (essential)
      • Grant of Rights (essential)
      • Restrictions (essential)
      • Payment Terms (essential)
      • Support and Maintenance (common)
      ... and 7 more

📄 Step 3: Extracting sections from documents...
   Original document: 35 sections
   Variant document: 42 sections

🏷️  Step 4: Identifying topics in original document...
   ✅ Found 10 topics in original

🏷️  Step 5: Identifying topics in variant document...
   ✅ Found 11 topics in variant

🔗 Step 6: Aligning topics between documents...
   ✅ Created 13 topic alignments

================================================================================
📊 TOPIC-BASED ALIGNMENT RESULTS
================================================================================

📋 DOCUMENT TYPE: Software License Agreement
   Confidence: high
   Characteristics: Grant of license provisions, Software definitions, Termination clauses

🗺️  TOPIC MAPPINGS:

Original Document Topics (10):
   • Definitions: sections 1, 1.1, 1.2, 1.3, 1.4, 1.5
   • Grant of Rights: sections 2.1, 2.2, 2.3
   • Restrictions: sections 3.1, 3.2, 3.3
   • Payment Terms: sections 4.1, 4.2, 4.3, 4.4
   ...

Variant Document Topics (11):
   • Definitions: sections 1.1, 1.2, 1.3, 1.4, 1.5
   • Grant of Rights: sections 2.1, 2.2
   • Usage Limitations: sections 3.1, 3.2, 3.3
   • Compensation: sections 4.1, 4.2, 4.3, 4.4
   ...

🔗 TOPIC ALIGNMENTS:

1. Topic: Definitions
   Confidence: high
   Original sections: 1, 1.1, 1.2, 1.3, 1.4, 1.5
   Variant sections: 1.1, 1.2, 1.3, 1.4, 1.5
   Differences: Both documents contain comprehensive definitions sections with 
                similar core terms. Variant uses slightly different wording 
                for some definitions but maintains the same concepts.

2. Topic: Grant of Rights
   Confidence: high
   Original sections: 2.1, 2.2, 2.3
   Variant sections: 2.1, 2.2
   Differences: Original includes additional subsection 2.3 regarding installation 
                limits. Variant combines this into section 2.2 with different 
                installation limits (10 vs 5 workstations).

📈 SUMMARY STATISTICS:
Total standard topics: 12
Topics in both documents: 9
Topics only in original: 1
Topics only in variant: 2
Topic coverage: 75.0%

✅ Topic-based alignment complete!
```

## Advantages Over Section-Based Alignment

### 1. **Semantic Understanding**
| Section-Based | Topic-Based |
|--------------|-------------|
| "Section 2.1 aligns with section 3.4" | "Grant of Rights topic appears in sections 2.1-2.3 of original and 3.4-3.6 of variant" |
| Structural matching | Conceptual matching |
| Breaks when numbering changes | Works despite structural differences |

### 2. **Adaptability**
```
Section-Based: Same algorithm for all documents
Topic-Based: Adapts to document type
  - NDA → Focus on confidentiality, disclosure, term
  - Employment → Focus on duties, compensation, termination
  - License → Focus on grant, restrictions, payment
```

### 3. **Higher-Level Insights**
```
Section-Based Output:
  "Section 3.1 differs in 5 clauses from section 4.2"

Topic-Based Output:
  "Payment Terms: Variant extends payment period from 30 to 45 days,
   adds 2% late fee (vs 1.5% in original), and introduces new 
   indemnification clause for tax obligations"
```

### 4. **Completeness Analysis**
```
Topic-Based can identify:
  ✓ Missing essential topics
  ✓ Extra optional topics
  ✓ Standard vs. non-standard organization
  ✗ Section-based can only count sections
```

## Comparison: All Three Approaches

| Feature | Section-Based | Chunked | Topic-Based |
|---------|--------------|---------|-------------|
| **Best For** | Similar structures | Very long docs | Different structures |
| **Scalability** | Limited by tokens | Unlimited | Limited by tokens |
| **Semantic Understanding** | Low | Medium | High |
| **Structural Flexibility** | Low | Medium | High |
| **Processing Speed** | Fast | Slow (multiple chunks) | Medium |
| **Legal Domain Knowledge** | None | None | Built-in |
| **Coverage Analysis** | Section count | Chunk overlap | Topic completeness |

## Use Cases

### ✅ When to Use Topic-Based Alignment

1. **Different document versions** with restructured sections
   - Original has 50 sections, variant has 80
   - Section numbering completely different

2. **Template compliance checking**
   - Does the document cover all required topics?
   - Are essential topics missing?

3. **Contract type identification**
   - What kind of document is this?
   - What should we expect to find?

4. **Cross-organization comparisons**
   - Company A's license agreement vs. Company B's
   - Different formats, same conceptual content

5. **Document quality assessment**
   - Are all essential topics covered?
   - Are topics organized in a standard way?

### ⚠️ When to Use Other Approaches

**Section-Based**: Documents with identical structure, quick comparison needed

**Chunked**: Very long documents (10,000+ words), memory constraints

**Hybrid**: Use topic-based for overview, section-based for details

## Configuration

### Environment Setup

```bash
# Create .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env

# Install dependencies
pip install openai python-dotenv
```

### Customization

```python
# Modify standard topics research
aligner = TopicBasedAligner(api_key)

# For specialized document types, you can override:
custom_topics = [
    TopicInfo(
        topic_name="Custom Topic",
        description="Your custom topic",
        typical_sections=["Section A", "Section B"],
        importance="essential"
    )
]
```

## Performance

### Processing Time
- **Document Type ID**: ~2-3 seconds
- **Standard Topics Research**: ~3-5 seconds
- **Topic Extraction**: ~5-7 seconds per document
- **Topic Alignment**: ~10-15 seconds
- **Total**: ~30-40 seconds for a typical document pair

### API Costs
- **Tokens per alignment**: ~8,000-12,000 tokens
- **Cost**: ~$0.10-0.15 per document pair (GPT-4o pricing)
- More expensive than section-based but provides deeper insights

## Future Enhancements

1. **Real Web Search Integration**: Use actual web search APIs for current legal standards
2. **Document Type Library**: Pre-computed standard topics for common document types
3. **Confidence Scoring**: ML-based confidence scoring for alignments
4. **Interactive Visualization**: Web UI to explore topic relationships
5. **Multi-Document Comparison**: Compare 3+ documents simultaneously
6. **Industry-Specific Topics**: Specialized topic libraries for different industries
7. **Regulatory Compliance**: Check topics against regulatory requirements

## Requirements

- Python 3.7+
- OpenAI API key (GPT-4o recommended)
- Dependencies: `openai`, `python-dotenv`

## Files

```
topic_alignment.py      # Main implementation
topic_demo.py          # Interactive demo
TOPIC_ALIGNMENT_README.md  # This file
```

## Integration with Existing System

```python
# Can be used alongside existing aligners
from alignment import LegalDocumentAligner
from topic_alignment import TopicBasedAligner

# Section-based for detailed comparison
section_aligner = LegalDocumentAligner(api_key)
section_result = section_aligner.run_full_alignment()

# Topic-based for overview
topic_aligner = TopicBasedAligner(api_key)
topic_result = topic_aligner.run_topic_alignment(original, variant)

# Best of both worlds!
```

---

**Built with ❤️ using OpenAI GPT-4o and legal domain knowledge**

