# 🚀 Complete Render.com Deployment Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Prepare Your Repository](#prepare-your-repository)
3. [Deploy to Render](#deploy-to-render)
4. [Configure Environment Variables](#configure-environment-variables)
5. [Access Your Live App](#access-your-live-app)
6. [Troubleshooting](#troubleshooting)
7. [Updating Your App](#updating-your-app)

---

## ✅ Prerequisites

Before deploying, make sure you have:

1. **GitHub Account** (free)
   - Sign up at https://github.com if you don't have one

2. **Render Account** (free)
   - Sign up at https://render.com
   - Can use your GitHub account to sign in

3. **OpenAI API Key**
   - Get it from https://platform.openai.com/api-keys
   - Make sure you have credits available

4. **Git Installed** on your computer
   - Check: `git --version`
   - Download from https://git-scm.com if needed

---

## 📦 Prepare Your Repository

### Step 1: Initialize Git (if not already done)

```bash
cd /Users/songhewang/Desktop/doc_alignment
git init
```

### Step 2: Create a `.gitignore` file (if not exists)

The repository already has a `.gitignore`, but make sure it contains:

```
# Environment variables
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# IDE
.vscode/
.idea/

# OS
.DS_Store

# Extracted files (from demos)
*_extracted.txt
nda_alignment_results.txt
nda_comparison_results.txt
```

### Step 3: Commit your code

```bash
# Add all files
git add .

# Commit
git commit -m "Initial commit - Legal Document Alignment Tool"
```

### Step 4: Create GitHub Repository

1. Go to https://github.com
2. Click the **"+"** icon in top-right → **"New repository"**
3. Fill in:
   - **Repository name**: `legal-doc-alignment` (or your choice)
   - **Description**: `AI-powered legal document alignment tool with GPT-4o`
   - **Visibility**: Public (for free Render hosting) or Private (requires paid Render plan)
4. **DO NOT** initialize with README (you already have files)
5. Click **"Create repository"**

### Step 5: Push to GitHub

```bash
# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/legal-doc-alignment.git

# Push code
git branch -M main
git push -u origin main
```

**Example:**
```bash
git remote add origin https://github.com/johndoe/legal-doc-alignment.git
git branch -M main
git push -u origin main
```

---

## 🌐 Deploy to Render

### Step 1: Sign in to Render

1. Go to https://render.com
2. Click **"Get Started"**
3. Sign in with GitHub (recommended) or email

### Step 2: Connect GitHub

1. After signing in, click **"New +"** → **"Web Service"**
2. Click **"Connect a repository"**
3. If first time: Authorize Render to access your GitHub
4. You'll see a list of your repositories

### Step 3: Select Your Repository

1. Find **"legal-doc-alignment"** (or your repo name)
2. Click **"Connect"**

### Step 4: Configure Web Service

Fill in the following settings:

#### Basic Settings
- **Name**: `legal-doc-alignment` (or your choice - this will be in your URL)
- **Region**: Choose closest to you (e.g., `Oregon (US West)`)
- **Branch**: `main`
- **Root Directory**: Leave blank
- **Runtime**: `Python 3`

#### Build & Deploy Settings
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```

- **Start Command**:
  ```
  gunicorn app:app
  ```

#### Instance Type
- Select **"Free"** (or paid if you prefer)
  - Free tier limitations:
    - Goes to sleep after 15 mins of inactivity
    - Takes ~30 seconds to wake up on first request
    - 750 hours/month free

#### Advanced Settings (expand this section)
- **Auto-Deploy**: `Yes` (recommended - auto-deploys on git push)

### Step 5: Add Environment Variables

**CRITICAL STEP - Your app won't work without this!**

Scroll down to **"Environment Variables"** section and add:

1. Click **"Add Environment Variable"**

2. Add **OPENAI_API_KEY**:
   - **Key**: `OPENAI_API_KEY`
   - **Value**: `sk-proj-...` (your actual OpenAI API key)
   - Click **"Add"**

3. Add **SECRET_KEY** (for Flask sessions):
   - **Key**: `SECRET_KEY`
   - **Value**: Generate a random string, or run:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
   - Click **"Add"**

4. (Optional) Add **PYTHON_VERSION**:
   - **Key**: `PYTHON_VERSION`
   - **Value**: `3.9.18`
   - Click **"Add"**

### Step 6: Deploy!

1. Click **"Create Web Service"** at the bottom
2. Render will now:
   - Clone your repository
   - Install dependencies
   - Start your app
3. Watch the logs in real-time (this takes 2-5 minutes)

---

## 🔧 Configure Environment Variables

You can add/edit environment variables anytime:

1. Go to your service dashboard on Render
2. Click **"Environment"** in left sidebar
3. Add or edit variables
4. Click **"Save Changes"**
5. App will automatically redeploy

---

## 🎉 Access Your Live App

### Your App URL

Once deployed, your app will be available at:
```
https://legal-doc-alignment.onrender.com
```

(Replace `legal-doc-alignment` with your actual service name)

### Test Your Deployment

1. Visit your URL
2. Upload two PDF or TXT documents
3. Select an alignment method:
   - **Section-Based**: Compares full documents semantically
   - **Topic-Based (Template)**: Uses standard legal topics
   - **Topic-Based (Direct)**: Extracts and aligns topics directly
4. Click **"Align Documents"**
5. View results!

---

## 🐛 Troubleshooting

### Issue: "Application Error" or "503 Service Unavailable"

**Cause**: App failed to start

**Solutions**:
1. Check the **Logs** tab on Render dashboard
2. Common issues:
   - Missing `OPENAI_API_KEY` → Add it in Environment Variables
   - Wrong Python version → Add `PYTHON_VERSION=3.9.18`
   - Import errors → Check `requirements.txt`

### Issue: "Free instance will spin down with inactivity"

**Cause**: Free tier limitation

**Solutions**:
- **Accept it**: First request after sleep takes ~30 seconds
- **Upgrade**: Pay $7/month for always-on instance
- **Keep-alive service**: Use UptimeRobot (free) to ping your app every 5 mins

### Issue: "Build failed"

**Cause**: Dependencies installation failed

**Solutions**:
1. Check logs for specific error
2. Verify `requirements.txt` is correct:
   ```
   Flask==3.0.0
   openai==1.3.0
   python-dotenv==1.0.0
   PyPDF2==3.0.1
   Werkzeug==3.0.1
   gunicorn==21.2.0
   ```
3. Make sure all files are committed to Git

### Issue: "OpenAI API Error" when using the app

**Cause**: API key issue

**Solutions**:
1. Verify `OPENAI_API_KEY` is set correctly in Environment Variables
2. Check your OpenAI account has available credits
3. Verify the API key is valid at https://platform.openai.com/api-keys

### Issue: "Module not found" errors in logs

**Cause**: Missing dependencies

**Solutions**:
1. Add missing package to `requirements.txt`
2. Commit and push:
   ```bash
   git add requirements.txt
   git commit -m "Add missing dependency"
   git push
   ```
3. Render will auto-deploy

### Issue: App is slow or timing out

**Cause**: GPT-4o calls can take 10-30 seconds

**Solutions**:
1. This is normal - LLM processing takes time
2. For very large documents, consider:
   - Upgrading Render instance
   - Optimizing prompts
   - Implementing request timeouts

---

## 🔄 Updating Your App

### Method 1: Auto-Deploy (Recommended)

If you enabled "Auto-Deploy", just push to GitHub:

```bash
# Make changes to your code
nano app.py  # or use your editor

# Commit changes
git add .
git commit -m "Description of changes"

# Push to GitHub
git push

# Render automatically deploys! ✨
```

Watch deployment progress on Render dashboard.

### Method 2: Manual Deploy

1. Go to your service on Render dashboard
2. Click **"Manual Deploy"** → **"Deploy latest commit"**
3. Render rebuilds and deploys

### Viewing Deployment Logs

1. Click **"Logs"** tab in Render dashboard
2. See real-time logs including:
   - Build process
   - Application startup
   - Request logs
   - Errors and debugging info

---

## 📊 Monitoring Your App

### Check App Status

- **Dashboard**: See if app is running, sleeping, or failed
- **Metrics**: View CPU, memory usage (paid plans)
- **Logs**: Real-time application logs

### View Request Logs

When users use your app, you'll see in logs:
```
🚀 NEW ALIGNMENT REQUEST
✅ API key found: sk-proj-...
📄 Doc1: nda_1.pdf
📄 Doc2: nda_2.pdf
🎯 Method: topic_direct
...
✅ ALIGNMENT COMPLETE: 8 alignments found
```

---

## 💰 Pricing

### Free Tier
- **750 hours/month** free
- Sleeps after 15 mins inactivity
- ~30 second cold start
- Perfect for demos and personal use

### Starter Plan ($7/month)
- Always on
- No cold starts
- Better performance
- Recommended for production

### OpenAI Costs
- GPT-4o: ~$0.005 per request for your use case
- With 12K char documents, ~$0.02-0.05 per alignment
- Set usage limits in OpenAI dashboard

---

## 🔒 Security Best Practices

### 1. Protect Your API Keys
- ✅ **NEVER** commit `.env` to Git
- ✅ Use Render Environment Variables
- ✅ Rotate keys periodically

### 2. Set OpenAI Usage Limits
- Go to https://platform.openai.com/settings/organization/billing/limits
- Set monthly spending limit
- Get email alerts

### 3. Monitor Logs
- Check Render logs regularly
- Look for unusual activity
- Track API usage on OpenAI dashboard

---

## 📝 Quick Reference

### Important URLs
- **Your App**: `https://YOUR-SERVICE-NAME.onrender.com`
- **Render Dashboard**: https://dashboard.render.com
- **GitHub Repo**: `https://github.com/YOUR_USERNAME/legal-doc-alignment`
- **OpenAI Dashboard**: https://platform.openai.com

### Key Commands
```bash
# Deploy updates
git add .
git commit -m "Update message"
git push

# View local logs
tail -f /var/log/render/app.log  # on Render server

# Restart app (via dashboard or)
render services restart YOUR-SERVICE-ID
```

### Files Required for Deployment
- ✅ `app.py` - Main application
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Start command
- ✅ `render.yaml` - Render configuration (optional but helpful)
- ✅ `templates/` - HTML templates
- ✅ `static/` - CSS, JS files
- ✅ `.gitignore` - Ignore `.env` and temporary files

---

## 🎯 Summary: Deployment Checklist

- [ ] Code committed to Git
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] GitHub connected to Render
- [ ] Web Service created on Render
- [ ] `OPENAI_API_KEY` environment variable set
- [ ] `SECRET_KEY` environment variable set
- [ ] Build completed successfully
- [ ] App accessible at Render URL
- [ ] Test with sample documents
- [ ] Share your app! 🎉

---

## 🆘 Need Help?

### Resources
- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **Flask Docs**: https://flask.palletsprojects.com
- **OpenAI Docs**: https://platform.openai.com/docs

### Common Questions

**Q: Can I use a custom domain?**
A: Yes! Render supports custom domains on all paid plans.

**Q: How do I see who's using my app?**
A: Check the Logs tab for request logs, or add analytics (Google Analytics, etc.)

**Q: Can I password-protect my app?**
A: Yes! You can add Flask-Login or HTTP Basic Auth. Let me know if you need help with this.

**Q: What if I hit OpenAI rate limits?**
A: Implement request queuing or upgrade your OpenAI tier.

---

## 🎊 You're All Set!

Your legal document alignment tool is now live and accessible to anyone with the URL!

**Next Steps:**
1. Test thoroughly with different document types
2. Share the URL with colleagues
3. Monitor usage and costs
4. Consider adding more features!

---

**Happy Deploying! 🚀**

