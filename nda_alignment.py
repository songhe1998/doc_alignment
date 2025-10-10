#!/usr/bin/env python3
"""
Run topic-based alignment on the two NDA PDF documents.
"""

import os
import sys
from dotenv import load_dotenv
from topic_alignment import TopicBasedAligner

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file using PyPDF2.
    """
    try:
        import PyPDF2
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            return text
    except ImportError:
        print("❌ PyPDF2 not installed. Trying pdfplumber...")
        try:
            import pdfplumber
            
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            return text
        except ImportError:
            print("❌ Neither PyPDF2 nor pdfplumber is installed.")
            print("Please install one: pip install PyPDF2 or pip install pdfplumber")
            sys.exit(1)

def main():
    """Main function to align NDA documents."""
    print("=" * 80)
    print("📄 NDA DOCUMENT ALIGNMENT USING TOPIC-BASED APPROACH")
    print("=" * 80)
    print()
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your OpenAI API key.")
        return
    
    # Define PDF paths
    pdf1_path = '/Users/songhewang/Desktop/doc_alignment/nda_1.pdf'
    pdf2_path = '/Users/songhewang/Desktop/doc_alignment/nda_2.pdf'
    
    # Check if PDFs exist
    if not os.path.exists(pdf1_path):
        print(f"❌ NDA 1 not found at: {pdf1_path}")
        return
    if not os.path.exists(pdf2_path):
        print(f"❌ NDA 2 not found at: {pdf2_path}")
        return
    
    # Extract text from PDFs
    print("📄 Extracting text from NDA documents...")
    print(f"   Reading: {os.path.basename(pdf1_path)}")
    nda1_text = extract_text_from_pdf(pdf1_path)
    print(f"   ✅ Extracted {len(nda1_text)} characters ({len(nda1_text.split())} words)")
    
    print(f"   Reading: {os.path.basename(pdf2_path)}")
    nda2_text = extract_text_from_pdf(pdf2_path)
    print(f"   ✅ Extracted {len(nda2_text)} characters ({len(nda2_text.split())} words)")
    print()
    
    # Save extracted text for reference
    with open('/Users/songhewang/Desktop/doc_alignment/nda_1_extracted.txt', 'w') as f:
        f.write(nda1_text)
    with open('/Users/songhewang/Desktop/doc_alignment/nda_2_extracted.txt', 'w') as f:
        f.write(nda2_text)
    print("💾 Saved extracted text to nda_1_extracted.txt and nda_2_extracted.txt")
    print()
    
    # Initialize topic-based aligner
    print("🔧 Initializing topic-based aligner...")
    aligner = TopicBasedAligner(api_key)
    print("   ✅ Aligner ready")
    print()
    
    # Run topic-based alignment
    print("🚀 Starting topic-based alignment on NDA documents...")
    print("-" * 80)
    print()
    
    result = aligner.run_topic_alignment(nda1_text, nda2_text, verbose=True)
    
    # Display final summary
    print("\n" + "=" * 80)
    print("🎉 NDA ALIGNMENT COMPLETE!")
    print("=" * 80)
    
    print(f"\n📊 ALIGNMENT SUMMARY:")
    print(f"   • Document Type: {result.document_type.document_type}")
    print(f"   • Confidence: {result.document_type.confidence}")
    print(f"   • Standard Topics: {len(result.standard_topics)}")
    print(f"   • Topics in NDA 1: {len(result.original_topics.topics)}")
    print(f"   • Topics in NDA 2: {len(result.variant_topics.topics)}")
    print(f"   • Total Alignments: {len(result.topic_alignments)}")
    print(f"   • Processing Time: {result.processing_time:.2f}s")
    
    # Calculate detailed statistics
    common_topics = [a for a in result.topic_alignments 
                    if a.original_sections and a.variant_sections]
    only_nda1 = [a for a in result.topic_alignments 
                 if a.original_sections and not a.variant_sections]
    only_nda2 = [a for a in result.topic_alignments 
                 if not a.original_sections and a.variant_sections]
    
    high_confidence = [a for a in common_topics if a.alignment_confidence == "high"]
    medium_confidence = [a for a in common_topics if a.alignment_confidence == "medium"]
    low_confidence = [a for a in common_topics if a.alignment_confidence == "low"]
    
    print(f"\n📈 DETAILED STATISTICS:")
    print(f"   Common Topics:")
    print(f"      • In both NDAs: {len(common_topics)}")
    print(f"      • High confidence: {len(high_confidence)}")
    print(f"      • Medium confidence: {len(medium_confidence)}")
    print(f"      • Low confidence: {len(low_confidence)}")
    print(f"   Unique Topics:")
    print(f"      • Only in NDA 1: {len(only_nda1)}")
    print(f"      • Only in NDA 2: {len(only_nda2)}")
    print(f"   Coverage:")
    print(f"      • {(len(common_topics)/len(result.standard_topics)*100):.1f}% of standard topics covered")
    
    # Show key differences
    if only_nda1:
        print(f"\n🔍 TOPICS ONLY IN NDA 1:")
        for alignment in only_nda1[:5]:  # Show first 5
            print(f"   • {alignment.topic_name}")
    
    if only_nda2:
        print(f"\n🔍 TOPICS ONLY IN NDA 2:")
        for alignment in only_nda2[:5]:  # Show first 5
            print(f"   • {alignment.topic_name}")
    
    # Save detailed results to file
    output_file = '/Users/songhewang/Desktop/doc_alignment/nda_alignment_results.txt'
    with open(output_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("NDA DOCUMENT ALIGNMENT RESULTS\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Document Type: {result.document_type.document_type}\n")
        f.write(f"Confidence: {result.document_type.confidence}\n")
        f.write(f"Key Characteristics:\n")
        for char in result.document_type.key_characteristics:
            f.write(f"  - {char}\n")
        f.write("\n")
        
        f.write("STANDARD TOPICS:\n")
        f.write("-" * 80 + "\n")
        for topic in result.standard_topics:
            f.write(f"\n{topic.topic_name} ({topic.importance}):\n")
            f.write(f"  {topic.description}\n")
        f.write("\n")
        
        f.write("TOPIC ALIGNMENTS:\n")
        f.write("=" * 80 + "\n")
        for i, alignment in enumerate(result.topic_alignments, 1):
            f.write(f"\n{i}. {alignment.topic_name}\n")
            f.write(f"   Confidence: {alignment.alignment_confidence}\n")
            f.write(f"   NDA 1 sections: {', '.join(alignment.original_sections) if alignment.original_sections else 'None'}\n")
            f.write(f"   NDA 2 sections: {', '.join(alignment.variant_sections) if alignment.variant_sections else 'None'}\n")
            f.write(f"   Differences:\n")
            f.write(f"   {alignment.content_differences}\n")
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    print()
    print("✅ All done! Check the output files for detailed analysis.")

if __name__ == "__main__":
    main()

