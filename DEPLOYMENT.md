# 🚀 Travel Guide Deployment Guide

This project can be deployed easily in **two ways**:
1. **Option 1 (Recommended - Simplest & 100% Free)**: Fullstack unified deployment on **Render** (Frontend + Backend served together from one service — eliminates all CORS issues and requires only one free service).
2. **Option 2**: Decoupled deployment (Frontend on **Vercel** or **Netlify**, Backend on **Render** or **Railway**).

---

## 🔑 Required API Keys
Ensure you have:
- **`GEMINI_API_KEY`**: From [Google AI Studio](https://aistudio.google.com/)
- **`MURF_API_KEY`**: From [Murf AI](https://murf.ai/)

---

## 🌟 Option 1: Deploy on Render (Recommended, Free, Single Service)

### Step 1: Initialize Git and Push to GitHub
1. Open PowerShell or Terminal in your project root:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for deployment"
   ```
2. Create a new repository on [GitHub](https://github.com/new).
3. Link and push your code:
   ```bash
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```
   *(Note: Thanks to `.gitignore`, your private `.env` file will NEVER be uploaded to GitHub!)*

### Step 2: Deploy on Render
1. Go to [Render Dashboard](https://dashboard.render.com/) and sign in with GitHub.
2. Click **New +** > **Web Service**.
3. Select **Build and deploy from a Git repository** and pick your newly created repository.
4. Fill in the service settings:
   - **Name**: `travel-guide-ai` (or any name you choose)
   - **Region**: Choose the closest region (e.g., Singapore, Frankfurt, Oregon)
   - **Language**: `Python 3`
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --chdir Backend app:app`
   - **Instance Type**: `Free`
5. Scroll down to **Environment Variables** and add:
   - `GEMINI_API_KEY`: *(paste your Gemini API key)*
   - `MURF_API_KEY`: *(paste your Murf API key)*
6. Click **Create Web Service**.
7. Render will build and deploy your app. Once deployed, open your `.onrender.com` link — your Travel Guide UI and AI audio generation are live!

---

## 🚂 Option 2: Deploy on Railway (Alternative Single-Click)

1. Sign in to [Railway](https://railway.app/) using GitHub.
2. Click **New Project** > **Deploy from GitHub repo**.
3. Select your repository.
4. Go to **Variables** tab in Railway and add:
   - `GEMINI_API_KEY`
   - `MURF_API_KEY`
   - `PORT`: `5000`
5. Railway will automatically detect the `Procfile` or `Dockerfile` and deploy the service.

---

## ⚡ Option 3: Decoupled (Frontend on Vercel + Backend on Render)

If you prefer hosting the Frontend on Vercel and Backend on Render:

1. **Deploy Backend on Render**:
   - Follow Step 2 from Option 1.
   - Note down the backend URL (e.g. `https://travel-guide-api.onrender.com`).
2. **Deploy Frontend on Vercel**:
   - Go to [Vercel](https://vercel.com/) and import your GitHub repo.
   - Set **Root Directory** to `Frontend`.
   - Before deploying, in `Frontend/index.html`, add this script in the `<head>`:
     ```html
     <script>
       window.BACKEND_API_URL = "https://travel-guide-api.onrender.com";
     </script>
     ```
   - Click **Deploy**.

---

## 🐳 Option 4: Docker Deployment

To run or deploy with Docker:
```bash
# Build the Docker container
docker build -t travel-guide-app .

# Run the container
docker run -p 5000:5000 \
  -e GEMINI_API_KEY="your_gemini_key" \
  -e MURF_API_KEY="your_murf_key" \
  travel-guide-app
```
Then visit `http://localhost:5000`.

---

## 🧪 Local Testing Before Deploying

To test the fullstack unified server locally:
```bash
python Backend/app.py
```
Open [http://localhost:5000](http://localhost:5000) in your browser.
