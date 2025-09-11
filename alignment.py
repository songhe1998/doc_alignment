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
class SectionMapping:
    doc_section: str
    template_section: str
    doc_title: str
    template_title: str
    confidence: str

@dataclass
class ContentDifference:
    in_doc_not_template: List[str]
    in_template_not_doc: List[str]

@dataclass
class AlignmentResult:
    pair_id: int
    doc_sections_count: int
    template_sections_count: int
    alignments_found: int
    section_mappings: List[SectionMapping]
    content_differences: List[Tuple[str, str, ContentDifference]]  # (doc_section, template_section, diff)
    processing_time: float

@dataclass
class EvaluationScore:
    pair_id: int
    section_alignment_accuracy: float  # 0-10 scale
    content_comparison_quality: float  # 0-10 scale
    overall_completeness: float  # 0-10 scale
    comments: str
    overall_score: float  # Average of the three scores

class LegalDocumentAligner:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    def generate_legal_document(self, document_type: str = "software_license") -> str:
        """Generate a synthetic legal document using ChatGPT"""
        prompt = f"""Generate a comprehensive legal document of approximately 2000 words for a {document_type} agreement. 
        The document should include:
        - Multiple numbered sections (e.g., 1.1, 1.2, 2.1, 2.2, etc.)
        - Clear section titles
        - Detailed legal language
        - Common legal sections like: Definitions, Terms and Conditions, Liability, Termination, etc.
        
        Format it with clear section numbering like:
        1. DEFINITIONS
        1.1 [content]
        1.2 [content]
        2. TERMS AND CONDITIONS
        2.1 [content]
        etc.
        
        Make it realistic and comprehensive."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating document: {e}")
            return ""
    
    def create_document_variant(self, original_doc: str) -> str:
        """Create a variant of the original document by shuffling, adding, and removing content"""
        prompt = f"""Take the following legal document and create a variant by:
        1. Changing some section numbers (e.g., move content from section 2.3 to 3.4)
        2. Adding 2-3 new sections with relevant content
        3. Removing 1-2 sections from the original
        4. Modifying some existing section content while keeping the core meaning
        5. Keep the overall structure similar but not identical
        
        Original document:
        {original_doc}
        
        Return the modified document with clear section numbering."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.8
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error creating variant: {e}")
            return ""
    
    def extract_sections(self, document: str) -> Dict[str, Tuple[str, str]]:
        """Extract sections from document. Returns dict of {section_num: (title, content)}"""
        sections = {}
        lines = document.split('\n')
        current_section = None
        current_title = ""
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for main section headers like "**1. DEFINITIONS**" or "1. DEFINITIONS"
            main_section_match = re.match(r'^\*\*(\d+)\.\s+([A-Z][A-Z\s\-\/]+)\*\*$', line) or \
                               re.match(r'^(\d+)\.\s+([A-Z][A-Z\s\-\/]+)$', line)
            if main_section_match:
                # Save previous section if exists
                if current_section:
                    sections[current_section] = (current_title, '\n'.join(current_content).strip())
                
                # Start new main section
                current_section = main_section_match.group(1)
                current_title = main_section_match.group(2).strip()
                current_content = []
                continue
            
            # Check for subsection headers like "1.1 **Grant of License**:" or "1.1 \"Software\" means..."
            subsection_match = re.match(r'^(\d+\.\d+(?:\.\d+)*)\s+(.+)$', line)
            if subsection_match and current_section:
                # Save previous subsection if exists
                if current_section and '.' not in current_section:
                    # We're in a main section, save it before starting subsection
                    sections[current_section] = (current_title, '\n'.join(current_content).strip())
                elif current_section:
                    # Save previous subsection
                    sections[current_section] = (current_title, '\n'.join(current_content).strip())
                
                # Start new subsection
                current_section = subsection_match.group(1)
                subsection_content = subsection_match.group(2).strip()
                
                # Extract title from subsection content (look for quoted terms or bold text)
                title_match = re.match(r'[\*"]*([^"*:]+)[\*"]*[:]*\s*(.*)', subsection_content)
                if title_match:
                    current_title = title_match.group(1).strip()
                    remaining_content = title_match.group(2).strip()
                    current_content = [remaining_content] if remaining_content else []
                else:
                    current_title = subsection_content[:50] + "..." if len(subsection_content) > 50 else subsection_content
                    current_content = []
                continue
            
            # Add to current section content if we have one
            if current_section:
                current_content.append(line)
        
        # Don't forget the last section
        if current_section:
            sections[current_section] = (current_title, '\n'.join(current_content).strip())
        
        return sections
    
    def align_sections(self, doc_sections: Dict[str, Tuple[str, str]], 
                      template_sections: Dict[str, Tuple[str, str]]) -> List[SectionMapping]:
        """Use ChatGPT to align sections between documents"""
        
        # Prepare section summaries for the LLM
        doc_summary = []
        for sec_num, (title, content) in doc_sections.items():
            preview = content[:200] + "..." if len(content) > 200 else content
            doc_summary.append(f"Section {sec_num}: {title}\nPreview: {preview}")
        
        template_summary = []
        for sec_num, (title, content) in template_sections.items():
            preview = content[:200] + "..." if len(content) > 200 else content
            template_summary.append(f"Section {sec_num}: {title}\nPreview: {preview}")
        
        prompt = f"""You are analyzing two legal documents to create section alignments. 
        Based on the content and titles, create a mapping table between sections that cover similar topics.
        
        Document sections:
        {chr(10).join(doc_summary)}
        
        Template sections:
        {chr(10).join(template_summary)}
        
        Create a JSON array where each object has:
        - "doc_section": section number from document
        - "template_section": section number from template  
        - "doc_title": section title from document
        - "template_title": section title from template
        - "confidence": "high", "medium", or "low" based on how well they match
        
        Only include mappings where there's a reasonable semantic similarity.
        Some sections may not have matches - that's okay, don't force mappings.
        
        Return only the JSON array, no other text."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.3
            )
            
            # Parse JSON response
            json_str = response.choices[0].message.content.strip()
            print(f"   Raw LLM response: {json_str[:200]}...")
            
            # Try to extract JSON from the response (sometimes LLM adds extra text)
            if "```json" in json_str:
                json_start = json_str.find("```json") + 7
                json_end = json_str.find("```", json_start)
                if json_end == -1:
                    json_str = json_str[json_start:].strip()
                else:
                    json_str = json_str[json_start:json_end].strip()
            elif json_str.startswith("```") and json_str.endswith("```"):
                json_str = json_str[3:-3].strip()
            elif not json_str.startswith('['):
                # Try to find the first [ and last ]
                start_idx = json_str.find('[')
                end_idx = json_str.rfind(']')
                if start_idx != -1 and end_idx != -1:
                    json_str = json_str[start_idx:end_idx+1]
                elif start_idx != -1:
                    # Try to recover partial JSON by finding complete objects
                    partial_json = json_str[start_idx:]
                    json_str = self._try_recover_partial_json(partial_json)
            
            # Try to parse JSON
            try:
                mappings_data = json.loads(json_str)
            except json.JSONDecodeError:
                # Try to recover partial JSON
                recovered_json = self._try_recover_partial_json(json_str)
                if recovered_json:
                    mappings_data = json.loads(recovered_json)
                else:
                    raise
            
            # Convert to SectionMapping objects
            mappings = []
            for mapping in mappings_data:
                mappings.append(SectionMapping(
                    doc_section=mapping["doc_section"],
                    template_section=mapping["template_section"],
                    doc_title=mapping["doc_title"],
                    template_title=mapping["template_title"],
                    confidence=mapping["confidence"]
                ))
            
            return mappings
        except Exception as e:
            print(f"Error aligning sections: {e}")
            print(f"Raw response was: {response.choices[0].message.content if 'response' in locals() else 'No response'}")
            return []
    
    def _try_recover_partial_json(self, partial_json: str) -> str:
        """Try to recover a valid JSON array from partial/cut-off JSON"""
        try:
            # Find the last complete object in the array
            if not partial_json.startswith('['):
                return ""
            
            # Count brackets and find last complete object
            bracket_count = 0
            brace_count = 0
            last_complete_idx = -1
            
            for i, char in enumerate(partial_json):
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                elif char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    # If we just closed a complete object and we're in the main array
                    if brace_count == 0 and bracket_count == 1:
                        last_complete_idx = i
            
            if last_complete_idx != -1:
                # Extract up to the last complete object and close the array
                recovered = partial_json[:last_complete_idx + 1] + ']'
                # Validate it's proper JSON
                json.loads(recovered)
                return recovered
        except:
            pass
        
        return ""
    
    def compare_section_content(self, doc_content: str, template_content: str, 
                              doc_title: str, template_title: str) -> ContentDifference:
        """Compare content between aligned sections"""
        
        prompt = f"""Compare these two legal document sections and identify the differences:

        Document Section: {doc_title}
        {doc_content}
        
        Template Section: {template_title}
        {template_content}
        
        Analyze the content and return a JSON object with:
        - "in_doc_not_template": array of strings describing what's in the document section but not in the template section
        - "in_template_not_doc": array of strings describing what's in the template section but not in the document section
        
        Focus on:
        - Different clauses or provisions
        - Different terms or definitions
        - Different requirements or obligations
        - Different procedures or processes
        
        Be specific and detailed. Return only the JSON object, no other text."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.3
            )
            
            json_str = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
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
            
            diff_data = json.loads(json_str)
            
            return ContentDifference(
                in_doc_not_template=diff_data.get("in_doc_not_template", []),
                in_template_not_doc=diff_data.get("in_template_not_doc", [])
            )
        except Exception as e:
            print(f"Error comparing content: {e}")
            print(f"Raw response was: {response.choices[0].message.content if 'response' in locals() else 'No response'}")
            return ContentDifference([], [])
    
    def run_full_alignment(self, pair_id: int = 0, verbose: bool = True) -> Optional[AlignmentResult]:
        """Run the complete document alignment pipeline and return results"""
        start_time = time.time()
        
        if verbose:
            print("🚀 Starting Legal Document Alignment Pipeline\n")
        
        # Step 1: Generate test data
        if verbose:
            print("📄 Generating original legal document...")
        original_doc = self.generate_legal_document()
        if not original_doc:
            if verbose:
                print("❌ Failed to generate original document")
            return None
        
        if verbose:
            print("📄 Creating document variant...")
        variant_doc = self.create_document_variant(original_doc)
        if not variant_doc:
            if verbose:
                print("❌ Failed to create document variant")
            return None
        
        # Save documents for reference (only for pair 0 or if verbose)
        if pair_id == 0 or verbose:
            with open(f'/Users/songhewang/Desktop/doc_alignment/original_doc_{pair_id}.txt', 'w') as f:
                f.write(original_doc)
            with open(f'/Users/songhewang/Desktop/doc_alignment/variant_doc_{pair_id}.txt', 'w') as f:
                f.write(variant_doc)
        
        if verbose:
            print(f"✅ Generated document pair {pair_id}\n")
        
        # Step 2: Extract sections
        if verbose:
            print("🔍 Extracting sections from documents...")
        doc_sections = self.extract_sections(variant_doc)  # This is our "doc"
        template_sections = self.extract_sections(original_doc)  # This is our "template"
        
        if verbose:
            print(f"   Document sections: {len(doc_sections)}")
            print(f"   Template sections: {len(template_sections)}\n")
        
        # Step 3: Align sections
        if verbose:
            print("🔗 Aligning sections using AI...")
        section_mappings = self.align_sections(doc_sections, template_sections)
        if verbose:
            print(f"✅ Found {len(section_mappings)} section alignments\n")
        
        # Step 4: Compare content for each alignment
        content_differences = []
        for mapping in section_mappings:
            # Get section content
            doc_content = doc_sections[mapping.doc_section][1]
            template_content = template_sections[mapping.template_section][1]
            
            # Compare content
            differences = self.compare_section_content(
                doc_content, template_content,
                mapping.doc_title, mapping.template_title
            )
            content_differences.append((mapping.doc_section, mapping.template_section, differences))
        
        processing_time = time.time() - start_time
        
        # Display results if verbose
        if verbose:
            self._display_alignment_results(section_mappings, content_differences, doc_sections, template_sections)
        
        return AlignmentResult(
            pair_id=pair_id,
            doc_sections_count=len(doc_sections),
            template_sections_count=len(template_sections),
            alignments_found=len(section_mappings),
            section_mappings=section_mappings,
            content_differences=content_differences,
            processing_time=processing_time
        )
    
    def _display_alignment_results(self, section_mappings, content_differences, doc_sections, template_sections):
        """Display alignment results in a formatted way"""
        # Display alignment table
        print("📊 SECTION ALIGNMENT TABLE")
        print("=" * 80)
        print(f"{'Doc Section':<12} {'Template Section':<16} {'Doc Title':<25} {'Template Title':<25}")
        print("-" * 80)
        for mapping in section_mappings:
            print(f"{mapping.doc_section:<12} {mapping.template_section:<16} "
                  f"{mapping.doc_title[:24]:<25} {mapping.template_title[:24]:<25}")
        print()
        
        # Display content comparison results
        print("📋 CONTENT COMPARISON RESULTS")
        print("=" * 80)
        
        for i, (mapping, (doc_section, template_section, differences)) in enumerate(zip(section_mappings, content_differences), 1):
            print(f"\n{i}. Comparing sections {mapping.doc_section} ↔ {mapping.template_section}")
            print(f"   Doc: {mapping.doc_title}")
            print(f"   Template: {mapping.template_title}")
            print(f"   Confidence: {mapping.confidence}")
            
            print("\n   📝 In Document but NOT in Template:")
            for diff in differences.in_doc_not_template:
                print(f"      • {diff}")
            
            print("\n   📝 In Template but NOT in Document:")
            for diff in differences.in_template_not_doc:
                print(f"      • {diff}")
            print()
        
        print("✅ Legal document alignment complete!")
    
    def evaluate_alignment_quality(self, result: AlignmentResult) -> EvaluationScore:
        """Use LLM to evaluate the quality of alignment results"""
        
        # Prepare summary for evaluation
        summary = f"""
        ALIGNMENT RESULTS SUMMARY:
        - Pair ID: {result.pair_id}
        - Document sections: {result.doc_sections_count}
        - Template sections: {result.template_sections_count}
        - Alignments found: {result.alignments_found}
        - Processing time: {result.processing_time:.2f}s
        
        SECTION MAPPINGS:
        """
        
        for mapping in result.section_mappings:
            summary += f"- {mapping.doc_section} ({mapping.doc_title}) ↔ {mapping.template_section} ({mapping.template_title}) [confidence: {mapping.confidence}]\n"
        
        summary += f"\nCONTENT DIFFERENCES SAMPLE:\n"
        
        # Include first 3 content comparisons as examples
        for i, (doc_section, template_section, diff) in enumerate(result.content_differences[:3]):
            summary += f"- Section {doc_section} ↔ {template_section}:\n"
            summary += f"  • In doc not template: {len(diff.in_doc_not_template)} items\n"
            summary += f"  • In template not doc: {len(diff.in_template_not_doc)} items\n"
        
        evaluation_prompt = f"""
        You are evaluating the quality of a legal document alignment system. Based on the results below, provide scores on a 0-10 scale for:
        
        1. Section Alignment Accuracy: How well did the system match corresponding sections?
        2. Content Comparison Quality: How detailed and accurate are the content differences identified?
        3. Overall Completeness: How comprehensive is the alignment coverage?
        
        {summary}
        
        Provide your evaluation as a JSON object with:
        - "section_alignment_accuracy": float (0-10)
        - "content_comparison_quality": float (0-10) 
        - "overall_completeness": float (0-10)
        - "comments": string with detailed feedback
        
        Consider factors like:
        - Reasonable section matching (similar topics should align)
        - High/medium/low confidence distribution
        - Coverage ratio (alignments found vs total sections)
        - Quality of content difference detection
        
        Return only the JSON object, no other text.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": evaluation_prompt}],
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
            
            eval_data = json.loads(json_str)
            
            overall_score = (eval_data["section_alignment_accuracy"] + 
                           eval_data["content_comparison_quality"] + 
                           eval_data["overall_completeness"]) / 3
            
            return EvaluationScore(
                pair_id=result.pair_id,
                section_alignment_accuracy=eval_data["section_alignment_accuracy"],
                content_comparison_quality=eval_data["content_comparison_quality"],
                overall_completeness=eval_data["overall_completeness"],
                comments=eval_data["comments"],
                overall_score=overall_score
            )
            
        except Exception as e:
            print(f"Error evaluating alignment quality for pair {result.pair_id}: {e}")
            return EvaluationScore(
                pair_id=result.pair_id,
                section_alignment_accuracy=5.0,
                content_comparison_quality=5.0,
                overall_completeness=5.0,
                comments=f"Evaluation failed: {str(e)}",
                overall_score=5.0
            )
    
    def run_batch_evaluation(self, num_pairs: int = 10) -> List[EvaluationScore]:
        """Run alignment on multiple document pairs and evaluate each"""
        print(f"🚀 Starting Batch Evaluation with {num_pairs} document pairs\n")
        
        results = []
        evaluation_scores = []
        
        for i in range(num_pairs):
            print(f"📄 Processing document pair {i+1}/{num_pairs}...")
            
            try:
                # Run alignment (non-verbose for batch processing)
                result = self.run_full_alignment(pair_id=i+1, verbose=False)
                if result is None:
                    print(f"❌ Failed to process pair {i+1}")
                    continue
                
                results.append(result)
                print(f"   ✅ Alignment complete: {result.alignments_found} mappings found in {result.processing_time:.2f}s")
                
                # Evaluate the result
                print(f"   📊 Evaluating alignment quality...")
                score = self.evaluate_alignment_quality(result)
                evaluation_scores.append(score)
                print(f"   ⭐ Overall score: {score.overall_score:.1f}/10")
                
            except Exception as e:
                print(f"❌ Error processing pair {i+1}: {e}")
                continue
        
        print(f"\n✅ Batch evaluation complete! Processed {len(evaluation_scores)} pairs successfully.")
        
        # Generate comprehensive report
        if evaluation_scores:
            self._generate_evaluation_report(results, evaluation_scores)
        
        return evaluation_scores
    
    def _generate_evaluation_report(self, results: List[AlignmentResult], scores: List[EvaluationScore]):
        """Generate a comprehensive evaluation report"""
        print("\n" + "="*100)
        print("📊 COMPREHENSIVE EVALUATION REPORT")
        print("="*100)
        
        # Basic Statistics
        print("\n📈 PERFORMANCE STATISTICS")
        print("-" * 60)
        
        section_accuracies = [s.section_alignment_accuracy for s in scores]
        content_qualities = [s.content_comparison_quality for s in scores]
        completeness_scores = [s.overall_completeness for s in scores]
        overall_scores = [s.overall_score for s in scores]
        processing_times = [r.processing_time for r in results]
        
        print(f"Average Section Alignment Accuracy: {statistics.mean(section_accuracies):.2f}/10 (σ={statistics.stdev(section_accuracies):.2f})")
        print(f"Average Content Comparison Quality: {statistics.mean(content_qualities):.2f}/10 (σ={statistics.stdev(content_qualities):.2f})")
        print(f"Average Overall Completeness:      {statistics.mean(completeness_scores):.2f}/10 (σ={statistics.stdev(completeness_scores):.2f})")
        print(f"Average Overall Score:             {statistics.mean(overall_scores):.2f}/10 (σ={statistics.stdev(overall_scores):.2f})")
        print(f"Average Processing Time:           {statistics.mean(processing_times):.2f}s (σ={statistics.stdev(processing_times):.2f}s)")
        
        # Alignment Coverage Statistics
        print(f"\n📋 ALIGNMENT COVERAGE STATISTICS")
        print("-" * 60)
        
        doc_sections = [r.doc_sections_count for r in results]
        template_sections = [r.template_sections_count for r in results]
        alignments_found = [r.alignments_found for r in results]
        coverage_ratios = [a/max(d,t,1) for r, a, d, t in zip(results, alignments_found, doc_sections, template_sections)]
        
        print(f"Average Document Sections:    {statistics.mean(doc_sections):.1f}")
        print(f"Average Template Sections:    {statistics.mean(template_sections):.1f}")
        print(f"Average Alignments Found:     {statistics.mean(alignments_found):.1f}")
        print(f"Average Coverage Ratio:       {statistics.mean(coverage_ratios):.2%}")
        
        # Performance Distribution
        print(f"\n⭐ SCORE DISTRIBUTION")
        print("-" * 60)
        
        score_ranges = [
            (9.0, 10.0, "Excellent"),
            (8.0, 8.9, "Very Good"),
            (7.0, 7.9, "Good"),
            (6.0, 6.9, "Fair"),
            (0.0, 5.9, "Needs Improvement")
        ]
        
        for min_score, max_score, label in score_ranges:
            count = len([s for s in overall_scores if min_score <= s <= max_score])
            percentage = (count / len(overall_scores)) * 100
            print(f"{label:17} ({min_score:.1f}-{max_score:.1f}): {count:2d} pairs ({percentage:5.1f}%)")
        
        # Detailed Results Table
        print(f"\n📋 DETAILED RESULTS")
        print("-" * 120)
        print(f"{'Pair':<4} {'Sections':<12} {'Aligned':<8} {'Time':<8} {'Accuracy':<9} {'Quality':<9} {'Complete':<9} {'Overall':<8}")
        print("-" * 120)
        
        for result, score in zip(results, scores):
            coverage_ratio = result.alignments_found / max(result.doc_sections_count, result.template_sections_count, 1)
            print(f"{result.pair_id:<4} {result.doc_sections_count:>3}/{result.template_sections_count:<3} ({coverage_ratio:.0%}) "
                  f"{result.alignments_found:<8} {result.processing_time:<8.1f} "
                  f"{score.section_alignment_accuracy:<9.1f} {score.content_comparison_quality:<9.1f} "
                  f"{score.overall_completeness:<9.1f} {score.overall_score:<8.1f}")
        
        # Representative Comments
        print(f"\n💬 REPRESENTATIVE EVALUATION COMMENTS")
        print("-" * 80)
        
        # Show comments from best, average, and worst performing pairs
        sorted_scores = sorted(scores, key=lambda x: x.overall_score, reverse=True)
        
        if len(sorted_scores) >= 3:
            print(f"\n🥇 Best Performance (Pair {sorted_scores[0].pair_id}, Score: {sorted_scores[0].overall_score:.1f}):")
            print(f"   {sorted_scores[0].comments}")
            
            mid_idx = len(sorted_scores) // 2
            print(f"\n📊 Average Performance (Pair {sorted_scores[mid_idx].pair_id}, Score: {sorted_scores[mid_idx].overall_score:.1f}):")
            print(f"   {sorted_scores[mid_idx].comments}")
            
            print(f"\n📉 Lowest Performance (Pair {sorted_scores[-1].pair_id}, Score: {sorted_scores[-1].overall_score:.1f}):")
            print(f"   {sorted_scores[-1].comments}")
        
        # Recommendations
        print(f"\n🎯 RECOMMENDATIONS")
        print("-" * 60)
        
        avg_score = statistics.mean(overall_scores)
        avg_accuracy = statistics.mean(section_accuracies)
        avg_quality = statistics.mean(content_qualities)
        avg_completeness = statistics.mean(completeness_scores)
        
        if avg_accuracy < 7.0:
            print("• Consider improving section alignment logic - accuracy below 7.0")
        if avg_quality < 7.0:
            print("• Enhance content comparison prompts - quality below 7.0")
        if avg_completeness < 7.0:
            print("• Work on coverage - completeness below 7.0")
        if avg_score >= 8.0:
            print("• System performing well overall! Consider fine-tuning for edge cases.")
        elif avg_score >= 6.0:
            print("• System shows good potential. Focus on top improvement areas above.")
        else:
            print("• System needs significant improvements across all metrics.")
            
        print(f"\n🎉 Evaluation complete! System overall score: {avg_score:.2f}/10")

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")
    
    aligner = LegalDocumentAligner(api_key)
    
    # Choose between single alignment or batch evaluation
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "evaluate":
        # Run batch evaluation
        num_pairs = int(sys.argv[2]) if len(sys.argv) > 2 else 8
        aligner.run_batch_evaluation(num_pairs)
    else:
        # Run single alignment (original behavior)
        aligner.run_full_alignment()

if __name__ == "__main__":
    main()
