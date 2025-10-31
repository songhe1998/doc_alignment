// Main JavaScript for Enhanced Legal Document Alignment Tool

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('alignmentForm');
    const doc1Input = document.getElementById('doc1');
    const doc2Input = document.getElementById('doc2');
    const file1Name = document.getElementById('file1Name');
    const file2Name = document.getElementById('file2Name');
    const submitBtn = document.getElementById('submitBtn');
    const resultsSection = document.getElementById('resultsSection');
    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');

    // Update file names when files are selected
    doc1Input.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            file1Name.textContent = e.target.files[0].name;
            file1Name.style.color = '#28a745';
        } else {
            file1Name.textContent = 'No file selected';
            file1Name.style.color = '#666';
        }
    });

    doc2Input.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            file2Name.textContent = e.target.files[0].name;
            file2Name.style.color = '#28a745';
        } else {
            file2Name.textContent = 'No file selected';
            file2Name.style.color = '#666';
        }
    });

    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Hide previous results/errors
        resultsSection.style.display = 'none';
        errorSection.style.display = 'none';
        
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.querySelector('.btn-text').style.display = 'none';
        submitBtn.querySelector('.btn-loader').style.display = 'inline';
        
        const formData = new FormData(form);
        
        try {
            const response = await fetch('/align', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                displayResults(data);
                resultsSection.style.display = 'block';
                resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
                displayError(data.error || 'An error occurred');
            }
        } catch (error) {
            displayError('Failed to connect to server: ' + error.message);
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            submitBtn.querySelector('.btn-text').style.display = 'inline';
            submitBtn.querySelector('.btn-loader').style.display = 'none';
        }
    });

    function displayError(message) {
        errorMessage.textContent = message;
        errorSection.style.display = 'block';
        errorSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function displayResults(data) {
        console.log('Displaying results:', data);
        
        // Set document names
        document.getElementById('doc1Name').textContent = data.doc1_name || 'Document 1';
        document.getElementById('doc2Name').textContent = data.doc2_name || 'Document 2';
        
        // Create legend
        createLegend(data.alignments);
        
        // Display documents with color-coded highlights
        displayColorCodedDocuments(data);
        
        // Display detailed alignments
        displayDetailedAlignments(data);
    }

    function createLegend(alignments) {
        const legend = document.getElementById('legend');
        let html = '<h4>🎨 Alignment Legend (Click to highlight)</h4>';
        
        alignments.forEach((alignment, index) => {
            const topic = alignment.topic_name || alignment.topic || `Alignment ${index + 1}`;
            const color = alignment.color || '#ddd';
            
            html += `
                <div class="legend-item" data-alignment-id="${alignment.id || index}" onclick="highlightAlignment(${alignment.id || index})">
                    <div class="legend-color" style="background-color: ${color};"></div>
                    <div class="legend-text">${topic}</div>
                </div>
            `;
        });
        
        legend.innerHTML = html;
    }

    function displayColorCodedDocuments(data) {
        const doc1Content = document.getElementById('doc1Content');
        const doc2Content = document.getElementById('doc2Content');
        
        console.log('📄 Displaying documents...');
        console.log('Doc1 text length:', data.doc1_text ? data.doc1_text.length : 0);
        console.log('Doc2 text length:', data.doc2_text ? data.doc2_text.length : 0);
        console.log('Method:', data.method);
        console.log('Alignments:', data.alignments ? data.alignments.length : 0);
        
        // For section-based alignment
        if (data.method.includes('Section-Based')) {
            console.log('Using section-based display');
            displaySectionBasedDocuments(doc1Content, doc2Content, data);
        } else {
            console.log('Using topic-based display');
            // For topic-based alignment
            displayTopicBasedDocuments(doc1Content, doc2Content, data);
        }
        
        console.log('✅ Documents displayed');
    }

    function displaySectionBasedDocuments(doc1Content, doc2Content, data) {
        console.log('🔧 displaySectionBasedDocuments called');
        // Show full documents with highlighting
        let doc1Text = data.doc1_text || '';
        let doc2Text = data.doc2_text || '';
        
        console.log('Raw doc1 length:', doc1Text.length);
        console.log('Raw doc2 length:', doc2Text.length);
        console.log('Doc1 preview:', doc1Text.substring(0, 200));
        
        // Convert to HTML-safe
        doc1Text = doc1Text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
        doc2Text = doc2Text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
        
        console.log('After HTML-safe doc1 length:', doc1Text.length);
        
        // Create arrays to hold highlighted ranges
        let doc1Highlights = [];
        let doc2Highlights = [];
        
        // For each alignment, find and mark the sections
        data.alignments.forEach((alignment, index) => {
            const color = alignment.color || '#ddd';
            const id = alignment.id || index;
            const topicName = alignment.topic || `Alignment ${index + 1}`;
            
            // Find doc1 section
            const doc1Section = alignment.doc1_section || '';
            const doc1Title = alignment.doc1_title || '';
            
            if (doc1Section || doc1Title) {
                // Try to find the section in the text
                let searchText = doc1Section + (doc1Title ? ' ' + doc1Title : '');
                searchText = searchText.substring(0, 150).trim();
                
                if (searchText) {
                    // Find all occurrences (there should usually be just one)
                    let pos = doc1Text.toLowerCase().indexOf(searchText.toLowerCase());
                    
                    if (pos !== -1) {
                        // Try to capture the whole section (up to next section or a reasonable length)
                        let endPos = pos + searchText.length;
                        
                        // Try to find where the section ends (next numbered section or end)
                        let nextSectionMatch = doc1Text.substring(endPos).match(/\n\s*\d+\./);
                        if (nextSectionMatch) {
                            endPos = endPos + nextSectionMatch.index;
                        } else {
                            // Take next ~500 characters
                            endPos = Math.min(endPos + 500, doc1Text.length);
                        }
                        
                        doc1Highlights.push({
                            start: pos,
                            end: endPos,
                            color: color,
                            id: id,
                            name: topicName
                        });
                    }
                }
            }
            
            // Find doc2 section
            const doc2Section = alignment.doc2_section || '';
            const doc2Title = alignment.doc2_title || '';
            
            if (doc2Section || doc2Title) {
                let searchText = doc2Section + (doc2Title ? ' ' + doc2Title : '');
                searchText = searchText.substring(0, 150).trim();
                
                if (searchText) {
                    let pos = doc2Text.toLowerCase().indexOf(searchText.toLowerCase());
                    
                    if (pos !== -1) {
                        let endPos = pos + searchText.length;
                        
                        let nextSectionMatch = doc2Text.substring(endPos).match(/\n\s*\d+\./);
                        if (nextSectionMatch) {
                            endPos = endPos + nextSectionMatch.index;
                        } else {
                            endPos = Math.min(endPos + 500, doc2Text.length);
                        }
                        
                        doc2Highlights.push({
                            start: pos,
                            end: endPos,
                            color: color,
                            id: id,
                            name: topicName
                        });
                    }
                }
            }
        });
        
        // Apply highlights
        const doc1Html = applyHighlights(doc1Text, doc1Highlights);
        const doc2Html = applyHighlights(doc2Text, doc2Highlights);
        
        console.log('Doc1 highlights found:', doc1Highlights.length);
        console.log('Doc2 highlights found:', doc2Highlights.length);
        console.log('Doc1 HTML length:', doc1Html.length);
        console.log('Doc2 HTML length:', doc2Html.length);
        console.log('Doc1 HTML preview:', doc1Html.substring(0, 300));
        
        doc1Content.innerHTML = doc1Html;
        doc2Content.innerHTML = doc2Html;
        
        console.log('✅ Section-based documents rendered');
        
        // Add click handlers to highlights
        addHighlightClickHandlers();
    }

    function displayTopicBasedDocuments(doc1Content, doc2Content, data) {
        console.log('🔧 displayTopicBasedDocuments called');
        // Show full documents with overlaid highlighting annotations
        let doc1Text = data.doc1_text || '';
        let doc2Text = data.doc2_text || '';
        
        console.log('Topic-based doc1 length:', doc1Text.length);
        console.log('Topic-based doc2 length:', doc2Text.length);
        
        // Convert text to HTML-safe format
        doc1Text = doc1Text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
        doc2Text = doc2Text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
        
        // Create arrays to hold highlighted ranges
        let doc1Highlights = [];
        let doc2Highlights = [];
        
        // For each alignment, try to find and mark sections in the text
        data.alignments.forEach((alignment, index) => {
            const color = alignment.color || '#ddd';
            const id = alignment.id || index;
            const topicName = alignment.topic_name || alignment.topic || `Topic ${index + 1}`;
            
            // Try to find sections in doc1
            if (alignment.doc1_sections && alignment.doc1_sections.length > 0) {
                alignment.doc1_sections.forEach(section => {
                    // Extract section number/title and search for it
                    const searchText = section.substring(0, 100); // First 100 chars
                    const pos = doc1Text.toLowerCase().indexOf(searchText.toLowerCase());
                    if (pos !== -1) {
                        doc1Highlights.push({
                            start: pos,
                            end: pos + searchText.length,
                            color: color,
                            id: id,
                            name: topicName
                        });
                    }
                });
            }
            
            // Try to find sections in doc2
            if (alignment.doc2_sections && alignment.doc2_sections.length > 0) {
                alignment.doc2_sections.forEach(section => {
                    const searchText = section.substring(0, 100);
                    const pos = doc2Text.toLowerCase().indexOf(searchText.toLowerCase());
                    if (pos !== -1) {
                        doc2Highlights.push({
                            start: pos,
                            end: pos + searchText.length,
                            color: color,
                            id: id,
                            name: topicName
                        });
                    }
                });
            }
        });
        
        // Apply highlights to doc1
        const doc1Html = applyHighlights(doc1Text, doc1Highlights);
        const doc2Html = applyHighlights(doc2Text, doc2Highlights);
        
        console.log('Topic doc1 highlights:', doc1Highlights.length);
        console.log('Topic doc2 highlights:', doc2Highlights.length);
        console.log('Topic doc1 HTML length:', doc1Html.length);
        console.log('Topic doc1 HTML preview:', doc1Html.substring(0, 300));
        
        doc1Content.innerHTML = doc1Html;
        doc2Content.innerHTML = doc2Html;
        
        console.log('✅ Topic-based documents rendered');
        
        // Add click handlers
        addHighlightClickHandlers();
    }
    
    function applyHighlights(text, highlights) {
        if (highlights.length === 0) {
            return text;
        }
        
        // Sort highlights by start position
        highlights.sort((a, b) => a.start - b.start);
        
        // Build HTML with highlights
        let html = '';
        let lastPos = 0;
        
        highlights.forEach(highlight => {
            // Add text before highlight
            if (highlight.start > lastPos) {
                html += text.substring(lastPos, highlight.start);
            }
            
            // Add highlighted text
            const highlightedText = text.substring(highlight.start, highlight.end);
            html += `<span class="highlight" data-alignment-id="${highlight.id}" style="background-color: ${highlight.color};" title="${highlight.name}">${highlightedText}</span>`;
            
            lastPos = highlight.end;
        });
        
        // Add remaining text
        if (lastPos < text.length) {
            html += text.substring(lastPos);
        }
        
        return html;
    }

    function displayDetailedAlignments(data) {
        const alignmentDetails = document.getElementById('alignmentDetails');
        let html = '<h3>📋 Detailed Alignment Information</h3>';
        
        data.alignments.forEach((alignment, index) => {
            const color = alignment.color || '#ddd';
            const id = alignment.id || index;
            const topic = alignment.topic_name || alignment.topic || `Alignment ${index + 1}`;
            
            html += `
                <div class="alignment-card" data-alignment-id="${id}" onclick="highlightAlignment(${id})">
                    <div class="alignment-header">
                        <div class="alignment-color-indicator" style="background-color: ${color};"></div>
                        <div class="alignment-title">
                            <h4>${topic}</h4>
                            ${alignment.topic_description ? '<p>' + alignment.topic_description + '</p>' : ''}
                        </div>
                    </div>
                    
                    <div class="alignment-body">
                        <div class="alignment-doc-side">
                            <h5>📄 Document 1</h5>
            `;
            
            // Document 1 content
            if (alignment.doc1_sections && alignment.doc1_sections.length > 0) {
                html += '<ul>';
                alignment.doc1_sections.forEach(section => {
                    html += `<li>${section}</li>`;
                });
                html += '</ul>';
                if (alignment.doc1_summary || alignment.doc1_content_summary) {
                    html += `<p><strong>Summary:</strong> ${alignment.doc1_summary || alignment.doc1_content_summary}</p>`;
                }
            } else if (alignment.doc1_title) {
                html += `<p>${alignment.doc1_section}: ${alignment.doc1_title}</p>`;
            } else {
                html += '<p style="color: #999; font-style: italic;">Not present</p>';
            }
            
            html += `
                        </div>
                        <div class="alignment-doc-side">
                            <h5>📄 Document 2</h5>
            `;
            
            // Document 2 content
            if (alignment.doc2_sections && alignment.doc2_sections.length > 0) {
                html += '<ul>';
                alignment.doc2_sections.forEach(section => {
                    html += `<li>${section}</li>`;
                });
                html += '</ul>';
                if (alignment.doc2_summary || alignment.doc2_content_summary) {
                    html += `<p><strong>Summary:</strong> ${alignment.doc2_summary || alignment.doc2_content_summary}</p>`;
                }
            } else if (alignment.doc2_title) {
                html += `<p>${alignment.doc2_section}: ${alignment.doc2_title}</p>`;
            } else {
                html += '<p style="color: #999; font-style: italic;">Not present</p>';
            }
            
            html += '</div></div>';
            
            // Differences
            if (alignment.differences) {
                html += `
                    <div class="differences-section">
                        <h5>🔍 Key Differences:</h5>
                        <p>${alignment.differences}</p>
                    </div>
                `;
            }
            
            html += '</div>';
        });
        
        alignmentDetails.innerHTML = html;
    }

    function addHighlightClickHandlers() {
        const highlights = document.querySelectorAll('.highlight');
        highlights.forEach(highlight => {
            highlight.addEventListener('click', function() {
                const alignmentId = this.getAttribute('data-alignment-id');
                highlightAlignment(parseInt(alignmentId));
            });
        });
    }

    // Make highlightAlignment global
    window.highlightAlignment = function(alignmentId) {
        console.log('Highlighting alignment:', alignmentId);
        
        // Remove active class from all elements
        document.querySelectorAll('.highlight.active, .alignment-card.active, .legend-item.active').forEach(el => {
            el.classList.remove('active');
        });
        
        // Add active class to selected elements
        document.querySelectorAll(`[data-alignment-id="${alignmentId}"]`).forEach(el => {
            el.classList.add('active');
            
            // Scroll into view if not visible
            if (!isElementInViewport(el)) {
                el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
    };

    function isElementInViewport(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }

    function escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
});

