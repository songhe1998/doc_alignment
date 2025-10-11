# 🚀 Vercel Deployment Guide

## ⚠️ Important Limitations

**Before deploying to Vercel, understand these constraints:**

### Time Limits (CRITICAL!)
- **Hobby (Free) Plan**: 10 second timeout
- **Pro Plan**: 60 second timeout

**Problem**: Your alignment methods use GPT-4o which can take 15-60 seconds per request.

**Result**: 
- ❌ Free plan will timeout on most requests
- ⚠️ Pro plan ($20/month) might work but could still timeout on large documents

### Recommendation
**Vercel is NOT ideal for this app** because:
- GPT-4o calls are slow (10-60 seconds)
- Vercel serverless functions have strict time limits
- Render.com is better suited (no timeout issues, cheaper)

**BUT** if you still want to use Vercel for learning/testing, here's how:

---

## 📋 Prerequisites

1. **Vercel Account** (free) - https://vercel.com
2. **GitHub Account** 
3. **OpenAI API Key**
4. **Code on GitHub** (follow GitHub section from RENDER_DEPLOYMENT_GUIDE.md)

---

## 🔧 Configuration Files

### 1. `vercel.json` (Already created)

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "env": {
    "FLASK_APP": "app.py"
  }
}
```

### 2. Update `app.py` for Vercel

Vercel needs a specific export. Add this to the END of `app.py`:

```python
# For Vercel deployment
app_vercel = app
```

This is already compatible with the existing code.

---

## 📦 Deployment Steps

### Step 1: Ensure Code is on GitHub

```bash
cd /Users/songhewang/Desktop/doc_alignment

# Add vercel.json
git add vercel.json

# Commit
git commit -m "Add Vercel configuration"

# Push
git push
```

### Step 2: Deploy to Vercel

#### Option A: Vercel Dashboard (Recommended)

1. **Go to** https://vercel.com/dashboard
2. **Click** "Add New" → "Project"
3. **Import** your GitHub repository
4. **Configure:**
   - Framework Preset: **Other**
   - Root Directory: `./` (leave as is)
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
   - Install Command: `pip install -r requirements.txt`

5. **Environment Variables:**
   Click "Environment Variables" and add:
   
   ```
   OPENAI_API_KEY = sk-proj-your-key-here
   SECRET_KEY = your-random-secret-here
   ```
   
   Generate SECRET_KEY:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

6. **Click "Deploy"**

#### Option B: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: legal-doc-alignment
# - Directory: ./
# - Want to modify settings? Yes
#   - Build Command: (leave empty)
#   - Output Directory: (leave empty)
#   - Development Command: python app.py

# Add environment variables
vercel env add OPENAI_API_KEY
# Paste your API key

vercel env add SECRET_KEY
# Paste generated secret

# Deploy to production
vercel --prod
```

---

## 🌐 Access Your App

After deployment:
```
https://your-project-name.vercel.app
```

Or custom domain (if configured):
```
https://your-domain.com
```

---

## ⚠️ Known Issues & Solutions

### Issue 1: Function Timeout (MOST COMMON)

**Error**: `FUNCTION_INVOCATION_TIMEOUT`

**Cause**: GPT-4o calls take longer than 10 seconds (free plan) or 60 seconds (pro)

**Solutions**:
1. **Upgrade to Pro** ($20/month) for 60s timeout
2. **Optimize prompts** - reduce document size sent to GPT
3. **Use Render.com instead** (recommended - no timeouts)

### Issue 2: Module Not Found

**Error**: `ModuleNotFoundError: No module named 'X'`

**Solution**: Ensure `requirements.txt` includes all dependencies:
```
Flask==3.0.0
openai==1.3.0
python-dotenv==1.0.0
PyPDF2==3.0.1
Werkzeug==3.0.1
```

### Issue 3: File System Access

**Error**: Read-only file system

**Cause**: Vercel functions are read-only

**Solution**: Don't try to write files. Your current app doesn't write files, so this shouldn't be an issue.

### Issue 4: Cold Starts

