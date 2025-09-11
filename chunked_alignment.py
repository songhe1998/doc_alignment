import openai
import json
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import time
import statistics
import os
from dotenv import load_dotenv

@dataclass
class ChunkSummary:
    chunk_id: int
    section_numbers: List[str]  # e.g., ["1", "1.1", "1.2"]
    section_titles: List[str]  # e.g., ["DEFINITIONS", "Grant of License", "Scope"]
    main_topics: List[str]  # High-level topics covered
    content_summary: str  # Brief summary of what this chunk contains
    word_count: int

@dataclass
class ChunkAlignment:
    original_chunk_id: int
    variant_chunk_id: int
    original_summary: ChunkSummary
    variant_summary: ChunkSummary
    alignment_confidence: str  # "high", "medium", "low"
    matching_sections: List[Tuple[str, str]]  # (original_section, variant_section)
    topic_overlap: List[str]  # Topics that appear in both chunks

@dataclass
class ChunkedAlignmentResult:
    original_chunks: List[ChunkSummary]
    variant_chunks: List[ChunkSummary]
    chunk_alignments: List[ChunkAlignment]
    processing_time: float
    total_words_processed: int

class ChunkedDocumentAligner:
    def __init__(self, api_key: str, chunk_size: int = 1000, overlap_size: int = 200):
        """
        Initialize the chunked document aligner.
        
        Args:
            api_key: OpenAI API key
            chunk_size: Target size for each chunk in words (default: 1000)
            overlap_size: Overlap between chunks in words (default: 200)
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
    
    def chunk_document(self, document: str) -> List[Tuple[int, str]]:
        """
        Split document into overlapping chunks.
        
        Returns:
            List of (chunk_id, chunk_content) tuples
        """
        # Split into words
        words = document.split()
        chunks = []
        chunk_id = 0
        
        start_idx = 0
        while start_idx < len(words):
            # Calculate end index for this chunk
            end_idx = min(start_idx + self.chunk_size, len(words))
            
            # Extract chunk content
            chunk_words = words[start_idx:end_idx]
            chunk_content = ' '.join(chunk_words)
            
            chunks.append((chunk_id, chunk_content))
            
            # Move start index with overlap
            start_idx = end_idx - self.overlap_size
            chunk_id += 1
            
            # Prevent infinite loop if overlap is too large
            if start_idx >= end_idx:
                start_idx = end_idx
        
        return chunks
    
    def summarize_chunk(self, chunk_id: int, chunk_content: str, document_type: str = "original") -> ChunkSummary:
        """
        Use LLM to summarize a chunk and identify its sections and topics.
        """
        prompt = f"""Analyze this chunk from a {document_type} legal document and provide a structured summary.

Document chunk:
{chunk_content}

Please provide a JSON object with:
- "section_numbers": array of section numbers found (e.g., ["1", "1.1", "1.2", "2"])
- "section_titles": array of corresponding section titles (e.g., ["DEFINITIONS", "Grant of License", "Scope", "TERMS"])
- "main_topics": array of 3-5 high-level topics this chunk covers (e.g., ["licensing terms", "definitions", "user obligations"])
- "content_summary": a 2-3 sentence summary of what this chunk contains
- "word_count": approximate word count of this chunk

Focus on identifying:
1. All section headers and their numbers
2. Main legal topics and concepts
3. Key provisions or clauses mentioned
4. Overall purpose of this chunk within the document

