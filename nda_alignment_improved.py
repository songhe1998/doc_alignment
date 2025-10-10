#!/usr/bin/env python3
"""
Improved NDA alignment that handles documents without subsection numbering.
Uses a more flexible approach that can analyze document chunks even without section numbers.
"""

import os
import re
from dotenv import load_dotenv
import openai
import json
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class TopicComparison:
    """Comparison of how a topic is handled in both documents"""
    topic_name: str
    present_in_nda1: bool
    present_in_nda2: bool
    nda1_content: str
    nda2_content: str
    differences: str
    confidence: str

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using PyPDF2."""
    import PyPDF2
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text

def extract_simple_sections(document: str) -> Dict[str, str]:
    """
    Extract sections with simple numbering like "1.", "2.", etc.
    Returns dict of {section_num: content}
    """
    sections = {}
    lines = document.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Look for patterns like "1." or "1. Title" at start of line
        match = re.match(r'^(\d+)\.\s+(.*)$', line)
        if match:
            # Save previous section
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            
            # Start new section
            current_section = match.group(1)
            remaining = match.group(2).strip()
            current_content = [remaining] if remaining else []
        elif current_section:
            current_content.append(line)
    
    # Don't forget last section
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections

def identify_nda_standard_topics(client: openai.OpenAI) -> List[Dict]:
    """Get standard topics for NDAs using LLM."""
    prompt = """Based on your knowledge of Non-Disclosure Agreements (NDAs), what are the typical topics and clauses found in such agreements?

Provide a JSON array where each object has:
- "topic_name": the general topic (e.g., "Definitions", "Confidential Information", "Obligations")
- "description": brief description of what this topic covers
- "importance": "essential" (must have), "common" (usually included), or "optional"

Focus on 10-15 most important topics for NDAs.
Return only the JSON array, no other text."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
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
    
    return json.loads(json_str)

def extract_topic_content(client: openai.OpenAI, document: str, topic: Dict) -> Tuple[bool, str]:
    """
    Check if a topic is present in the document and extract relevant content.
    Returns (is_present, content)
    """
    # Take a reasonable chunk of the document (first 3000 chars if too long)
    doc_preview = document[:4000] if len(document) > 4000 else document
    
    prompt = f"""Analyze this legal document to determine if it covers the topic: "{topic['topic_name']}"

Topic description: {topic['description']}

Document:
{doc_preview}

Provide a JSON object with:
- "is_present": true/false indicating if this topic is covered
- "content": if present, provide a 2-3 sentence summary of how this topic is addressed. If not present, return empty string.

Return only the JSON object, no other text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
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
        elif not json_str.startswith('{'):
            start_idx = json_str.find('{')
            end_idx = json_str.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = json_str[start_idx:end_idx+1]
        
        data = json.loads(json_str)
        return data.get("is_present", False), data.get("content", "")
    except Exception as e:
        print(f"   Error extracting topic '{topic['topic_name']}': {e}")
        return False, ""

def compare_topic_handling(client: openai.OpenAI, topic_name: str, nda1_content: str, 
                           nda2_content: str, both_present: bool) -> Tuple[str, str]:
    """
    Compare how a topic is handled in both documents.
    Returns (differences, confidence)
    """
    if not both_present:
        return "Topic not present in both documents", "low"
    
    prompt = f"""Compare how the topic "{topic_name}" is addressed in these two NDA documents:

NDA 1 approach:
{nda1_content}

NDA 2 approach:
{nda2_content}

Provide a concise 2-3 sentence comparison highlighting the key differences or similarities.
Focus on substantive differences in scope, obligations, or terms.

Also assess confidence: "high" if both clearly address the topic, "medium" if one is vague, "low" if unclear."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.3
        )
        
        differences = response.choices[0].message.content.strip()
        
        # Simple heuristic for confidence
        if "similar" in differences.lower() or "both" in differences.lower():
            confidence = "high"
        elif "unclear" in differences.lower() or "limited" in differences.lower():
            confidence = "low"
        else:
            confidence = "medium"
        
        return differences, confidence
    except Exception as e:
        return f"Error comparing: {str(e)}", "low"

