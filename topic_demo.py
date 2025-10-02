#!/usr/bin/env python3
"""
Demo script for the topic-based document alignment system.
This demonstrates how to identify document types and align based on standard legal topics.
"""

import os
from dotenv import load_dotenv
from topic_alignment import TopicBasedAligner

def main():
    """Main demo function."""
    print("🚀 Topic-Based Document Alignment Demo")
    print("=" * 60)
    print()
    print("This demo will:")
    print("  1. Identify what type of legal document it is")
    print("  2. Research standard topics for that document type")
    print("  3. Extract topics from both documents")
    print("  4. Align documents based on topics")
    print("  5. Compare content for each topic")
    print()
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your OpenAI API key.")
        return
    
    # Load sample documents
    print("📄 Loading sample documents...")
    try:
        with open('/Users/songhewang/Desktop/doc_alignment/original_doc.txt', 'r') as f:
            original_doc = f.read()
        with open('/Users/songhewang/Desktop/doc_alignment/variant_doc.txt', 'r') as f:
            variant_doc = f.read()
        
        print(f"   ✅ Original document loaded ({len(original_doc.split())} words)")
        print(f"   ✅ Variant document loaded ({len(variant_doc.split())} words)")
        print()
        
    except FileNotFoundError:
        print("❌ Test documents not found.")
        print("Please ensure original_doc.txt and variant_doc.txt exist in the directory.")
        return
    
    # Initialize aligner
    print("🔧 Initializing topic-based aligner...")
    aligner = TopicBasedAligner(api_key)
    print()
    
    # Run topic-based alignment
    print("🎯 Starting topic-based alignment process...")
    print("-" * 60)
    print()
    
    result = aligner.run_topic_alignment(original_doc, variant_doc, verbose=True)
    
    # Display final summary
    print("\n" + "=" * 60)
    print("🎉 Demo Complete!")
    print("=" * 60)
    print(f"\n📊 Results Summary:")
    print(f"   • Document Type: {result.document_type.document_type}")
    print(f"   • Standard Topics: {len(result.standard_topics)}")
    print(f"   • Topics in Original: {len(result.original_topics.topics)}")
    print(f"   • Topics in Variant: {len(result.variant_topics.topics)}")
    print(f"   • Topic Alignments: {len(result.topic_alignments)}")
    print(f"   • Processing Time: {result.processing_time:.2f}s")
    
    # Calculate coverage statistics
    common_topics = len([a for a in result.topic_alignments 
                        if a.original_sections and a.variant_sections])
    high_confidence = len([a for a in result.topic_alignments 
                          if a.alignment_confidence == "high"])
    
    print(f"\n📈 Coverage Statistics:")
    print(f"   • Topics in both documents: {common_topics}")
    print(f"   • High confidence alignments: {high_confidence}")
    print(f"   • Coverage rate: {(common_topics/len(result.standard_topics)*100):.1f}%")
    
    print("\n✅ Topic-based alignment provides a higher-level view of document structure")
    print("   and content organization compared to section-by-section alignment.")

if __name__ == "__main__":
    main()

