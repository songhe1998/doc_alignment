# 📄 Legal Document Alignment Web Application

A beautiful, AI-powered web application that allows anyone to compare and align legal documents using three different intelligent methods.

![Legal Document Alignment](https://img.shields.io/badge/AI-Powered-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Flask](https://img.shields.io/badge/Flask-3.0-red)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-purple)

---

## 🌟 Features

### Three Powerful Alignment Methods

1. **📋 Section-Based Alignment**
   - Extracts numbered sections (1.1, 2.3, etc.)
   - Matches sections by semantic similarity
   - Fast and efficient for structured documents
   - Best for documents with similar section numbering

2. **📚 Topic-Based Alignment (Template)**
   - Identifies document type (NDA, License Agreement, etc.)
   - Uses standard legal topics as reference
   - Shows what's missing from industry standards
   - Best for compliance checking and template adherence

3. **🎯 Topic-Based Alignment (Direct)**
   - Extracts topics directly from documents
   - No predefined templates needed
   - Discovers unique content automatically
   - Best for comparing documents with different structures

### User-Friendly Interface

- ✨ Beautiful modern UI with gradient design
- 📤 Drag-and-drop file upload (PDF and TXT)
- 🎨 Color-coded confidence levels
- 📊 Real-time results display
- 📱 Fully responsive (mobile-friendly)
- ⚡ Fast processing with loading indicators

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/doc-alignment.git
cd doc-alignment
```

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set Environment Variables

Create a `.env` file:
```bash
OPENAI_API_KEY=your-openai-api-key-here
SECRET_KEY=your-random-secret-key
```

### 4. Run Locally

```bash
python app.py
```

Visit [http://localhost:5000](http://localhost:5000)

---

## 📁 Project Structure

```
doc-alignment/
├── app.py                      # Flask application
├── alignment.py                # Section-based alignment logic
├── topic_alignment.py          # Topic-based alignment logic
├── templates/
│   └── index.html             # Frontend HTML
├── static/
│   ├── css/
│   │   └── style.css          # Styling
│   └── js/
│       └── main.js            # JavaScript logic
├── uploads/                    # Temporary file storage
├── requirements.txt            # Python dependencies
├── Procfile                    # For deployment
├── DEPLOYMENT_GUIDE.md         # Deployment instructions
└── README.md                   # This file
```

---

## 🎨 How It Works

### User Flow

```
1. User uploads two documents (PDF or TXT)
        ↓
2. Selects alignment method
        ↓
3. Clicks "Align Documents"
        ↓
4. AI processes documents in backend
        ↓
5. Results displayed with visualizations
```

### Backend Process

```python
# Section-Based
Extract Sections → Align Sections → Compare Content → Display

# Topic-Template
Identify Type → Research Topics → Extract Topics → Align → Compare

# Topic-Direct
Extract Topics from Doc1 → Extract Topics from Doc2 → Align → Compare
```

---

## 💡 Usage Examples

### Example 1: Compare Two NDAs

```
1. Upload: nda_company_a.pdf and nda_company_b.pdf
2. Select: Topic-Based (Direct)
3. Result: See which clauses differ and what's unique to each
```

### Example 2: Check License Agreement Compliance

```
1. Upload: your_license.pdf and standard_template.pdf
2. Select: Topic-Based (Template)
3. Result: See what standard clauses you're missing
```

### Example 3: Track Contract Changes

```
1. Upload: contract_v1.pdf and contract_v2.pdf
2. Select: Section-Based
3. Result: See exactly what changed between versions
```

---

## 🔧 Configuration

### File Upload Limits

```python
# In app.py
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
```

### Supported File Types

- `.txt` - Plain text files
- `.pdf` - PDF documents (text extraction via PyPDF2)

---

## 🎯 Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

**Quick Deploy to Render:**

1. Push code to GitHub
2. Connect repository on Render.com
3. Set environment variables
4. Deploy!

Your app will be live at `https://your-app.onrender.com`

---

## 📊 API Costs

### Estimated Costs per Comparison

| Method | Tokens Used | Cost (GPT-4o) |
|--------|------------|---------------|
| Section-Based | ~3,000-5,000 | $0.02-0.05 |
| Topic-Template | ~8,000-12,000 | $0.10-0.15 |
| Topic-Direct | ~6,000-10,000 | $0.08-0.12 |

**Monthly Cost Estimates:**
- 10 comparisons: ~$1-2
- 100 comparisons: ~$10-15
- 1000 comparisons: ~$100-150

---

## 🔒 Security

### Best Practices Implemented

- ✅ Environment variables for sensitive data
- ✅ File type validation
- ✅ File size limits
- ✅ Secure file handling
- ✅ No permanent file storage

### Recommended Additions

```bash
# Add rate limiting
pip install Flask-Limiter

# Add CORS protection
pip install flask-cors

# Add user authentication (optional)
pip install Flask-Login
```

---

## 🐛 Troubleshooting

### Common Issues

**1. "OpenAI API key not configured"**
- Check `.env` file exists
- Verify `OPENAI_API_KEY` is set correctly

**2. "Error extracting PDF"**
- Ensure PDF has extractable text (not scanned image)
- Try converting to TXT first

**3. "File too large"**
- Max size is 16MB
- Compress PDF or split document

**4. Slow processing**
- Processing time: 10-60 seconds depending on method
- Longer documents take more time
- Topic-Template method is slowest

---

## 🎨 Customization

### Change Color Scheme

Edit `static/css/style.css`:
```css
/* Change primary gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* To your colors */
background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
```

### Add New Alignment Method

1. Create function in `app.py`:
```python
def your_new_method(api_key, doc1_text, doc2_text):
    # Your logic here
    return {...}
```

2. Add route handler in `align_documents()`

3. Update frontend HTML with new radio option

---

## 📈 Performance Optimization

### Tips for Production

1. **Enable Caching**:
   ```python
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'simple'})
   ```

2. **Add Result Pagination**:
   - Limit alignments displayed at once
   - Add "Show More" button

3. **Async Processing**:
   ```python
   from celery import Celery
   # Background task processing
   ```

4. **Database Storage**:
   - Store results for reuse
   - Track user comparisons

---

## 🤝 Contributing

Want to improve the app? Here's how:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Ideas for Contributions

- [ ] Add user authentication
- [ ] Store comparison history
- [ ] Export results to PDF/Word
- [ ] Add more document types
- [ ] Implement caching
- [ ] Add API endpoints
- [ ] Create mobile app
- [ ] Add document templates library

---

## 📝 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

- **OpenAI** for GPT-4o API
- **Flask** framework
- **PyPDF2** for PDF processing
- All contributors and users

---

## 📞 Support & Contact

- **Issues**: Open an issue on GitHub
- **Questions**: Start a discussion
- **Email**: your-email@example.com

---

## 🎉 Live Demo

Try it now: **[https://your-app.onrender.com](https://your-app.onrender.com)**

---

**Built with ❤️ for making legal document analysis accessible to everyone**

⭐ Star this repo if you find it useful!

