// Main JavaScript for Legal Document Alignment Tool

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('alignmentForm');
    const doc1Input = document.getElementById('doc1');
    const doc2Input = document.getElementById('doc2');
    const file1Name = document.getElementById('file1Name');
    const file2Name = document.getElementById('file2Name');
    const submitBtn = document.getElementById('submitBtn');
    const resultsSection = document.getElementById('resultsSection');
    const resultsContent = document.getElementById('resultsContent');
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
                // Scroll to results
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
        let html = '';
        
        // Summary section
        html += '<div class="result-summary">';
        html += `<h3>🎯 ${data.method}</h3>`;
        html += '<div class="stat-grid">';
        
        if (data.method.includes('Section-Based')) {
            html += `
                <div class="stat-item">
                    <div class="stat-value">${data.doc1_sections}</div>
                    <div class="stat-label">Doc 1 Sections</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${data.doc2_sections}</div>
                    <div class="stat-label">Doc 2 Sections</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${data.alignments_found}</div>
                    <div class="stat-label">Alignments Found</div>
                </div>
            `;
        } else if (data.method.includes('Template')) {
            html += `
                <div class="stat-item">
                    <div class="stat-value">${data.document_type || 'N/A'}</div>
                    <div class="stat-label">Document Type</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${data.standard_topics}</div>
                    <div class="stat-label">Standard Topics</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${data.doc1_topics}</div>
                    <div class="stat-label">Doc 1 Topics</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${data.doc2_topics}</div>
                    <div class="stat-label">Doc 2 Topics</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${data.alignments_found}</div>
                    <div class="stat-label">Alignments</div>
                </div>
            `;
        } else {
            html += `
                <div class="stat-item">
                    <div class="stat-value">${data.doc1_topics}</div>
                    <div class="stat-label">Doc 1 Topics</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${data.doc2_topics}</div>
                    <div class="stat-label">Doc 2 Topics</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${data.alignments_found}</div>
                    <div class="stat-label">Alignments Found</div>
                </div>
            `;
        }
        
        html += '</div></div>';
        
        // Alignments
        if (data.alignments && data.alignments.length > 0) {
            html += '<h3 style="margin-top: 30px; margin-bottom: 20px; color: #667eea;">📋 Detailed Alignments</h3>';
            
            data.alignments.forEach((alignment, index) => {
                const confidence = alignment.confidence || alignment.similarity || 'medium';
                html += `<div class="alignment-card ${confidence}">`;
                html += `<div class="alignment-header">`;
                html += `<h4>Alignment ${index + 1}</h4>`;
                html += `<span class="confidence-badge ${confidence}">${confidence.toUpperCase()}</span>`;
                html += `</div>`;
                
                if (data.method.includes('Section-Based')) {
                    html += renderSectionAlignment(alignment);
                } else if (data.method.includes('Template')) {
                    html += renderTopicTemplateAlignment(alignment);
                } else {
                    html += renderTopicDirectAlignment(alignment);
                }
                
                html += '</div>';
            });
        } else {
            html += '<p style="text-align: center; color: #666; padding: 40px;">No alignments found.</p>';
        }
        
        resultsContent.innerHTML = html;
    }

    function renderSectionAlignment(alignment) {
        let html = '<div class="doc-comparison">';
        
        html += '<div class="doc-side">';
        html += '<h4>📄 Document 1</h4>';
        html += `<p><strong>Section ${alignment.doc1_section}:</strong> ${alignment.doc1_title}</p>`;
        html += '</div>';
        
        html += '<div class="doc-side">';
        html += '<h4>📄 Document 2</h4>';
        html += `<p><strong>Section ${alignment.doc2_section}:</strong> ${alignment.doc2_title}</p>`;
        html += '</div>';
        
        html += '</div>';
        
        if (alignment.in_doc1_not_doc2 && alignment.in_doc1_not_doc2.length > 0) {
            html += '<div class="differences">';
            html += '<h4>📝 In Document 1 but NOT in Document 2:</h4>';
            html += '<ul>';
            alignment.in_doc1_not_doc2.forEach(diff => {
                html += `<li>${diff}</li>`;
            });
            html += '</ul>';
            html += '</div>';
        }
        
        if (alignment.in_doc2_not_doc1 && alignment.in_doc2_not_doc1.length > 0) {
            html += '<div class="differences" style="margin-top: 10px;">';
            html += '<h4>📝 In Document 2 but NOT in Document 1:</h4>';
            html += '<ul>';
            alignment.in_doc2_not_doc1.forEach(diff => {
                html += `<li>${diff}</li>`;
            });
            html += '</ul>';
            html += '</div>';
        }
        
        return html;
    }

    function renderTopicTemplateAlignment(alignment) {
        let html = '';
        
        // Topic header with star if standard
        html += `<div style="margin-bottom: 20px;">`;
        const star = alignment.is_standard ? '⭐ ' : '';
        html += `<h3 style="color: #667eea; margin: 0 0 10px 0;">${star}🏷️ ${alignment.topic_name || 'Topic'}</h3>`;
        if (alignment.topic_description) {
            html += `<p style="color: #666; font-style: italic; margin: 0 0 15px 0;">${alignment.topic_description}</p>`;
        }
        if (alignment.is_standard) {
            html += `<p style="color: #999; font-size: 12px; margin: 0 0 15px 0;">⭐ Standard topic for this document type</p>`;
        }
        html += `</div>`;
        
        // Documents comparison
        html += '<div class="doc-comparison">';
        
        // Document 1
        html += '<div class="doc-side">';
        html += '<h4>📄 Document 1</h4>';
        
        if (alignment.doc1_sections && alignment.doc1_sections.length > 0) {
            html += '<p><strong>Sections:</strong></p>';
            html += '<ul>';
            alignment.doc1_sections.forEach(section => {
                html += `<li>${section}</li>`;
            });
            html += '</ul>';
            
            if (alignment.doc1_summary) {
                html += `<p><strong>Summary:</strong> ${alignment.doc1_summary}</p>`;
            }
        } else {
            html += '<p style="color: #999; font-style: italic;">Not present in Document 1</p>';
        }
        html += '</div>';
        
        // Document 2
        html += '<div class="doc-side">';
        html += '<h4>📄 Document 2</h4>';
        
        if (alignment.doc2_sections && alignment.doc2_sections.length > 0) {
            html += '<p><strong>Sections:</strong></p>';
            html += '<ul>';
            alignment.doc2_sections.forEach(section => {
                html += `<li>${section}</li>`;
            });
            html += '</ul>';
            
            if (alignment.doc2_summary) {
                html += `<p><strong>Summary:</strong> ${alignment.doc2_summary}</p>`;
            }
        } else {
            html += '<p style="color: #999; font-style: italic;">Not present in Document 2</p>';
        }
        html += '</div>';
        
        html += '</div>';
        
        // Key differences
        if (alignment.differences) {
            html += '<div class="differences">';
            html += '<h4>🔍 Key Differences:</h4>';
            html += `<p>${alignment.differences}</p>`;
            html += '</div>';
        }
        
        return html;
    }

    function renderTopicDirectAlignment(alignment) {
        let html = '';
        
        // Topic header
        html += `<div style="margin-bottom: 20px;">`;
        html += `<h3 style="color: #667eea; margin: 0 0 10px 0;">🏷️ ${alignment.topic_name || 'Topic'}</h3>`;
        if (alignment.topic_description) {
            html += `<p style="color: #666; font-style: italic; margin: 0 0 15px 0;">${alignment.topic_description}</p>`;
        }
        html += `</div>`;
        
        // Documents comparison
        html += '<div class="doc-comparison">';
        
        // Document 1
        html += '<div class="doc-side">';
        html += '<h4>📄 Document 1</h4>';
        
        if (alignment.doc1_sections && alignment.doc1_sections.length > 0) {
            html += '<p><strong>Sections:</strong></p>';
            html += '<ul>';
            alignment.doc1_sections.forEach(section => {
                html += `<li>${section}</li>`;
            });
            html += '</ul>';
            
            if (alignment.doc1_summary) {
                html += `<p><strong>Summary:</strong> ${alignment.doc1_summary}</p>`;
            }
        } else {
            html += '<p style="color: #999; font-style: italic;">Not present in Document 1</p>';
        }
        html += '</div>';
        
        // Document 2
        html += '<div class="doc-side">';
        html += '<h4>📄 Document 2</h4>';
        
        if (alignment.doc2_sections && alignment.doc2_sections.length > 0) {
            html += '<p><strong>Sections:</strong></p>';
            html += '<ul>';
            alignment.doc2_sections.forEach(section => {
                html += `<li>${section}</li>`;
            });
            html += '</ul>';
            
            if (alignment.doc2_summary) {
                html += `<p><strong>Summary:</strong> ${alignment.doc2_summary}</p>`;
            }
        } else {
            html += '<p style="color: #999; font-style: italic;">Not present in Document 2</p>';
        }
        html += '</div>';
        
        html += '</div>';
        
        // Key differences
        if (alignment.differences) {
            html += '<div class="differences">';
            html += '<h4>🔍 Key Differences:</h4>';
            html += `<p>${alignment.differences}</p>`;
            html += '</div>';
        }

        return html;
    }
});

