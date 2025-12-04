#!/usr/bin/env python3
"""
Direct topic-based alignment without standard topic templates.
Extracts topics directly from each document and aligns them.
"""

import os
import json
from dotenv import load_dotenv
import openai
from dataclasses import dataclass
from typing import List, Tuple, Dict

@dataclass
class DocumentTopic:
    """A topic identified in a document"""
    topic_name: str
    description: str
    key_points: List[str]
    relevant_content: str

@dataclass
class TopicAlignment:
    """Alignment between topics from two documents"""
    doc1_topic: DocumentTopic
    doc2_topic: DocumentTopic
    similarity_score: str  # "high", "medium", "low"
    alignment_rationale: str
    key_differences: str

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using PyPDF2."""
    import PyPDF2
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text

def extract_topics_from_document(client: openai.OpenAI, document: str, doc_name: str) -> List[DocumentTopic]:
    """
    Extract topics directly from a document without reference to standard topics.
    """
    # Limit document length for API
    doc_preview = document[:6000] if len(document) > 6000 else document
    
    prompt = f"""Analyze this legal document and identify the main topics/themes it covers.

Document:
{doc_preview}

For each topic you identify, provide:
- "topic_name": a clear name for the topic (e.g., "Confidential Information Definition", "Non-Disclosure Obligations")
- "description": what this topic is about (1-2 sentences)
- "key_points": array of 2-4 EXACT PHRASES copied verbatim from the document (do not paraphrase, copy the exact wording)
- "relevant_content": an EXACT QUOTE from the document (copy 50-100 consecutive words exactly as they appear, including any typos or formatting)

IMPORTANT: For "key_points" and "relevant_content", copy the text EXACTLY as it appears in the document. Do not paraphrase or summarize.

Focus on identifying 5-10 main topics that capture the essential elements of this document.
Return a JSON array of topics. Return only the JSON array, no other text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4 Omni - most capable model for extraction
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2500,
            temperature=0  # Set to 0 for exact extraction, not creative paraphrasing
        )
        
        json_str = response.choices[0].message.content.strip()
        
        # Clean JSON response
        if "```json" in json_str:
            json_start = json_str.find("```json") + 7
            json_end = json_str.find("```", json_start)
            json_str = json_str[json_start:json_end].strip()
        elif json_str.startswith("```"):
            json_str = json_str[3:-3].strip()
        elif not json_str.startswith('['):
            start_idx = json_str.find('[')
            end_idx = json_str.rfind(']')
            if start_idx != -1 and end_idx != -1:
                json_str = json_str[start_idx:end_idx+1]
        
        # Fix invalid JSON escape sequences from corrupted PDF text
        # The PDF has corrupted text like "aQ\" which creates invalid \escapes
        import re
        # Replace backslash followed by a character that's NOT a valid JSON escape
        # Valid JSON escapes: \", \\, \/, \b, \f, \n, \r, \t, \uXXXX
        json_str = re.sub(r'\\([^"\\/bfnrtu])', r'\1', json_str)
        
        topics_data = json.loads(json_str)
        
        topics = []
        for topic_data in topics_data:
            topics.append(DocumentTopic(
                topic_name=topic_data.get("topic_name", "Unknown"),
                description=topic_data.get("description", ""),
                key_points=topic_data.get("key_points", []),
                relevant_content=topic_data.get("relevant_content", "")
            ))
        
        return topics
    
    except Exception as e:
        print(f"   ❌ Error extracting topics from {doc_name}: {e}")
        return []

