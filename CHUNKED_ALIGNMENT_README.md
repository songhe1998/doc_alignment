# Chunked Document Alignment System

## Overview

This is a new approach to document alignment that handles very long documents by processing them in chunks rather than feeding the entire document to the LLM at once. This approach is designed to work with documents that are too large to process in a single API call while maintaining high-quality alignment results.

## Key Features

### 🔄 **Chunking Strategy**
- **Smart Chunking**: Documents are split into overlapping chunks (default: 1000 words with 200-word overlap)
- **Configurable Parameters**: Adjustable chunk size and overlap based on your needs
- **Context Preservation**: Overlap ensures important context isn't lost at chunk boundaries

### 📝 **Intelligent Summarization**
- **Section Identification**: Each chunk is analyzed to identify section numbers and titles
- **Topic Extraction**: High-level topics and legal concepts are extracted from each chunk
- **Content Summarization**: Brief summaries capture the essence of each chunk's content
- **Metadata Tracking**: Word counts and structural information are preserved

### 🔗 **Chunk-Level Alignment**
- **Semantic Matching**: Chunks are aligned based on content similarity, not just structure
- **Confidence Scoring**: Each alignment gets a confidence rating (high/medium/low)
- **Section Mapping**: Specific sections within aligned chunks are identified
- **Topic Overlap**: Common topics between aligned chunks are highlighted

## How It Works

### 1. Document Chunking
```
Original Document (5000 words) → [Chunk 1, Chunk 2, Chunk 3, Chunk 4, Chunk 5]
Variant Document (5200 words)  → [Chunk 1, Chunk 2, Chunk 3, Chunk 4, Chunk 5, Chunk 6]
```

### 2. Chunk Summarization
Each chunk is analyzed by the LLM to extract:
- **Section Numbers**: `["1", "1.1", "1.2", "2"]`
- **Section Titles**: `["DEFINITIONS", "Grant of License", "Scope", "TERMS"]`
- **Main Topics**: `["licensing terms", "definitions", "user obligations"]`
- **Content Summary**: `"This chunk covers the core definitions and licensing terms..."`

### 3. Chunk Alignment
The system compares chunk summaries to find matches:
```
Original Chunk 1 ↔ Variant Chunk 1 (High Confidence)
- Matching Sections: ["1" ↔ "1", "1.1" ↔ "1.1"]
- Topic Overlap: ["definitions", "licensing terms"]

Original Chunk 2 ↔ Variant Chunk 3 (Medium Confidence)
- Matching Sections: ["2.1" ↔ "2.1"]
- Topic Overlap: ["payment terms"]
```

## Usage

### Basic Usage

```python
from chunked_alignment import ChunkedDocumentAligner

# Initialize aligner
aligner = ChunkedDocumentAligner(api_key="your-api-key")

# Run alignment
result = aligner.run_chunked_alignment(original_doc, variant_doc)

# Access results
print(f"Found {len(result.chunk_alignments)} alignments")
for alignment in result.chunk_alignments:
    print(f"Chunk {alignment.original_chunk_id} ↔ {alignment.variant_chunk_id}")
```

### Configuration Options

```python
# Custom chunk size and overlap
aligner = ChunkedDocumentAligner(
    api_key="your-api-key",
    chunk_size=1500,    # Larger chunks for more context
    overlap_size=300    # More overlap for better continuity
)
```

### Running the Demo

```bash
# Run the demo with sample documents
python chunked_demo.py

# Or use your own documents
python chunked_alignment.py
```

## Data Structures

### ChunkSummary
```python
@dataclass
class ChunkSummary:
    chunk_id: int
    section_numbers: List[str]      # ["1", "1.1", "1.2"]
    section_titles: List[str]       # ["DEFINITIONS", "Grant of License"]
    main_topics: List[str]          # ["licensing terms", "definitions"]
    content_summary: str            # Brief description of chunk content
    word_count: int                 # Number of words in chunk
```

