# GitHub Setup Guide

This guide will help you push your Interactive English Learning Quiz project to GitHub.

## Prerequisites

1. **Install Git** (if not already installed):
   - Download from: https://git-scm.com/download/win
   - During installation, make sure to select "Add Git to PATH"

2. **GitHub Account**: Make sure you have a GitHub account and access to the repository:
   - Repository URL: https://github.com/29SalahMo/Interactive-learnig.git

## Step-by-Step Instructions

### Step 1: Open Command Prompt or PowerShell

Navigate to your project directory:
```bash
cd "D:\Interactive learnig english quiz for children"
```

### Step 2: Initialize Git Repository (if not already done)

```bash
git init
```

### Step 3: Add Remote Repository

```bash
git remote add origin https://github.com/29SalahMo/Interactive-learnig.git
```

If the remote already exists, update it:
```bash
git remote set-url origin https://github.com/29SalahMo/Interactive-learnig.git
```

### Step 4: Configure Git (if first time)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Step 5: Add All Files

```bash
git add .
```

### Step 6: Commit Changes

```bash
git commit -m "Initial commit: Interactive English Learning Quiz System"
```

### Step 7: Push to GitHub

```bash
git branch -M main
git push -u origin main
```

If you encounter authentication issues, you may need to:
- Use a Personal Access Token instead of password
- Or use GitHub Desktop application

## Alternative: Using GitHub Desktop

1. Download GitHub Desktop: https://desktop.github.com/
2. Sign in with your GitHub account
3. Click "File" → "Add Local Repository"
4. Select your project folder
5. Click "Publish repository" to push to GitHub

## What Gets Uploaded

The `.gitignore` file has been configured to exclude:
- Python cache files (`__pycache__/`)
- Database files (`*.db`)
- Face encodings (`faces/`, `*.pkl`)
- Compiled files (`*.pyc`)
- IDE settings (`.vscode/`, `.idea/`)
- Build artifacts
- Temporary files

## Important Files Included

✅ All Python source code
✅ Configuration files
✅ Batch scripts
✅ Documentation (`.md` files)
✅ Project structure

## Troubleshooting

### If you get "fatal: not a git repository"
Run: `git init` first

### If you get authentication errors
- Use Personal Access Token: GitHub → Settings → Developer settings → Personal access tokens
- Or use GitHub Desktop for easier authentication

### If you want to update existing repository
```bash
git add .
git commit -m "Update: [describe your changes]"
git push origin main
```

## Next Steps After Uploading

1. Add a comprehensive README.md with:
   - Project description
   - Installation instructions
   - Usage guide
   - Features list

2. Consider adding:
   - License file
   - Contributing guidelines
   - Issue templates

3. Update repository description on GitHub
