import openai
import json
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import time
import os
from dotenv import load_dotenv
from openai_helper import create_openai_client

@dataclass
class DocumentTypeInfo:
    """Information about the identified document type"""
    document_type: str  # e.g., "NDA", "Software License Agreement", "Employment Contract"
    confidence: str  # "high", "medium", "low"
    key_characteristics: List[str]  # Key features that identify this document type
    
@dataclass
class TopicInfo:
    """Information about a legal topic"""
    topic_name: str
    description: str
    typical_sections: List[str]  # Common section titles for this topic
    importance: str  # "essential", "common", "optional"

@dataclass
class DocumentTopics:
    """Topics identified in a document"""
    document_id: str  # "original" or "variant"
    topics: List[Tuple[str, List[str]]]  # (topic_name, [section_numbers])
    
@dataclass
class TopicAlignment:
    """Alignment between topics in two documents"""
    topic_name: str
    original_sections: List[str]
    variant_sections: List[str]
    alignment_confidence: str  # "high", "medium", "low"
    content_differences: str  # Summary of key differences

@dataclass
class TopicAlignmentResult:
    """Complete result of topic-based alignment"""
    document_type: DocumentTypeInfo
    standard_topics: List[TopicInfo]
    original_topics: DocumentTopics
    variant_topics: DocumentTopics
    topic_alignments: List[TopicAlignment]
    processing_time: float

class TopicBasedAligner:
    def __init__(self, api_key: str):
        """
        Initialize the topic-based aligner.
        
        Args:
            api_key: OpenAI API key
        """
        self.client = create_openai_client(api_key)
    
    def identify_document_type(self, document: str) -> DocumentTypeInfo:
        """
        Use LLM to identify what type of legal document this is.
        
        Args:
            document: The document text to analyze
            
        Returns:
            DocumentTypeInfo with type, confidence, and characteristics
        """
        # Take a sample of the document for analysis (first 2000 characters)
        sample = document[:2000]
        
        prompt = f"""Analyze this legal document excerpt and identify what type of legal document it is.

Document excerpt:
{sample}

Provide a JSON object with:
- "document_type": the specific type (e.g., "Non-Disclosure Agreement", "Software License Agreement", "Employment Contract", "Service Agreement", "Lease Agreement", etc.)
- "confidence": "high", "medium", or "low" based on how certain you are
- "key_characteristics": array of 3-5 key features that identify this as this document type

Return only the JSON object, no other text."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
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
            
            return DocumentTypeInfo(
                document_type=data["document_type"],
                confidence=data["confidence"],
                key_characteristics=data.get("key_characteristics", [])
            )
            
        except Exception as e:
            print(f"Error identifying document type: {e}")
            return DocumentTypeInfo(
                document_type="Unknown Legal Document",
                confidence="low",
                key_characteristics=[]
            )
    
    def research_standard_topics(self, document_type: str) -> List[TopicInfo]:
        """
        Use web search to research what topics are typically covered in this document type.
        
        Args:
            document_type: The type of document (e.g., "Software License Agreement")
            
        Returns:
            List of TopicInfo describing common topics for this document type
        """
        # Use LLM with web search knowledge to identify standard topics
        prompt = f"""Based on your knowledge of legal documents, what are the typical topics and sections found in a {document_type}?

Provide a JSON array where each object represents a common topic/section with:
- "topic_name": the general topic (e.g., "Definitions", "Grant of Rights", "Payment Terms", "Termination")
- "description": brief description of what this topic covers
- "typical_sections": array of common section titles used for this topic
- "importance": "essential" (must have), "common" (usually included), or "optional" (sometimes included)