def align_topics(client: openai.OpenAI, doc1_topics: List[DocumentTopic], 
                doc2_topics: List[DocumentTopic]) -> List[TopicAlignment]:
    """
    Align topics between two documents by finding semantic matches.
    """
    # Prepare summaries for alignment
    doc1_summary = []
    for i, topic in enumerate(doc1_topics):
        summary = f"{i}. {topic.topic_name}: {topic.description}"
        doc1_summary.append(summary)
    
    doc2_summary = []
    for i, topic in enumerate(doc2_topics):
        summary = f"{i}. {topic.topic_name}: {topic.description}"
        doc2_summary.append(summary)
    
    prompt = f"""You are aligning topics between two legal documents. Find topics that are semantically related.

Document 1 Topics:
{chr(10).join(doc1_summary)}

Document 2 Topics:
{chr(10).join(doc2_summary)}

Create alignments between topics that cover similar legal concepts, even if they use different terminology.

Return a JSON array where each object has:
- "doc1_topic_index": index of topic from Document 1 (or -1 if no match)
- "doc2_topic_index": index of topic from Document 2 (or -1 if no match)
- "similarity_score": "high" (very similar), "medium" (related), or "low" (loosely related)
- "alignment_rationale": why these topics are aligned (1 sentence)

Include alignments for:
1. Topics that appear in both documents
2. Unique topics in Document 1 (doc2_topic_index = -1)
3. Unique topics in Document 2 (doc1_topic_index = -1)

Return only the JSON array, no other text."""

    try:
        response = client.chat.completions.create(
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
        elif json_str.startswith("```"):
            json_str = json_str[3:-3].strip()
        elif not json_str.startswith('['):
            start_idx = json_str.find('[')
            end_idx = json_str.rfind(']')
            if start_idx != -1 and end_idx != -1:
                json_str = json_str[start_idx:end_idx+1]
        
        alignments_data = json.loads(json_str)
        
        # Now compare content for each alignment
        alignments = []
        for alignment_data in alignments_data:
            doc1_idx = alignment_data.get("doc1_topic_index", -1)
            doc2_idx = alignment_data.get("doc2_topic_index", -1)
            similarity = alignment_data.get("similarity_score", "low")
            rationale = alignment_data.get("alignment_rationale", "")
            
            # Get topics (or None if index is -1)
            doc1_topic = doc1_topics[doc1_idx] if doc1_idx >= 0 and doc1_idx < len(doc1_topics) else None
            doc2_topic = doc2_topics[doc2_idx] if doc2_idx >= 0 and doc2_idx < len(doc2_topics) else None
            
            # Compare content if both topics exist
            if doc1_topic and doc2_topic:
                differences = compare_topic_content(
                    client, 
                    doc1_topic.topic_name,
                    doc1_topic.relevant_content,
                    doc2_topic.topic_name,
                    doc2_topic.relevant_content
                )
            elif doc1_topic:
                differences = f"Topic '{doc1_topic.topic_name}' only appears in Document 1."
            elif doc2_topic:
                differences = f"Topic '{doc2_topic.topic_name}' only appears in Document 2."
            else:
                continue  # Skip if both are None
            
            # Create placeholder topics for single-sided alignments
            if not doc1_topic:
                doc1_topic = DocumentTopic(
                    topic_name="[Not Present]",
                    description="",
                    key_points=[],
                    relevant_content=""
                )
            if not doc2_topic:
                doc2_topic = DocumentTopic(
                    topic_name="[Not Present]",
                    description="",
                    key_points=[],
                    relevant_content=""
                )
            
            alignments.append(TopicAlignment(
                doc1_topic=doc1_topic,
                doc2_topic=doc2_topic,
                similarity_score=similarity,
                alignment_rationale=rationale,
                key_differences=differences
            ))
        
        return alignments
    
    except Exception as e:
        print(f"   ❌ Error aligning topics: {e}")
        import traceback
        traceback.print_exc()
        return []

def compare_topic_content(client: openai.OpenAI, topic1_name: str, content1: str,
                         topic2_name: str, content2: str) -> str:
    """Compare how a topic is handled in both documents."""
    
    prompt = f"""Compare how these two topics are addressed in their respective documents:

Document 1 - "{topic1_name}":
{content1}

Document 2 - "{topic2_name}":
{content2}

Provide a concise 2-3 sentence comparison highlighting:
- What's similar
- What's different
- Any notable variations in scope or approach

Focus on substantive differences."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Error comparing: {str(e)}"

def main():
    """Main function."""
    print("=" * 80)
    print("📄 DIRECT TOPIC-BASED ALIGNMENT (No Template Required)")
    print("=" * 80)
    print()
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return
    
    client = openai.OpenAI(api_key=api_key)
    
    # Define paths
    pdf1_path = '/Users/songhewang/Desktop/doc_alignment/nda_1.pdf'
    pdf2_path = '/Users/songhewang/Desktop/doc_alignment/nda_2.pdf'
    
    # Extract text
    print("📄 Extracting text from PDFs...")
    nda1_text = extract_text_from_pdf(pdf1_path)
    nda2_text = extract_text_from_pdf(pdf2_path)
    print(f"   NDA 1 (JEA): {len(nda1_text.split())} words")
    print(f"   NDA 2 (Frodsham): {len(nda2_text.split())} words")
    print()
    
    # Extract topics from each document independently
    print("🔍 Extracting topics from NDA 1 (JEA)...")
    nda1_topics = extract_topics_from_document(client, nda1_text, "NDA 1")
    print(f"   ✅ Found {len(nda1_topics)} topics in NDA 1")
    
    print("\n🔍 Extracting topics from NDA 2 (Frodsham)...")
    nda2_topics = extract_topics_from_document(client, nda2_text, "NDA 2")
    print(f"   ✅ Found {len(nda2_topics)} topics in NDA 2")
    print()
    
    # Show extracted topics
    print("=" * 80)
    print("📋 TOPICS IDENTIFIED IN EACH DOCUMENT")
    print("=" * 80)
    
    print("\n📄 NDA 1 (JEA) Topics:")
    print("-" * 60)
    for i, topic in enumerate(nda1_topics, 1):
        print(f"\n{i}. {topic.topic_name}")
        print(f"   {topic.description}")
        if topic.key_points:
            print(f"   Key points: {', '.join(topic.key_points[:3])}")
    
    print("\n" + "=" * 80)
    print("\n📄 NDA 2 (Frodsham) Topics:")
    print("-" * 60)
    for i, topic in enumerate(nda2_topics, 1):
        print(f"\n{i}. {topic.topic_name}")
        print(f"   {topic.description}")
        if topic.key_points:
            print(f"   Key points: {', '.join(topic.key_points[:3])}")
    
    # Align topics
    print("\n" + "=" * 80)
    print("🔗 ALIGNING TOPICS BETWEEN DOCUMENTS...")
    print("=" * 80)
    print()
    
    alignments = align_topics(client, nda1_topics, nda2_topics)
    print(f"✅ Created {len(alignments)} topic alignments")
    
    # Display alignment results
    print("\n" + "=" * 80)
    print("📊 TOPIC ALIGNMENT RESULTS")
    print("=" * 80)
    
    # Calculate statistics
    both_present = len([a for a in alignments if a.doc1_topic.topic_name != "[Not Present]" 
                        and a.doc2_topic.topic_name != "[Not Present]"])
    only_nda1 = len([a for a in alignments if a.doc2_topic.topic_name == "[Not Present]"])
    only_nda2 = len([a for a in alignments if a.doc1_topic.topic_name == "[Not Present]"])
    
    high_sim = len([a for a in alignments if a.similarity_score == "high"])
    med_sim = len([a for a in alignments if a.similarity_score == "medium"])
    low_sim = len([a for a in alignments if a.similarity_score == "low"])
    
    print(f"\n📈 ALIGNMENT STATISTICS:")
    print(f"   Topics in both documents: {both_present}")
    print(f"   Topics only in NDA 1: {only_nda1}")
    print(f"   Topics only in NDA 2: {only_nda2}")
    print(f"   Total alignments: {len(alignments)}")
    print()
    print(f"📊 SIMILARITY DISTRIBUTION:")
    print(f"   High similarity: {high_sim}")
    print(f"   Medium similarity: {med_sim}")
    print(f"   Low similarity: {low_sim}")
    
    # Detailed alignments
    print("\n" + "=" * 80)
    print("🔍 DETAILED TOPIC ALIGNMENTS")
    print("=" * 80)
    
    for i, alignment in enumerate(alignments, 1):
        print(f"\n{'='*60}")
        print(f"Alignment {i}: {alignment.similarity_score.upper()} Similarity")
        print(f"{'='*60}")
        
        print(f"\n📄 NDA 1 Topic: {alignment.doc1_topic.topic_name}")
        if alignment.doc1_topic.description:
            print(f"   Description: {alignment.doc1_topic.description}")
            if alignment.doc1_topic.key_points:
                print(f"   Key Points:")
                for point in alignment.doc1_topic.key_points:
                    print(f"      • {point}")
        
        print(f"\n📄 NDA 2 Topic: {alignment.doc2_topic.topic_name}")
        if alignment.doc2_topic.description:
            print(f"   Description: {alignment.doc2_topic.description}")
            if alignment.doc2_topic.key_points:
                print(f"   Key Points:")
                for point in alignment.doc2_topic.key_points:
                    print(f"      • {point}")
        
        print(f"\n🔗 Alignment Rationale:")
        print(f"   {alignment.alignment_rationale}")
        
        print(f"\n📝 Key Differences:")
        print(f"   {alignment.key_differences}")
    
    # Save results
    output_file = '/Users/songhewang/Desktop/doc_alignment/nda_direct_alignment_results.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("DIRECT TOPIC-BASED ALIGNMENT RESULTS\n")
        f.write("(Without Standard Topic Templates)\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Topics in both: {both_present}\n")
        f.write(f"Only in NDA 1: {only_nda1}\n")
        f.write(f"Only in NDA 2: {only_nda2}\n")
        f.write(f"High similarity: {high_sim}, Medium: {med_sim}, Low: {low_sim}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("NDA 1 (JEA) TOPICS\n")
        f.write("=" * 80 + "\n\n")
        for i, topic in enumerate(nda1_topics, 1):
            f.write(f"{i}. {topic.topic_name}\n")
            f.write(f"   Description: {topic.description}\n")
            f.write(f"   Key Points: {', '.join(topic.key_points)}\n")
            f.write(f"   Content: {topic.relevant_content[:200]}...\n\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("NDA 2 (Frodsham) TOPICS\n")
        f.write("=" * 80 + "\n\n")
        for i, topic in enumerate(nda2_topics, 1):
            f.write(f"{i}. {topic.topic_name}\n")
            f.write(f"   Description: {topic.description}\n")
            f.write(f"   Key Points: {', '.join(topic.key_points)}\n")
            f.write(f"   Content: {topic.relevant_content[:200]}...\n\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("TOPIC ALIGNMENTS\n")
        f.write("=" * 80 + "\n\n")
        
        for i, alignment in enumerate(alignments, 1):
            f.write(f"\n{'='*60}\n")
            f.write(f"Alignment {i}: {alignment.similarity_score.upper()}\n")
            f.write(f"{'='*60}\n\n")
            f.write(f"NDA 1: {alignment.doc1_topic.topic_name}\n")
            f.write(f"NDA 2: {alignment.doc2_topic.topic_name}\n\n")
            f.write(f"Rationale: {alignment.alignment_rationale}\n\n")
            f.write(f"Differences: {alignment.key_differences}\n\n")
    
    print(f"\n\n💾 Detailed results saved to: {output_file}")
    print("\n✅ Direct topic-based alignment complete!")
    print("\n📋 Summary:")
    print(f"   • Identified {len(nda1_topics)} topics in NDA 1")
    print(f"   • Identified {len(nda2_topics)} topics in NDA 2")
    print(f"   • Created {len(alignments)} alignments")
    print(f"   • {both_present} topics found in both documents")
    print(f"   • {high_sim} high-similarity matches")

if __name__ == "__main__":
    main()

