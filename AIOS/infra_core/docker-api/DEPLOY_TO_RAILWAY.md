# Deploy API Proxy to Railway

## Quick Deployment Steps

1. **Go to Railway.app** and sign in with GitHub
2. **Click "New Project"** → **"Deploy from GitHub repo"**
3. **Select your AIOS repository**
4. **Set the root directory** to: `docker-api`
5. **Add environment variable:**
   - Key: `LM_STUDIO_BASE_URL`
   - Value: `http://192.168.1.21:1234` (your local LM Studio IP)
6. **Deploy!**

## Important Notes

⚠️ **This won't work directly** because Railway can't access your local LM Studio.

## Alternative Solutions

### Option 1: Use a Public LM Studio Instance
- Deploy LM Studio to a cloud service (Railway, Render, etc.)
- Update the `LM_STUDIO_BASE_URL` to point to the cloud instance

### Option 2: Use ngrok (Temporary)
- Install ngrok: https://ngrok.com/
- Run: `ngrok http 1234` (while LM Studio is running)
- Copy the public URL (e.g., `https://abc123.ngrok.io`)
- Update `LM_STUDIO_BASE_URL` to the ngrok URL

### Option 3: Use Cloudflare Tunnel (Free)
- Install cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/
- Run: `cloudflared tunnel --url http://localhost:1234`
- Copy the public URL and update `LM_STUDIO_BASE_URL`

## After Deployment

Once deployed, Railway will give you a URL like: `https://your-app-name.railway.app`

Update your Streamlit app's `LM_STUDIO_URL` to:
```python
LM_STUDIO_URL = "https://your-app-name.railway.app/v1/chat/completions"
```