### ChunkAlignment
```python
@dataclass
class ChunkAlignment:
    original_chunk_id: int
    variant_chunk_id: int
    original_summary: ChunkSummary
    variant_summary: ChunkSummary
    alignment_confidence: str       # "high", "medium", "low"
    matching_sections: List[Tuple[str, str]]  # [("1.1", "1.1"), ("2", "2")]
    topic_overlap: List[str]        # ["definitions", "licensing terms"]
```

## Advantages Over Original Approach

### 🚀 **Scalability**
- **Large Documents**: Can handle documents of any size
- **Memory Efficient**: Processes chunks individually
- **API Limits**: Stays within token limits for each API call

### 🎯 **Accuracy**
- **Context Preservation**: Overlap ensures important context isn't lost
- **Semantic Understanding**: Aligns based on content meaning, not just structure
- **Confidence Scoring**: Provides reliability indicators for each alignment

### ⚡ **Performance**
- **Parallel Processing**: Chunks can be processed in parallel (future enhancement)
- **Faster Processing**: Smaller chunks process faster than large documents
- **Better Error Handling**: Issues with one chunk don't affect others

### 🔍 **Insights**
- **Granular Analysis**: Understand document structure at chunk level
- **Topic Tracking**: See how topics are distributed across documents
- **Section Mapping**: Detailed mapping of corresponding sections

## Example Output

```
📊 CHUNK SUMMARIES
==================

📄 ORIGINAL DOCUMENT CHUNKS:
------------------------------

Chunk 0 (487 words):
  Sections: 1 (DEFINITIONS), 1.1 (Software), 1.2 (Licensee)
  Topics: definitions, software licensing, terminology
  Summary: This chunk establishes the foundational definitions and terminology for the software license agreement.

Chunk 1 (523 words):
  Sections: 2 (GRANT OF LICENSE), 2.1 (License Grant), 2.2 (Restrictions)
  Topics: license grant, usage rights, restrictions
  Summary: This chunk outlines the specific terms of the license grant and usage restrictions.

🔗 CHUNK ALIGNMENTS
===================

1. Original Chunk 0 ↔ Variant Chunk 0
   Confidence: high
   Topic Overlap: definitions, terminology, software licensing
   Matching Sections:
      1 ↔ 1
      1.1 ↔ 1.1
      1.2 ↔ 1.2

2. Original Chunk 1 ↔ Variant Chunk 1
   Confidence: high
   Topic Overlap: license grant, usage rights, authorization
   Matching Sections:
      2.1 ↔ 2.1
      2.2 ↔ 3.1
```

## Configuration Recommendations

### For Legal Documents
- **Chunk Size**: 1000-1500 words
- **Overlap**: 200-300 words
- **Rationale**: Legal documents have clear section boundaries

### For Technical Documents
- **Chunk Size**: 800-1200 words
- **Overlap**: 150-250 words
- **Rationale**: Technical content may have more complex cross-references

### For Large Documents (>10,000 words)
- **Chunk Size**: 1500-2000 words
- **Overlap**: 300-400 words
- **Rationale**: Larger chunks preserve more context for complex alignments

## Future Enhancements

1. **Parallel Processing**: Process multiple chunks simultaneously
2. **Smart Chunking**: Use document structure to guide chunk boundaries
3. **Hierarchical Alignment**: Align at both chunk and section levels
4. **Interactive Visualization**: Web interface for exploring alignments
5. **Batch Processing**: Handle multiple document pairs efficiently

## Comparison with Original System

| Aspect | Original System | Chunked System |
|--------|----------------|----------------|
| Document Size | Limited by API tokens | Unlimited |
| Processing | Single API call | Multiple API calls |
| Memory Usage | High (full document) | Low (chunk by chunk) |
| Error Handling | All-or-nothing | Granular |
| Scalability | Limited | High |
| Context Preservation | Full document | Chunk + overlap |
| Alignment Granularity | Section level | Chunk + section level |

## Requirements

- Python 3.7+
- OpenAI API key
- Required packages: `openai`, `python-dotenv`

## Installation

```bash
pip install openai python-dotenv
```

## Environment Setup

Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your-api-key-here
```

## License

This project follows the same license as the original alignment system.