Return only the JSON object, no other text."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.3
            )
            
            json_str = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if "```json" in json_str:
                json_start = json_str.find("```json") + 7
                json_end = json_str.find("```", json_start)
                json_str = json_str[json_start:json_end].strip()
            elif json_str.startswith("```") and json_str.endswith("```"):
                json_str = json_str[3:-3].strip()
            elif not json_str.startswith('{'):
                start_idx = json_str.find('{')
                end_idx = json_str.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    json_str = json_str[start_idx:end_idx+1]
            
            data = json.loads(json_str)
            
            return ChunkSummary(
                chunk_id=chunk_id,
                section_numbers=data.get("section_numbers", []),
                section_titles=data.get("section_titles", []),
                main_topics=data.get("main_topics", []),
                content_summary=data.get("content_summary", ""),
                word_count=data.get("word_count", len(chunk_content.split()))
            )
            
        except Exception as e:
            print(f"Error summarizing chunk {chunk_id}: {e}")
            return ChunkSummary(
                chunk_id=chunk_id,
                section_numbers=[],
                section_titles=[],
                main_topics=[],
                content_summary=f"Error processing chunk: {str(e)}",
                word_count=len(chunk_content.split())
            )
    
    def align_chunks(self, original_chunks: List[ChunkSummary], variant_chunks: List[ChunkSummary]) -> List[ChunkAlignment]:
        """
        Use LLM to align chunks between original and variant documents based on their summaries.
        """
        # Prepare chunk summaries for alignment
        original_summaries = []
        for chunk in original_chunks:
            summary_text = f"""Chunk {chunk.chunk_id}:
Sections: {', '.join([f"{num} ({title})" for num, title in zip(chunk.section_numbers, chunk.section_titles)])}
Topics: {', '.join(chunk.main_topics)}
Summary: {chunk.content_summary}"""
            original_summaries.append(summary_text)
        
        variant_summaries = []
        for chunk in variant_chunks:
            summary_text = f"""Chunk {chunk.chunk_id}:
Sections: {', '.join([f"{num} ({title})" for num, title in zip(chunk.section_numbers, chunk.section_titles)])}
Topics: {', '.join(chunk.main_topics)}
Summary: {chunk.content_summary}"""
            variant_summaries.append(summary_text)
        
        prompt = f"""You are aligning chunks from two versions of a legal document based on their content summaries.

ORIGINAL DOCUMENT CHUNKS:
{chr(10).join(original_summaries)}

VARIANT DOCUMENT CHUNKS:
{chr(10).join(variant_summaries)}

Create alignments between chunks that cover similar content. For each alignment, provide a JSON array where each object has:
- "original_chunk_id": chunk ID from original document
- "variant_chunk_id": chunk ID from variant document  
- "alignment_confidence": "high", "medium", or "low" based on content similarity
- "matching_sections": array of [original_section, variant_section] pairs that correspond
- "topic_overlap": array of topics that appear in both chunks

Consider:
1. Section number/name similarities
2. Topic overlaps
3. Content summary similarities
4. Legal concept alignment

Only create alignments where there's reasonable content similarity. Some chunks may not have matches.
Return only the JSON array, no other text."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.3
            )
            
            json_str = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if "```json" in json_str:
                json_start = json_str.find("```json") + 7
                json_end = json_str.find("```", json_start)
                json_str = json_str[json_start:json_end].strip()
            elif json_str.startswith("```") and json_str.endswith("```"):
                json_str = json_str[3:-3].strip()
            elif not json_str.startswith('['):
                start_idx = json_str.find('[')
                end_idx = json_str.rfind(']')
                if start_idx != -1 and end_idx != -1:
                    json_str = json_str[start_idx:end_idx+1]
            
            alignments_data = json.loads(json_str)
            
            # Convert to ChunkAlignment objects
            alignments = []
            for alignment_data in alignments_data:
                original_chunk = next((c for c in original_chunks if c.chunk_id == alignment_data["original_chunk_id"]), None)
                variant_chunk = next((c for c in variant_chunks if c.chunk_id == alignment_data["variant_chunk_id"]), None)
                
                if original_chunk and variant_chunk:
                    alignments.append(ChunkAlignment(
                        original_chunk_id=alignment_data["original_chunk_id"],
                        variant_chunk_id=alignment_data["variant_chunk_id"],
                        original_summary=original_chunk,
                        variant_summary=variant_chunk,
                        alignment_confidence=alignment_data["alignment_confidence"],
                        matching_sections=alignment_data.get("matching_sections", []),
                        topic_overlap=alignment_data.get("topic_overlap", [])
                    ))
            
            return alignments
            
        except Exception as e:
            print(f"Error aligning chunks: {e}")
            return []
    
    def run_chunked_alignment(self, original_doc: str, variant_doc: str, verbose: bool = True) -> ChunkedAlignmentResult:
        """
        Run the complete chunked alignment pipeline.
        """
        start_time = time.time()
        
        if verbose:
            print("🚀 Starting Chunked Document Alignment Pipeline\n")
        
        # Step 1: Chunk both documents
        if verbose:
            print("📄 Chunking documents...")
        original_chunks_data = self.chunk_document(original_doc)
        variant_chunks_data = self.chunk_document(variant_doc)
        
        if verbose:
            print(f"   Original document: {len(original_chunks_data)} chunks")
            print(f"   Variant document: {len(variant_chunks_data)} chunks\n")
        
        # Step 2: Summarize each chunk
        if verbose:
            print("📝 Summarizing chunks...")
        original_chunks = []
        variant_chunks = []
        
        for chunk_id, chunk_content in original_chunks_data:
            if verbose:
                print(f"   Summarizing original chunk {chunk_id}...")
            summary = self.summarize_chunk(chunk_id, chunk_content, "original")
            original_chunks.append(summary)
        
        for chunk_id, chunk_content in variant_chunks_data:
            if verbose:
                print(f"   Summarizing variant chunk {chunk_id}...")
            summary = self.summarize_chunk(chunk_id, chunk_content, "variant")
            variant_chunks.append(summary)
        
        if verbose:
            print(f"✅ Completed chunk summarization\n")
        
        # Step 3: Align chunks
        if verbose:
            print("🔗 Aligning chunks using AI...")
        chunk_alignments = self.align_chunks(original_chunks, variant_chunks)
        
        if verbose:
            print(f"✅ Found {len(chunk_alignments)} chunk alignments\n")
        
        # Step 4: Display results
        if verbose:
            self._display_chunked_results(original_chunks, variant_chunks, chunk_alignments)
        
        processing_time = time.time() - start_time
        total_words = sum(c.word_count for c in original_chunks) + sum(c.word_count for c in variant_chunks)
        
        return ChunkedAlignmentResult(
            original_chunks=original_chunks,
            variant_chunks=variant_chunks,
            chunk_alignments=chunk_alignments,
            processing_time=processing_time,
            total_words_processed=total_words
        )
    
    def _display_chunked_results(self, original_chunks: List[ChunkSummary], 
                                variant_chunks: List[ChunkSummary], 
                                chunk_alignments: List[ChunkAlignment]):
        """Display chunked alignment results in a formatted way"""
        
        # Display chunk summaries
        print("📊 CHUNK SUMMARIES")
        print("=" * 100)
        
        print("\n📄 ORIGINAL DOCUMENT CHUNKS:")
        print("-" * 50)
        for chunk in original_chunks:
            print(f"\nChunk {chunk.chunk_id} ({chunk.word_count} words):")
            print(f"  Sections: {', '.join([f'{num} ({title})' for num, title in zip(chunk.section_numbers, chunk.section_titles)])}")
            print(f"  Topics: {', '.join(chunk.main_topics)}")
            print(f"  Summary: {chunk.content_summary}")
        
        print("\n📄 VARIANT DOCUMENT CHUNKS:")
        print("-" * 50)
        for chunk in variant_chunks:
            print(f"\nChunk {chunk.chunk_id} ({chunk.word_count} words):")
            print(f"  Sections: {', '.join([f'{num} ({title})' for num, title in zip(chunk.section_numbers, chunk.section_titles)])}")
            print(f"  Topics: {', '.join(chunk.main_topics)}")
            print(f"  Summary: {chunk.content_summary}")
        
        # Display alignments
        print("\n🔗 CHUNK ALIGNMENTS")
        print("=" * 100)
        
        if not chunk_alignments:
            print("No chunk alignments found.")
            return
        
        for i, alignment in enumerate(chunk_alignments, 1):
            print(f"\n{i}. Original Chunk {alignment.original_chunk_id} ↔ Variant Chunk {alignment.variant_chunk_id}")
            print(f"   Confidence: {alignment.alignment_confidence}")
            print(f"   Topic Overlap: {', '.join(alignment.topic_overlap)}")
            
            if alignment.matching_sections:
                print(f"   Matching Sections:")
                for orig_sec, var_sec in alignment.matching_sections:
                    print(f"      {orig_sec} ↔ {var_sec}")
            else:
                print(f"   No specific section matches identified")
        
        # Summary statistics
        print(f"\n📈 ALIGNMENT SUMMARY")
        print("-" * 50)
        print(f"Original chunks: {len(original_chunks)}")
        print(f"Variant chunks: {len(variant_chunks)}")
        print(f"Alignments found: {len(chunk_alignments)}")
        print(f"Coverage: {len(chunk_alignments)/max(len(original_chunks), len(variant_chunks), 1):.1%}")
        
        confidence_counts = {}
        for alignment in chunk_alignments:
            conf = alignment.alignment_confidence
            confidence_counts[conf] = confidence_counts.get(conf, 0) + 1
        
        print(f"Confidence distribution: {confidence_counts}")
        
        print("\n✅ Chunked document alignment complete!")

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")
    
    # Initialize chunked aligner
    aligner = ChunkedDocumentAligner(api_key, chunk_size=1000, overlap_size=200)
    
    # Load test documents (you can replace these with your own documents)
    try:
        with open('/Users/songhewang/Desktop/doc_alignment/original_doc.txt', 'r') as f:
            original_doc = f.read()
        with open('/Users/songhewang/Desktop/doc_alignment/variant_doc.txt', 'r') as f:
            variant_doc = f.read()
    except FileNotFoundError:
        print("Test documents not found. Please ensure original_doc.txt and variant_doc.txt exist.")
        return
    
    # Run chunked alignment
    result = aligner.run_chunked_alignment(original_doc, variant_doc)
    
    print(f"\n🎉 Processing complete!")
    print(f"Total words processed: {result.total_words_processed:,}")
    print(f"Processing time: {result.processing_time:.2f}s")
    print(f"Words per second: {result.total_words_processed/result.processing_time:.1f}")

if __name__ == "__main__":
    main()
