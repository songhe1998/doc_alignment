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
        const doc1Text = data.doc1_text || '';
        const doc2Text = data.doc2_text || '';
        const doc1Lookup = buildSectionLookup(data.doc1_sections || []);
        const doc2Lookup = buildSectionLookup(data.doc2_sections || []);
        
        console.log('Doc1 text length:', doc1Text.length);
        
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
                const lookupLabel = `${doc1Section || ''} ${doc1Title || ''}`.trim();
                const matchedSection = findSectionMatch(lookupLabel, doc1Lookup);
                if (matchedSection && matchedSection.start_char !== undefined && matchedSection.end_char) {
                    doc1Highlights.push({
                        start: matchedSection.start_char,
                        end: matchedSection.end_char,
                        color,
                        id,
                        name: topicName
                    });
                } else {
                    const fallback = lookupLabel.substring(0, 150).trim();
                    addFallbackHighlight(fallback, doc1Text, doc1Highlights, color, id, topicName);
                }
            }
            
            // Find doc2 section
            const doc2Section = alignment.doc2_section || '';
            const doc2Title = alignment.doc2_title || '';
            
            if (doc2Section || doc2Title) {
                const lookupLabel = `${doc2Section || ''} ${doc2Title || ''}`.trim();
                const matchedSection = findSectionMatch(lookupLabel, doc2Lookup);
                if (matchedSection && matchedSection.start_char !== undefined && matchedSection.end_char) {
                    doc2Highlights.push({
                        start: matchedSection.start_char,
                        end: matchedSection.end_char,
                        color,
                        id,
                        name: topicName
                    });
                } else {
                    const fallback = lookupLabel.substring(0, 150).trim();
                    addFallbackHighlight(fallback, doc2Text, doc2Highlights, color, id, topicName);
                }
            }
        });
        
        // Apply highlights
        renderDocumentWithHighlights(doc1Text, doc1Highlights, doc1Content);
        renderDocumentWithHighlights(doc2Text, doc2Highlights, doc2Content);
        
        console.log('Doc1 highlights found:', doc1Highlights.length);
        console.log('Doc2 highlights found:', doc2Highlights.length);
        console.log('Doc1 HTML preview:', doc1Text.substring(0, 300));
        
        console.log('✅ Section-based documents rendered');
        
        // Add click handlers to highlights
        addHighlightClickHandlers();
    }

    function displayTopicBasedDocuments(doc1Content, doc2Content, data) {
        console.log('🔧 displayTopicBasedDocuments called');
        // Show full documents with overlaid highlighting annotations
        const doc1Text = data.doc1_text || '';
        const doc2Text = data.doc2_text || '';
        const doc1Lookup = buildSectionLookup(data.doc1_sections || []);
        const doc2Lookup = buildSectionLookup(data.doc2_sections || []);
        
        // Create arrays to hold highlighted ranges
        let doc1Highlights = [];
        let doc2Highlights = [];
        
        // Determine if this is topic_direct method (sections are key_points, not section IDs)
        const isDirectMethod = data.method && data.method.includes('Direct');
        console.log('Is Direct Method:', isDirectMethod);
        
        // For each alignment, try to find and mark sections in the text
        data.alignments.forEach((alignment, index) => {
            const color = alignment.color || '#ddd';
            const id = alignment.id || index;
            const topicName = alignment.topic_name || alignment.topic || `Topic ${index + 1}`;
            
            // Try to find sections in doc1
            if (alignment.doc1_sections && alignment.doc1_sections.length > 0) {
                alignment.doc1_sections.forEach(section => {
                    if (isDirectMethod) {
                        // For direct method, sections are key_points (descriptive text)
                        // Try to find this text in the document
                        addFallbackHighlight(section.substring(0, 150), doc1Text, doc1Highlights, color, id, topicName);
                    } else {
                        // For template method, sections are section IDs
                        const matchedSection = findSectionMatch(section, doc1Lookup);
                        if (matchedSection && matchedSection.start_char !== undefined && matchedSection.end_char) {
                            doc1Highlights.push({
                                start: matchedSection.start_char,
                                end: matchedSection.end_char,
                                color,
                                id,
                                name: topicName
                            });
                        } else {
                            addFallbackHighlight(section.substring(0, 120), doc1Text, doc1Highlights, color, id, topicName);
                        }
                    }
                });
            }
            
            // Try to find sections in doc2
            if (alignment.doc2_sections && alignment.doc2_sections.length > 0) {
                alignment.doc2_sections.forEach(section => {
                    if (isDirectMethod) {
                        // For direct method, sections are key_points (descriptive text)
                        // Try to find this text in the document
                        addFallbackHighlight(section.substring(0, 150), doc2Text, doc2Highlights, color, id, topicName);
                    } else {
                        // For template method, sections are section IDs
                        const matchedSection = findSectionMatch(section, doc2Lookup);
                        if (matchedSection && matchedSection.start_char !== undefined && matchedSection.end_char) {
                            doc2Highlights.push({
                                start: matchedSection.start_char,
                                end: matchedSection.end_char,
                                color,
                                id,
                                name: topicName
                            });
                        } else {
                            addFallbackHighlight(section.substring(0, 120), doc2Text, doc2Highlights, color, id, topicName);
                        }
                    }
                });
            }
        });
        
        // Apply highlights to doc1
        renderDocumentWithHighlights(doc1Text, doc1Highlights, doc1Content);
        renderDocumentWithHighlights(doc2Text, doc2Highlights, doc2Content);
        
        console.log('✅ Topic-based documents rendered');
        console.log('Doc1 highlights:', doc1Highlights.length);
        console.log('Doc2 highlights:', doc2Highlights.length);
        
        // Add click handlers
        addHighlightClickHandlers();
    }
    
    function renderDocumentWithHighlights(text, highlights, container) {
        const frag = document.createDocumentFragment();
        let lastPos = 0;
        const sorted = [...highlights].sort((a, b) => a.start - b.start);
        
        sorted.forEach(highlight => {
            if (highlight.start > lastPos) {
                frag.appendChild(document.createTextNode(text.slice(lastPos, highlight.start)));
            }
            
            const span = document.createElement('span');
            span.classList.add('highlight');
            span.setAttribute('data-alignment-id', highlight.id);
            span.style.backgroundColor = highlight.color;
            span.title = highlight.name;
            span.appendChild(document.createTextNode(text.slice(highlight.start, highlight.end)));
            frag.appendChild(span);
            lastPos = highlight.end;
        });
        
        if (lastPos < text.length) {
            frag.appendChild(document.createTextNode(text.slice(lastPos)));
        }
        
        container.innerHTML = '';
        container.appendChild(frag);
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

    function normalizeLabel(text) {
        return (text || '')
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, ' ')
            .trim();
    }

    function buildSectionLookup(sections) {
        return (sections || []).map(section => ({
            ...section,
            normalizedTitle: normalizeLabel(section.title),
            normalizedId: normalizeLabel(section.section_id || section.title || '')
        }));
    }

    function findSectionMatch(label, lookup) {
        const normalizedLabel = normalizeLabel(label);
        if (!normalizedLabel) {
            return null;
        }

        let match = lookup.find(
            section => section.normalizedId && section.normalizedId === normalizedLabel
        );
        if (match) {
            return match;
        }

        match = lookup.find(
            section => section.normalizedTitle && section.normalizedTitle === normalizedLabel
        );
        if (match) {
            return match;
        }

        match = lookup.find(
            section =>
                section.normalizedTitle &&
                (section.normalizedTitle.includes(normalizedLabel) ||
                    normalizedLabel.includes(section.normalizedTitle))
        );
        if (match) {
            return match;
        }

        const numberMatch = label ? label.match(/\d+(\.\d+)+/) : null;
        if (numberMatch) {
            const normalizedNumber = normalizeLabel(numberMatch[0]);
            match = lookup.find(
                section =>
                    (section.normalizedId && section.normalizedId.includes(normalizedNumber)) ||
                    (section.normalizedTitle && section.normalizedTitle.includes(normalizedNumber))
            );
            if (match) {
                return match;
            }
        }

        return null;
    }

    function addFallbackHighlight(searchText, documentText, highlights, color, id, name) {
        if (!searchText) {
            return;
        }
        const normalizedDoc = documentText.toLowerCase();
        const normalizedSearch = searchText.toLowerCase();
        const pos = normalizedDoc.indexOf(normalizedSearch);
        if (pos !== -1) {
            const length = Math.max(searchText.length, 120);
            highlights.push({
                start: pos,
                end: Math.min(pos + length, documentText.length),
                color,
                id,
                name
            });
        }
    }

    function escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
});