**Problem**: First request after inactivity is slow (5-10 seconds)

**This is normal** on Vercel's free plan. Pro plan has better performance.

---

## 💰 Pricing Comparison

| Feature | Vercel Free | Vercel Pro | Render Free | Render Starter |
|---------|------------|------------|-------------|----------------|
| **Cost** | $0 | $20/month | $0 | $7/month |
| **Timeout** | 10s ❌ | 60s ⚠️ | None ✅ | None ✅ |
| **Sleep** | No | No | Yes (15min) | No |
| **Good for this app?** | ❌ No | ⚠️ Maybe | ✅ Yes | ✅ Yes |

**Verdict**: Render is better for this app due to no timeout limits.

---

## 🔄 Update Your App

### Auto-Deploy (Recommended)
Vercel auto-deploys on every push to main branch:

```bash
git add .
git commit -m "Update"
git push
```

Vercel rebuilds automatically in ~1-2 minutes.

### Manual Redeploy
```bash
vercel --prod
```

---

## 📊 Monitor Deployments

1. **Dashboard**: https://vercel.com/dashboard
2. **View logs** for each deployment
3. **Check function logs** to debug issues
4. **Monitor usage** (free tier limits)

---

## 🎯 Recommended Optimizations for Vercel

If you want to make it work better on Vercel:

### 1. Reduce Document Size
In `app.py`, reduce max_len:
```python
# Change from 12000 to 6000
max_len = 6000
```

### 2. Reduce Max Tokens
```python
# Change from 4000 to 2000
max_tokens=2000
```

### 3. Add Timeout Handling
```python
try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0.3,
        timeout=30  # Add explicit timeout
    )
except Exception as e:
    if 'timeout' in str(e).lower():
        return {'error': 'Request took too long. Try smaller documents or upgrade to Pro.'}
```

---

## 🆚 Vercel vs Render: Quick Comparison

### Choose Vercel If:
- ✅ You want automatic HTTPS
- ✅ You want global CDN
- ✅ You're okay paying $20/month for Pro
- ✅ You'll optimize for faster responses

### Choose Render If:
- ✅ You need long-running requests (GPT-4o calls)
- ✅ You want cheaper paid plan ($7 vs $20)
- ✅ You want simpler Python app hosting
- ✅ You don't want to worry about timeouts

**For this app: Render is recommended** ⭐

---

## 🐛 Debugging

### Check Logs
```bash
# View recent logs
vercel logs

# View specific deployment
vercel logs [deployment-url]
```

### Test Locally
```bash
# Install Vercel CLI
npm i -g vercel

# Run locally (simulates Vercel environment)
vercel dev
```

---

## 📝 Summary

### Deployment Checklist
- [ ] Code on GitHub
- [ ] `vercel.json` created
- [ ] `requirements.txt` updated
- [ ] Connected GitHub to Vercel
- [ ] Environment variables set (OPENAI_API_KEY, SECRET_KEY)
- [ ] Deployed
- [ ] Tested with small documents first
- [ ] Monitored for timeouts

### If Timeouts Occur:
1. Try smaller documents
2. Upgrade to Vercel Pro ($20/month)
3. **OR switch to Render** (recommended)

---

## 🆘 Need Help?

- **Vercel Docs**: https://vercel.com/docs
- **Vercel Community**: https://github.com/vercel/vercel/discussions
- **Flask on Vercel Guide**: https://vercel.com/guides/using-flask-with-vercel

---

## ⚡ Quick Deploy (If you're sure)

```bash
# 1. Push to GitHub
git add .
git commit -m "Add Vercel config"
git push

# 2. Install Vercel CLI
npm install -g vercel

# 3. Deploy
vercel

# 4. Add env vars
vercel env add OPENAI_API_KEY
vercel env add SECRET_KEY

# 5. Deploy to production
vercel --prod

# Done! Your app is live at https://your-project.vercel.app
```

**But remember: Expect timeouts on free plan!** 

Consider Render.com instead (see RENDER_DEPLOYMENT_GUIDE.md) for a better experience with this app.