Focus on the 10-15 most important topics for this document type.
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
            
            topics_data = json.loads(json_str)
            
            topics = []
            for topic_data in topics_data:
                topics.append(TopicInfo(
                    topic_name=topic_data["topic_name"],
                    description=topic_data["description"],
                    typical_sections=topic_data.get("typical_sections", []),
                    importance=topic_data.get("importance", "common")
                ))
            
            return topics
            
        except Exception as e:
            print(f"Error researching standard topics: {e}")
            return []
    
    def extract_sections(self, document: str) -> Dict[str, Tuple[str, str]]:
        """Extract sections from document. Returns dict of {section_num: (title, content)}"""
        sections = {}
        lines = document.split('\n')
        current_section = None
        current_title = ""
        current_content = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current_section:
                    current_content.append("")
                continue
            
            # Try multiple patterns for section headers
            # Pattern 1: **1. Title** (markdown bold)
            match = re.match(r'^\*\*(\d+(?:\.\d+)*)\.\s+(.+?)\*\*$', stripped)
            
            # Pattern 2: 1. Title (with capital letter at start)
            if not match:
                match = re.match(r'^(\d+(?:\.\d+)*)\.\s+([A-Z][^\n]{2,100})\.?\s*$', stripped)
            
            # Pattern 3: More lenient - number. followed by text (handle embedded sections)
            if not match:
                # Look for section markers anywhere in the line
                match = re.search(r'\b(\d+)\.\s+([A-Z][A-Za-z\s]{3,80})\s*\.?\s*(?:\s|$)', stripped)
                if match:
                    # Make sure it's actually a section header, not just a number in text
                    section_num = match.group(1)
                    title = match.group(2).strip()
                    # Check if this looks like a section header
                    if len(title) < 100 and not title.lower().startswith('the '):
                        # Save previous section
                        if current_section:
                            sections[current_section] = (current_title, '\n'.join(current_content).strip())
                        
                        current_section = section_num
                        current_title = title
                        current_content = []
                        continue
            
            # If we found a match with earlier patterns
            if match:
                # Save previous section
                if current_section:
                    sections[current_section] = (current_title, '\n'.join(current_content).strip())
                
                current_section = match.group(1)
                current_title = match.group(2).strip()
                current_content = []
                continue
            
            # Not a header, add to current section content
            if current_section:
                current_content.append(stripped)
        
        # Save the last section
        if current_section:
            sections[current_section] = (current_title, '\n'.join(current_content).strip())
        
        # If we didn't find any sections, create a fallback
        if not sections:
            # Try to extract any numbered items as sections
            for i, line in enumerate(lines):
                stripped = line.strip()
                # Very lenient pattern - just look for numbers at start
                match = re.match(r'^(\d+)\.\s+(.{5,100})', stripped)
                if match:
                    sec_num = match.group(1)
                    title = match.group(2).strip()[:80]
                    # Gather following lines as content
                    content_lines = []
                    for j in range(i+1, min(i+20, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and not re.match(r'^\d+\.', next_line):
                            content_lines.append(next_line)
                        elif re.match(r'^\d+\.', next_line):
                            break
                    sections[sec_num] = (title, '\n'.join(content_lines).strip())
        
        return sections
    
    def identify_topics_in_document(self, document: str, sections: Dict[str, Tuple[str, str]], 
                                   standard_topics: List[TopicInfo], document_id: str) -> DocumentTopics:
        """
        Use LLM to identify which standard topics appear in the document and map them to sections.
        
        Args:
            document: The full document text
            sections: Extracted sections {section_num: (title, content)}
            standard_topics: List of standard topics for this document type
            document_id: "original" or "variant"
            
        Returns:
            DocumentTopics with mapped topics and their sections
        """
        # Prepare section summary
        section_summary = []
        for sec_num, (title, content) in sections.items():
            preview = content[:150] + "..." if len(content) > 150 else content
            section_summary.append(f"Section {sec_num}: {title}\nContent: {preview}")
        
        # Prepare standard topics summary
        topics_summary = []
        for topic in standard_topics:
            topics_summary.append(f"- {topic.topic_name}: {topic.description}")
        
        prompt = f"""Analyze this legal document and identify which of the standard topics appear in it.

Standard Topics for this document type:
{chr(10).join(topics_summary)}

Document Sections:
{chr(10).join(section_summary)}

For each standard topic that appears in the document, identify which section(s) cover that topic.

Provide a JSON array where each object has:
- "topic_name": the standard topic name (must match one from the list above)
- "section_numbers": array of section numbers that cover this topic (e.g., ["1.1", "1.2", "2"])

Only include topics that are actually present in the document.
Return only the JSON array, no other text."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
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
            
            topics_data = json.loads(json_str)
            
            topics = []
            for topic_data in topics_data:
                topics.append((
                    topic_data["topic_name"],
                    topic_data.get("section_numbers", [])
                ))
            
            return DocumentTopics(
                document_id=document_id,
                topics=topics
            )
            
        except Exception as e:
            print(f"Error identifying topics in {document_id} document: {e}")
            return DocumentTopics(document_id=document_id, topics=[])
    
    def align_topics(self, original_topics: DocumentTopics, variant_topics: DocumentTopics,
                    original_sections: Dict[str, Tuple[str, str]], 
                    variant_sections: Dict[str, Tuple[str, str]]) -> List[TopicAlignment]:
        """
        Align topics between original and variant documents and compare their content.
        
        Args:
            original_topics: Topics identified in original document
            variant_topics: Topics identified in variant document
            original_sections: Sections from original document
            variant_sections: Sections from variant document
            
        Returns:
            List of TopicAlignment objects
        """
        alignments = []
        
        # Create dictionaries for easy lookup
        original_topic_dict = {topic_name: sections for topic_name, sections in original_topics.topics}
        variant_topic_dict = {topic_name: sections for topic_name, sections in variant_topics.topics}
        
        # Find topics that appear in both documents
        common_topics = set(original_topic_dict.keys()) & set(variant_topic_dict.keys())
        
        for topic_name in common_topics:
            original_secs = original_topic_dict[topic_name]
            variant_secs = variant_topic_dict[topic_name]
            
            # Get content for these sections
            original_content = []
            for sec_num in original_secs:
                if sec_num in original_sections:
                    title, content = original_sections[sec_num]
                    original_content.append(f"{title}: {content[:300]}")
            
            variant_content = []
            for sec_num in variant_secs:
                if sec_num in variant_sections:
                    title, content = variant_sections[sec_num]
                    variant_content.append(f"{title}: {content[:300]}")
            
            # Compare content using LLM
            differences = self._compare_topic_content(
                topic_name, 
                "\n".join(original_content), 
                "\n".join(variant_content)
            )
            
            # Determine confidence based on number of sections matched
            if len(original_secs) > 0 and len(variant_secs) > 0:
                confidence = "high"
            elif len(original_secs) == 0 or len(variant_secs) == 0:
                confidence = "low"
            else:
                confidence = "medium"
            
            alignments.append(TopicAlignment(
                topic_name=topic_name,
                original_sections=original_secs,
                variant_sections=variant_secs,
                alignment_confidence=confidence,
                content_differences=differences
            ))
        
        # Identify topics only in original
        only_original = set(original_topic_dict.keys()) - set(variant_topic_dict.keys())
        for topic_name in only_original:
            alignments.append(TopicAlignment(
                topic_name=topic_name,
                original_sections=original_topic_dict[topic_name],
                variant_sections=[],
                alignment_confidence="low",
                content_differences=f"Topic '{topic_name}' appears only in original document"
            ))
        
        # Identify topics only in variant
        only_variant = set(variant_topic_dict.keys()) - set(original_topic_dict.keys())
        for topic_name in only_variant:
            alignments.append(TopicAlignment(
                topic_name=topic_name,
                original_sections=[],
                variant_sections=variant_topic_dict[topic_name],
                alignment_confidence="low",
                content_differences=f"Topic '{topic_name}' appears only in variant document"
            ))
        
        return alignments
    
    def _compare_topic_content(self, topic_name: str, original_content: str, 
                              variant_content: str) -> str:
        """Compare content for a specific topic using LLM"""
        
        prompt = f"""Compare how the topic "{topic_name}" is handled in these two legal document versions.

Original Document Content:
{original_content}

Variant Document Content:
{variant_content}

Provide a concise summary (2-3 sentences) of the key differences in how this topic is addressed.
Focus on substantive differences in terms, obligations, rights, or conditions.
If the content is substantially similar, state that."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error comparing topic content: {e}")
            return "Error comparing content"
    
    def run_topic_alignment(self, original_doc: str, variant_doc: str, 
                          verbose: bool = True) -> TopicAlignmentResult:
        """
        Run the complete topic-based alignment pipeline.
        
        Args:
            original_doc: Original document text
            variant_doc: Variant document text
            verbose: Whether to print detailed progress
            
        Returns:
            TopicAlignmentResult with complete alignment information
        """
        start_time = time.time()
        
        if verbose:
            print("🚀 Starting Topic-Based Document Alignment Pipeline\n")
        
        # Step 1: Identify document type
        if verbose:
            print("📋 Step 1: Identifying document type...")
        doc_type = self.identify_document_type(original_doc)
        if verbose:
            print(f"   ✅ Document Type: {doc_type.document_type} (confidence: {doc_type.confidence})")
            print(f"   Key characteristics: {', '.join(doc_type.key_characteristics)}\n")
        
        # Step 2: Research standard topics for this document type
        if verbose:
            print(f"🔍 Step 2: Researching standard topics for {doc_type.document_type}...")
        standard_topics = self.research_standard_topics(doc_type.document_type)
        if verbose:
            print(f"   ✅ Found {len(standard_topics)} standard topics")
            for topic in standard_topics[:5]:  # Show first 5
                print(f"      • {topic.topic_name} ({topic.importance})")
            if len(standard_topics) > 5:
                print(f"      ... and {len(standard_topics) - 5} more\n")
        
        # Step 3: Extract sections from both documents
        if verbose:
            print("📄 Step 3: Extracting sections from documents...")
        original_sections = self.extract_sections(original_doc)
        variant_sections = self.extract_sections(variant_doc)
        if verbose:
            print(f"   Original document: {len(original_sections)} sections")
            print(f"   Variant document: {len(variant_sections)} sections\n")
        
        # Step 4: Identify topics in each document
        if verbose:
            print("🏷️  Step 4: Identifying topics in original document...")
        original_topics = self.identify_topics_in_document(
            original_doc, original_sections, standard_topics, "original"
        )
        if verbose:
            print(f"   ✅ Found {len(original_topics.topics)} topics in original\n")
        
        if verbose:
            print("🏷️  Step 5: Identifying topics in variant document...")
        variant_topics = self.identify_topics_in_document(
            variant_doc, variant_sections, standard_topics, "variant"
        )
        if verbose:
            print(f"   ✅ Found {len(variant_topics.topics)} topics in variant\n")
        
        # Step 5: Align topics between documents
        if verbose:
            print("🔗 Step 6: Aligning topics between documents...")
        topic_alignments = self.align_topics(
            original_topics, variant_topics, 
            original_sections, variant_sections
        )
        if verbose:
            print(f"   ✅ Created {len(topic_alignments)} topic alignments\n")
        
        # Step 6: Display results
        if verbose:
            self._display_results(doc_type, standard_topics, original_topics, 
                                variant_topics, topic_alignments)
        
        processing_time = time.time() - start_time
        
        return TopicAlignmentResult(
            document_type=doc_type,
            standard_topics=standard_topics,
            original_topics=original_topics,
            variant_topics=variant_topics,
            topic_alignments=topic_alignments,
            processing_time=processing_time
        )
    
    def _display_results(self, doc_type: DocumentTypeInfo, standard_topics: List[TopicInfo],
                        original_topics: DocumentTopics, variant_topics: DocumentTopics,
                        topic_alignments: List[TopicAlignment]):
        """Display topic alignment results in a formatted way"""
        
        print("=" * 100)
        print("📊 TOPIC-BASED ALIGNMENT RESULTS")
        print("=" * 100)
        
        # Document type
        print(f"\n📋 DOCUMENT TYPE: {doc_type.document_type}")
        print(f"   Confidence: {doc_type.confidence}")
        print(f"   Characteristics: {', '.join(doc_type.key_characteristics)}")
        
        # Standard topics
        print(f"\n📚 STANDARD TOPICS FOR {doc_type.document_type.upper()}:")
        print("-" * 80)
        essential = [t for t in standard_topics if t.importance == "essential"]
        common = [t for t in standard_topics if t.importance == "common"]
        optional = [t for t in standard_topics if t.importance == "optional"]
        
        if essential:
            print("\n   Essential Topics:")
            for topic in essential:
                print(f"      • {topic.topic_name}: {topic.description}")
        
        if common:
            print("\n   Common Topics:")
            for topic in common[:5]:  # Show first 5
                print(f"      • {topic.topic_name}: {topic.description}")
            if len(common) > 5:
                print(f"      ... and {len(common) - 5} more")
        
        # Topic mappings
        print(f"\n🗺️  TOPIC MAPPINGS:")
        print("-" * 80)
        
        print(f"\nOriginal Document Topics ({len(original_topics.topics)}):")
        for topic_name, sections in original_topics.topics:
            print(f"   • {topic_name}: sections {', '.join(sections)}")
        
        print(f"\nVariant Document Topics ({len(variant_topics.topics)}):")
        for topic_name, sections in variant_topics.topics:
            print(f"   • {topic_name}: sections {', '.join(sections)}")
        
        # Topic alignments
        print(f"\n🔗 TOPIC ALIGNMENTS:")
        print("=" * 100)
        
        for i, alignment in enumerate(topic_alignments, 1):
            print(f"\n{i}. Topic: {alignment.topic_name}")
            print(f"   Confidence: {alignment.alignment_confidence}")
            print(f"   Original sections: {', '.join(alignment.original_sections) if alignment.original_sections else 'None'}")
            print(f"   Variant sections: {', '.join(alignment.variant_sections) if alignment.variant_sections else 'None'}")
            print(f"   Differences: {alignment.content_differences}")
        
        # Summary statistics
        print(f"\n📈 SUMMARY STATISTICS:")
        print("-" * 80)
        common_topics = len([a for a in topic_alignments if a.original_sections and a.variant_sections])
        only_original = len([a for a in topic_alignments if a.original_sections and not a.variant_sections])
        only_variant = len([a for a in topic_alignments if not a.original_sections and a.variant_sections])
        
        print(f"Total standard topics: {len(standard_topics)}")
        print(f"Topics in both documents: {common_topics}")
        print(f"Topics only in original: {only_original}")
        print(f"Topics only in variant: {only_variant}")
        print(f"Topic coverage: {(common_topics/len(standard_topics)*100):.1f}%")
        
        print("\n✅ Topic-based alignment complete!")

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")
    
    # Initialize topic-based aligner
    aligner = TopicBasedAligner(api_key)
    
    # Load test documents
    try:
        with open('/Users/songhewang/Desktop/doc_alignment/original_doc.txt', 'r') as f:
            original_doc = f.read()
        with open('/Users/songhewang/Desktop/doc_alignment/variant_doc.txt', 'r') as f:
            variant_doc = f.read()
    except FileNotFoundError:
        print("Test documents not found. Please ensure original_doc.txt and variant_doc.txt exist.")
        return
    
    # Run topic-based alignment
    result = aligner.run_topic_alignment(original_doc, variant_doc)
    
    print(f"\n🎉 Processing complete!")
    print(f"Processing time: {result.processing_time:.2f}s")

if __name__ == "__main__":
    main()

