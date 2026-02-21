# Streamlit Web Demo Setup

This guide explains how to deploy the Streamlit web demo so users can access it online.

## 🚀 Deploy to Streamlit Cloud (Free)

### Step 1: Push to GitHub
Make sure your code is pushed to GitHub (already done).

### Step 2: Go to Streamlit Cloud
1. Visit: https://share.streamlit.io/
2. Sign in with your GitHub account
3. Click "New app"

### Step 3: Configure Your App
- **Repository**: `29SalahMo/Interactive-learnig`
- **Branch**: `main`
- **Main file path**: `streamlit_app.py`
- **Python version**: 3.10 or 3.11

### Step 4: Deploy
Click "Deploy" and wait for the app to build and launch.

### Step 5: Get Your URL
Once deployed, you'll get a URL like:
`https://interactive-learnig.streamlit.app/`

## 📝 Update README

After deployment, update the Streamlit badge URL in README.md with your actual Streamlit Cloud URL.

## 🎯 What Users Get

Users can now:
- Visit the Streamlit URL
- Play the interactive quiz directly in their browser
- No installation required
- Works on any device with a browser

## 🔧 Local Testing

To test locally before deploying:
```bash
pip install streamlit
streamlit run streamlit_app.py
```

Then visit: http://localhost:8501

## 📦 Requirements

The Streamlit demo uses minimal requirements (just Streamlit) to keep it lightweight and fast to load.

For the full desktop application, use `requirements.txt` instead.
