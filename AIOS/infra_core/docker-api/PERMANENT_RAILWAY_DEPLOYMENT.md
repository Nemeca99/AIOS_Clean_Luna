# Permanent Railway Deployment Guide

## Overview
This guide deploys a complete AI system to Railway:
1. **Ollama Service** - Runs AI models in the cloud
2. **API Proxy** - Converts Ollama to OpenAI-compatible API
3. **Streamlit App** - Connects to the cloud API

## Step 1: Deploy Ollama Service

### 1.1 Create First Railway Project
1. Go to https://railway.app
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your **AIOS repository**
5. Set **Root Directory** to: `docker-api/ollama-railway`
6. Click **"Deploy"**

### 1.2 Configure Ollama Service
- **Service Name**: `aios-ollama`
- **Environment Variables**: None needed (uses default models)
- **Wait for deployment** (5-10 minutes - it downloads models)

### 1.3 Get Ollama Service URL
- Copy the Railway URL (e.g., `https://aios-ollama-production.up.railway.app`)
- Note this URL - you'll need it for the API proxy

## Step 2: Deploy API Proxy

### 2.1 Create Second Railway Project
1. Click **"New Project"** → **"Deploy from GitHub repo"**
2. Select your **AIOS repository**
3. Set **Root Directory** to: `docker-api`
4. **Important**: Update `api_proxy.py` to use the new Ollama proxy

### 2.2 Configure API Proxy Service
- **Service Name**: `aios-api-proxy`
- **Environment Variables**:
  - `OLLAMA_BASE_URL`: `https://aios-ollama-production.up.railway.app` (your Ollama URL)
- Click **"Deploy"**

### 2.3 Get API Proxy URL
- Copy the Railway URL (e.g., `https://aios-api-proxy-production.up.railway.app`)
- This is your final API URL for Streamlit

## Step 3: Update Streamlit App

### 3.1 Update streamlit_app.py
Replace the LM Studio URL with your Railway API proxy URL:

```python
LM_STUDIO_URL = "https://aios-api-proxy-production.up.railway.app/v1/chat/completions"
```

### 3.2 Update Connection Test URL
```python
response = requests.get("https://aios-api-proxy-production.up.railway.app/v1/models", timeout=5)
```

### 3.3 Push Changes
```bash
git add streamlit_app.py
git commit -m "Update Streamlit app to use Railway API proxy"
git push
```

## Step 4: Test the System

1. **Wait for Streamlit Cloud to redeploy** (2-3 minutes)
2. **Go to your Streamlit app**
3. **Navigate to "Live AI Demo" tab**
4. **Test the connection** - should show "✅ Connected to LM Studio"
5. **Try chatting with Luna** - should work!

## Cost Considerations

### Railway Free Tier
- **$5/month credit**
- **500 hours of runtime**
- **1GB RAM per service**
- **Should be enough for development/testing**

### Upgrade Options
- **Pro Plan**: $20/month for more resources
- **Team Plan**: $99/month for production use

## Troubleshooting

### If Ollama Service Fails
- Check Railway logs for download issues
- Models are large (1-4GB each)
- May need to restart deployment

### If API Proxy Fails
- Verify `OLLAMA_BASE_URL` environment variable
- Check that Ollama service is running
- Test Ollama URL directly in browser

### If Streamlit Can't Connect
- Verify API proxy URL is correct
- Check Railway service status
- Test API proxy health endpoint

## Benefits of This Setup

✅ **Completely cloud-based** - No local dependencies  
✅ **Permanent** - No need for local services  
✅ **Scalable** - Can handle multiple users  
✅ **Professional** - Real production deployment  
✅ **Cost-effective** - Railway free tier covers development  

## Next Steps

Once working, you can:
1. **Add more models** to Ollama
2. **Scale up resources** on Railway
3. **Add authentication** to the API
4. **Monitor usage** and costs
5. **Deploy to production** with custom domain
