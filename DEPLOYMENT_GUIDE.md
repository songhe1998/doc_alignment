# 🚀 Deployment Guide - Legal Document Alignment Web App

## Overview

This guide will help you deploy the Legal Document Alignment web application so everyone can access it.

---

## 📋 Prerequisites

1. **OpenAI API Key** - Get one from [https://platform.openai.com/](https://platform.openai.com/)
2. **Git** installed on your machine
3. **Python 3.8+** installed
4. A deployment platform account (choose one):
   - [Render](https://render.com/) - **RECOMMENDED** (Free tier available)
   - [Railway](https://railway.app/) (Free tier available)
   - [Heroku](https://heroku.com/) (Paid)
   - [PythonAnywhere](https://www.pythonanywhere.com/) (Free tier available)

---

## 🌟 Option 1: Deploy to Render (RECOMMENDED)

Render is free, easy to use, and has great Python support.

### Step 1: Prepare Your Repository

```bash
cd /Users/songhewang/Desktop/doc_alignment

# Initialize git if not already done
git init
git add .
git commit -m "Initial commit - Legal Document Alignment App"

# Create a GitHub repository and push
# (Follow GitHub instructions to create a new repository)
git remote add origin https://github.com/YOUR_USERNAME/doc-alignment.git
git push -u origin main
```

### Step 2: Deploy on Render

1. **Sign up** at [https://render.com/](https://render.com/)

2. **Create a New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `doc-alignment` repository

3. **Configure the Service**:
   - **Name**: `legal-document-alignment` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`

4. **Set Environment Variables**:
   - Click "Environment" tab
   - Add variable: `OPENAI_API_KEY` = `your-openai-api-key-here`
   - Add variable: `SECRET_KEY` = `your-random-secret-key`

5. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment (3-5 minutes)
   - Your app will be live at `https://your-app-name.onrender.com`

---

## 🚂 Option 2: Deploy to Railway

Railway offers an excellent free tier with automatic deployments.

### Step 1: Prepare Repository (same as above)

### Step 2: Deploy on Railway

1. **Sign up** at [https://railway.app/](https://railway.app/)

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your `doc-alignment` repository

3. **Configure**:
   - Railway will auto-detect Python and Flask
   - Click on your service → "Variables"
   - Add: `OPENAI_API_KEY` = `your-key`
   - Add: `SECRET_KEY` = `your-secret`

4. **Generate Domain**:
   - Go to "Settings" → "Networking"
   - Click "Generate Domain"
   - Your app will be live at `https://your-app.railway.app`

---

## 🎈 Option 3: Deploy to Heroku

Heroku is reliable but now requires payment.

### Step 1: Install Heroku CLI

```bash
brew install heroku/brew/heroku  # macOS
# Or download from https://devcenter.heroku.com/articles/heroku-cli
```

### Step 2: Deploy

```bash
cd /Users/songhewang/Desktop/doc_alignment

# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set OPENAI_API_KEY=your-key
heroku config:set SECRET_KEY=your-secret

# Deploy
git push heroku main

# Open app
heroku open
```

---

## 🐍 Option 4: Deploy to PythonAnywhere

Good for free tier, but slower than Render/Railway.

### Step 1: Upload Code

1. Sign up at [https://www.pythonanywhere.com/](https://www.pythonanywhere.com/)
2. Open a Bash console
3. Clone your repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/doc-alignment.git
   cd doc-alignment
   pip install -r requirements.txt
   ```

### Step 2: Configure Web App

1. Go to "Web" tab → "Add a new web app"
2. Select "Manual configuration" → "Python 3.10"
3. Set source code directory: `/home/yourusername/doc-alignment`
4. Edit WSGI file:
   ```python
   import sys
   path = '/home/yourusername/doc-alignment'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import app as application
   ```
5. Set environment variables in `.env` file
6. Reload web app

---

## 🔒 Security Best Practices

### 1. Protect Your API Key

**Never commit your `.env` file to Git!**

Create `.env` file locally:
```bash
OPENAI_API_KEY=your-key-here
SECRET_KEY=your-random-secret-key-here
```

### 2. Add Rate Limiting (Optional but Recommended)

Install Flask-Limiter:
```bash
pip install Flask-Limiter
```

Add to `app.py`:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per day", "10 per hour"]
)
```

### 3. Add CORS Protection (if needed)

```bash
pip install flask-cors
```

Add to `app.py`:
```python
from flask_cors import CORS
CORS(app)
```

---

## 📊 Monitoring Usage

### Track OpenAI API Usage

1. Go to [https://platform.openai.com/usage](https://platform.openai.com/usage)
2. Monitor your API costs
3. Set up billing alerts

### Track Web App Usage

For Render:
- Go to your service → "Metrics"
- View requests, response times, errors

For Railway:
- Go to your service → "Metrics"
- View CPU, memory, network usage

---

## 🔧 Troubleshooting

### Common Issues

**1. App Won't Start**
```bash
# Check logs
render logs  # For Render
railway logs  # For Railway
heroku logs --tail  # For Heroku
```

**2. API Key Not Working**
- Verify environment variable is set correctly
- Check for extra spaces in the key
- Ensure `.env` file is not committed to Git

**3. File Upload Errors**
- Check `MAX_CONTENT_LENGTH` in `app.py`
- Ensure upload folder has write permissions

**4. Slow Response**
- Use a paid tier for better performance
- Consider caching results
- Optimize document size limits

---

## 💰 Cost Estimate

### OpenAI API Costs (GPT-4o)

- **Section-Based**: ~$0.02-0.05 per comparison
- **Topic-Template**: ~$0.10-0.15 per comparison
- **Topic-Direct**: ~$0.08-0.12 per comparison

### Hosting Costs

- **Render Free**: $0/month (spins down after inactivity)
- **Render Starter**: $7/month (always on)
- **Railway Free**: $0/month (500 hours/month)
- **Railway Hobby**: $5/month (unlimited)
- **Heroku Basic**: $7/month
- **PythonAnywhere Free**: $0/month (limited)

---

## 🎯 Recommended Setup for Public Use

**For Light Use (< 100 comparisons/month):**
- **Hosting**: Render Free or Railway Free
- **API**: OpenAI Pay-as-you-go
- **Cost**: ~$5-10/month total

**For Moderate Use (100-1000 comparisons/month):**
- **Hosting**: Render Starter ($7/month)
- **API**: OpenAI with rate limiting
- **Cost**: ~$20-50/month

**For Heavy Use:**
- Consider implementing caching
- Use Redis for session storage
- Add user authentication
- Consider paid hosting tier

---

## 🚀 Quick Start Commands

### Local Testing

```bash
cd /Users/songhewang/Desktop/doc_alignment

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY='your-key'
export SECRET_KEY='your-secret'

# Run locally
python app.py

# Visit http://localhost:5000
```

### Production Deploy (Render)

```bash
# Push to GitHub
git add .
git commit -m "Ready for deployment"
git push origin main

# Render will auto-deploy from GitHub
# No additional commands needed!
```

---

## 📝 Post-Deployment Checklist

- [ ] Test all three alignment methods
- [ ] Verify PDF and TXT uploads work
- [ ] Check mobile responsiveness
- [ ] Monitor initial API costs
- [ ] Set up usage alerts
- [ ] Share the URL!

---

## 🎉 You're Live!

Your Legal Document Alignment tool is now accessible to everyone!

**Share your URL:**
- `https://your-app.onrender.com`
- `https://your-app.railway.app`
- Or your custom domain

---

## 📞 Support

If you encounter issues:
1. Check deployment platform logs
2. Verify environment variables
3. Test locally first
4. Check OpenAI API status: [https://status.openai.com/](https://status.openai.com/)

---

**Built with ❤️ for legal document analysis**

