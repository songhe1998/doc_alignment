# ⚡ Render.com Quick Deploy Guide

## 1️⃣ Push to GitHub (5 minutes)

```bash
# In your project directory
cd /Users/songhewang/Desktop/doc_alignment

# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit"

# Create repo on GitHub: https://github.com/new
# Then:
git remote add origin https://github.com/YOUR_USERNAME/legal-doc-alignment.git
git branch -M main
git push -u origin main
```

## 2️⃣ Deploy on Render (5 minutes)

1. **Sign up/Login**: https://render.com

2. **New Web Service**: Click "New +" → "Web Service"

3. **Connect Repository**: Select your `legal-doc-alignment` repo

4. **Configure**:
   - **Name**: `legal-doc-alignment`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free

5. **Environment Variables**:
   - Add `OPENAI_API_KEY` = `sk-proj-...` (your API key)
   - Add `SECRET_KEY` = (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)

6. **Click "Create Web Service"**

## 3️⃣ Done! 🎉

Your app will be live at:
```
https://legal-doc-alignment.onrender.com
```

Wait 2-5 minutes for initial deploy to complete.

---

## 🔄 Update Your App

```bash
# Make changes
nano app.py

# Deploy
git add .
git commit -m "Update"
git push
```

Render auto-deploys in ~2 minutes!

---

## 🐛 If Something Goes Wrong

1. **Check Logs** on Render dashboard
2. **Verify** `OPENAI_API_KEY` is set correctly
3. **Ensure** all files are pushed to GitHub:
   ```bash
   git status  # should say "nothing to commit"
   ```

---

## 📱 Share Your App

Send this URL to anyone:
```
https://YOUR-SERVICE-NAME.onrender.com
```

**Note**: Free tier sleeps after 15 mins. First request takes ~30 sec to wake up.

---

**Need detailed help?** See `RENDER_DEPLOYMENT_GUIDE.md`

