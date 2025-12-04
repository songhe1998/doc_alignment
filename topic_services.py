import time
from typing import Dict, List

import openai

from topic_alignment import TopicBasedAligner
from nda_direct_alignment import (
    extract_topics_from_document as extract_direct_topics,
    align_topics as align_direct_topics,
)
from openai_helper import create_openai_client


def _format_section_label(section_id: str, sections: Dict[str, tuple]) -> str:
    """Return a stable label for a section id."""
    title, _ = sections.get(section_id, ("", ""))
    title = title.strip()
    if title:
        return f"{section_id} {title}".strip()
    return section_id.strip()


def _summarize_sections(section_ids: List[str], sections: Dict[str, tuple]) -> str:
    """Create a short textual summary for UI cards."""
    snippets = []
    for sec_id in section_ids:
        title, content = sections.get(sec_id, ("", ""))
        if not title and not content:
            continue
        preview = " ".join(content.split())[:220]
        label = title or sec_id
        snippets.append(f"{label}: {preview}")
    return " ".join(snippets[:2])


def run_topic_template_alignment(api_key: str, doc1_text: str, doc2_text: str) -> Dict:
    """
    Use the TopicBasedAligner pipeline to perform template/topic alignment
    between doc1 and doc2. Returns a dict ready for API/UI consumption.
    """
    start_time = time.time()
    aligner = TopicBasedAligner(api_key)

    doc_type = aligner.identify_document_type(doc1_text)
    standard_topics = aligner.research_standard_topics(doc_type.document_type)
    if not standard_topics:
        raise RuntimeError(
            "Failed to load standard topics from OpenAI. "
            "This often occurs when the API quota is exhausted or the request failed."
        )

    doc1_sections = aligner.extract_sections(doc1_text)
    doc2_sections = aligner.extract_sections(doc2_text)

    doc1_topics = aligner.identify_topics_in_document(
        doc1_text, doc1_sections, standard_topics, "doc1"
    )
    doc2_topics = aligner.identify_topics_in_document(
        doc2_text, doc2_sections, standard_topics, "doc2"
    )
    if not doc1_topics.topics and not doc2_topics.topics:
        raise RuntimeError(
            "Topic extraction returned no data for either document. "
            "Check the OpenAI API status or your quota limits."
        )

    topic_alignments = aligner.align_topics(
        doc1_topics, doc2_topics, doc1_sections, doc2_sections
    )

    topic_desc_map = {topic.topic_name: topic.description for topic in standard_topics}
    alignments_payload = []
    for idx, alignment in enumerate(topic_alignments):
        entry = {
            "id": idx,
            "topic_name": alignment.topic_name,
            "topic_description": topic_desc_map.get(alignment.topic_name, ""),
            "doc1_sections": [
                _format_section_label(sec_id, doc1_sections)
                for sec_id in alignment.original_sections
            ],
            "doc2_sections": [
                _format_section_label(sec_id, doc2_sections)
                for sec_id in alignment.variant_sections
            ],
            "doc1_summary": _summarize_sections(
                alignment.original_sections, doc1_sections
            ),
            "doc2_summary": _summarize_sections(
                alignment.variant_sections, doc2_sections
            ),
            "differences": alignment.content_differences,
            "confidence": alignment.alignment_confidence,
        }
        alignments_payload.append(entry)

    topics_in_both = len(
        [
            a
            for a in alignments_payload
            if a["doc1_sections"] and a["doc2_sections"]
        ]
    )

    return {
        "method": "Topic-Based Alignment (Template)",
        "document_type": doc_type.document_type,
        "document_type_confidence": doc_type.confidence,
        "standard_topics": len(standard_topics),
        "doc1_topics": len(doc1_topics.topics),
        "doc2_topics": len(doc2_topics.topics),
        "doc1_sections_count": len(doc1_sections),
        "doc2_sections_count": len(doc2_sections),
        "topics_in_both": topics_in_both,
        "alignments_found": len(alignments_payload),
        "alignments": alignments_payload,
        "processing_time": time.time() - start_time,
    }


def run_topic_direct_alignment(api_key: str, doc1_text: str, doc2_text: str) -> Dict:
    """
    Run the direct topic-alignment workflow (no templates). Uses the
    nda_direct_alignment helper functions under the hood.
    """
    import re
    
    start_time = time.time()
    client = create_openai_client(api_key)

    doc1_topics = extract_direct_topics(client, doc1_text, "Document 1")
    doc2_topics = extract_direct_topics(client, doc2_text, "Document 2")
    if not doc1_topics and not doc2_topics:
        raise RuntimeError(
            "Failed to extract topics from either document. "
            "Verify that the OpenAI API key has sufficient quota."
        )

    topic_alignments = align_direct_topics(client, doc1_topics, doc2_topics)

    alignments_payload = []
    for idx, alignment in enumerate(topic_alignments):
        doc1_topic = alignment.doc1_topic
        doc2_topic = alignment.doc2_topic
        topic_name = (
            doc1_topic.topic_name
            if doc1_topic.topic_name != "[Not Present]"
            else doc2_topic.topic_name
        )
        
        # For direct method, use key points as "sections" for display
        # If no key points, use relevant_content snippet for highlighting
        doc1_sections = []
        doc2_sections = []
        
        # Use key points if available, otherwise extract from content
        if doc1_topic.topic_name != "[Not Present]":
            if doc1_topic.key_points:
                doc1_sections = doc1_topic.key_points[:3]
            elif doc1_topic.relevant_content:
                # Extract meaningful snippets from content for highlighting
                content_lines = doc1_topic.relevant_content.split('.')[:2]
                doc1_sections = [line.strip()[:100] for line in content_lines if line.strip()]
        
        if doc2_topic.topic_name != "[Not Present]":
            if doc2_topic.key_points:
                doc2_sections = doc2_topic.key_points[:3]
            elif doc2_topic.relevant_content:
                content_lines = doc2_topic.relevant_content.split('.')[:2]
                doc2_sections = [line.strip()[:100] for line in content_lines if line.strip()]

        entry = {
            "id": idx,
            "topic_name": topic_name,
            "doc1_sections": doc1_sections,
            "doc2_sections": doc2_sections,
            "doc1_summary": doc1_topic.relevant_content,
            "doc2_summary": doc2_topic.relevant_content,
            "differences": alignment.key_differences,
            "confidence": alignment.similarity_score,
            "alignment_rationale": alignment.alignment_rationale,
        }
        alignments_payload.append(entry)

    topics_in_both = len(
        [
            a
            for a in alignments_payload
            if a["doc1_sections"] and a["doc2_sections"]
        ]
    )

    return {
        "method": "Direct Topic-Based Alignment",
        "doc1_topics": len(doc1_topics),
        "doc2_topics": len(doc2_topics),
        "topics_in_both": topics_in_both,
        "alignments_found": len(topic_alignments),
        "alignments": alignments_payload,
        "processing_time": time.time() - start_time,
    }