def main():
    """Main function."""
    print("=" * 80)
    print("📄 IMPROVED NDA ALIGNMENT - Topic-Based Analysis")
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
    print("📄 Extracting text from NDAs...")
    nda1_text = extract_text_from_pdf(pdf1_path)
    nda2_text = extract_text_from_pdf(pdf2_path)
    print(f"   NDA 1: {len(nda1_text.split())} words")
    print(f"   NDA 2: {len(nda2_text.split())} words")
    print()
    
    # Try to extract sections
    print("📑 Extracting sections...")
    nda1_sections = extract_simple_sections(nda1_text)
    nda2_sections = extract_simple_sections(nda2_text)
    print(f"   NDA 1: {len(nda1_sections)} sections")
    print(f"   NDA 2: {len(nda2_sections)} sections")
    print()
    
    # Get standard NDA topics
    print("🔍 Identifying standard NDA topics...")
    standard_topics = identify_nda_standard_topics(client)
    print(f"   Found {len(standard_topics)} standard topics")
    
    # Show essential topics
    essential = [t for t in standard_topics if t.get('importance') == 'essential']
    print(f"   Essential topics: {', '.join([t['topic_name'] for t in essential[:5]])}")
    print()
    
    # Analyze each topic in both documents
    print("🔬 Analyzing topic coverage in both NDAs...")
    print("-" * 80)
    
    comparisons = []
    
    for i, topic in enumerate(standard_topics, 1):
        topic_name = topic['topic_name']
        print(f"\n{i}. Analyzing: {topic_name}")
        
        # Check NDA 1
        print(f"   Checking NDA 1...", end=" ")
        present1, content1 = extract_topic_content(client, nda1_text, topic)
        print(f"{'✅ Present' if present1 else '❌ Not found'}")
        
        # Check NDA 2
        print(f"   Checking NDA 2...", end=" ")
        present2, content2 = extract_topic_content(client, nda2_text, topic)
        print(f"{'✅ Present' if present2 else '❌ Not found'}")
        
        # Compare if both present
        if present1 and present2:
            print(f"   Comparing approaches...", end=" ")
            differences, confidence = compare_topic_handling(
                client, topic_name, content1, content2, True
            )
            print(f"{confidence} confidence")
        elif present1:
            differences = "Topic only present in NDA 1"
            confidence = "low"
        elif present2:
            differences = "Topic only present in NDA 2"
            confidence = "low"
        else:
            differences = "Topic not found in either NDA"
            confidence = "low"
        
        comparisons.append(TopicComparison(
            topic_name=topic_name,
            present_in_nda1=present1,
            present_in_nda2=present2,
            nda1_content=content1,
            nda2_content=content2,
            differences=differences,
            confidence=confidence
        ))
    
    # Display results
    print("\n" + "=" * 80)
    print("📊 ALIGNMENT RESULTS")
    print("=" * 80)
    
    # Statistics
    in_both = len([c for c in comparisons if c.present_in_nda1 and c.present_in_nda2])
    only_nda1 = len([c for c in comparisons if c.present_in_nda1 and not c.present_in_nda2])
    only_nda2 = len([c for c in comparisons if c.present_in_nda2 and not c.present_in_nda1])
    in_neither = len([c for c in comparisons if not c.present_in_nda1 and not c.present_in_nda2])
    
    high_conf = len([c for c in comparisons if c.confidence == "high"])
    med_conf = len([c for c in comparisons if c.confidence == "medium"])
    low_conf = len([c for c in comparisons if c.confidence == "low"])
    
    print(f"\n📈 COVERAGE STATISTICS:")
    print(f"   Topics in both NDAs: {in_both}/{len(standard_topics)} ({in_both/len(standard_topics)*100:.1f}%)")
    print(f"   Only in NDA 1: {only_nda1}")
    print(f"   Only in NDA 2: {only_nda2}")
    print(f"   In neither: {in_neither}")
    print()
    print(f"📊 CONFIDENCE DISTRIBUTION:")
    print(f"   High confidence alignments: {high_conf}")
    print(f"   Medium confidence: {med_conf}")
    print(f"   Low confidence: {low_conf}")
    
    # Detailed comparison
    print("\n" + "=" * 80)
    print("🔍 DETAILED TOPIC COMPARISONS")
    print("=" * 80)
    
    for i, comp in enumerate(comparisons, 1):
        print(f"\n{i}. {comp.topic_name}")
        print(f"   Status: ", end="")
        if comp.present_in_nda1 and comp.present_in_nda2:
            print(f"✅ Present in both (confidence: {comp.confidence})")
        elif comp.present_in_nda1:
            print("⚠️  Only in NDA 1")
        elif comp.present_in_nda2:
            print("⚠️  Only in NDA 2")
        else:
            print("❌ Not found in either")
        
        if comp.present_in_nda1:
            print(f"\n   NDA 1: {comp.nda1_content[:200]}...")
        
        if comp.present_in_nda2:
            print(f"\n   NDA 2: {comp.nda2_content[:200]}...")
        
        if comp.present_in_nda1 and comp.present_in_nda2:
            print(f"\n   📝 Comparison: {comp.differences}")
    
    # Save results
    output_file = '/Users/songhewang/Desktop/doc_alignment/nda_comparison_results.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("NDA TOPIC-BASED COMPARISON RESULTS\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Coverage: {in_both}/{len(standard_topics)} topics in both NDAs\n")
        f.write(f"Confidence: {high_conf} high, {med_conf} medium, {low_conf} low\n\n")
        
        for comp in comparisons:
            f.write(f"\n{'='*60}\n")
            f.write(f"Topic: {comp.topic_name}\n")
            f.write(f"{'='*60}\n")
            f.write(f"Present in NDA 1: {comp.present_in_nda1}\n")
            f.write(f"Present in NDA 2: {comp.present_in_nda2}\n")
            f.write(f"Confidence: {comp.confidence}\n\n")
            
            if comp.nda1_content:
                f.write(f"NDA 1 Content:\n{comp.nda1_content}\n\n")
            
            if comp.nda2_content:
                f.write(f"NDA 2 Content:\n{comp.nda2_content}\n\n")
            
            f.write(f"Comparison:\n{comp.differences}\n")
    
    print(f"\n\n💾 Detailed results saved to: {output_file}")
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main()

