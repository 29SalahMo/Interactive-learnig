# Web Pages Setup Guide

This guide explains how to enable the web pages so users can access your project online.

## ✅ What Has Been Created

1. **GitHub Pages Site** (`docs/index.html`)
   - Beautiful landing page with interactive quiz demo
   - Shows project features and links
   - Sample questions users can try

2. **Streamlit Web App** (`streamlit_app.py`)
   - Full interactive quiz that runs in the browser
   - No installation needed
   - Works on any device

3. **GitHub Actions Workflow** (`.github/workflows/pages.yml`)
   - Automatically deploys GitHub Pages when you push changes

## 🚀 Enable GitHub Pages

### Step 1: Go to Repository Settings
1. Go to your GitHub repository: https://github.com/29SalahMo/Interactive-learnig
2. Click on **Settings** (top menu)
3. Scroll down to **Pages** (left sidebar)

### Step 2: Configure GitHub Pages
1. Under **Source**, select: **GitHub Actions**
2. The workflow will automatically deploy your site
3. Wait a few minutes for the first deployment

### Step 3: Get Your URL
After deployment, your site will be available at:
```
https://29salahmo.github.io/Interactive-learnig/
```

This URL is automatically generated from your GitHub username and repository name.

## 🎮 Enable Streamlit Cloud (Optional)

### Step 1: Visit Streamlit Cloud
1. Go to: https://share.streamlit.io/
2. Sign in with your GitHub account

### Step 2: Deploy Your App
1. Click **"New app"**
2. Select repository: `29SalahMo/Interactive-learnig`
3. Branch: `main`
4. Main file: `streamlit_app.py`
5. Click **"Deploy"**

### Step 3: Get Your Streamlit URL
After deployment, you'll get a URL like:
```
https://interactive-learnig.streamlit.app/
```

## 📝 Update README Links

After getting your URLs, you can update the README.md badges with the actual URLs if needed. The current badges use placeholder URLs that will work once you enable the services.

## 🎯 What Users Can Do Now

Once enabled, users can:

1. **Visit GitHub Pages**: 
   - See a beautiful landing page
   - Try sample quiz questions
   - Learn about the project
   - Access all download links

2. **Use Streamlit Demo**:
   - Play the full interactive quiz
   - Answer questions in the browser
   - See their score
   - No installation needed

3. **Download Desktop App**:
   - Get the full version with all features
   - Face recognition
   - Gesture control
   - TUIO markers support

## 🔍 Verify Everything Works

1. **GitHub Pages**: 
   - Visit: https://29salahmo.github.io/Interactive-learnig/
   - Should see the landing page

2. **Streamlit** (if deployed):
   - Visit your Streamlit Cloud URL
   - Should see the interactive quiz

3. **GitHub Repository**:
   - All files are pushed
   - README shows the badges

## 🎉 Result

Your project now has:
- ✅ Beautiful web landing page (GitHub Pages)
- ✅ Interactive web quiz (Streamlit)
- ✅ Desktop application (GitHub repository)
- ✅ Multiple ways for users to access and test your project

Users can now **use your project directly on GitHub** without downloading anything!
