from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import json

app = FastAPI(title="AIOS Ollama API Proxy", version="1.0.0")

# Configure CORS to allow requests from Streamlit Cloud
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Ollama URL - this should be accessible from where this Docker container runs
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama-service:11434")

@app.get("/health")
async def health_check():
    """Health check endpoint for the proxy."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json()
        return {
            "status": "ok", 
            "ollama_reachable": True, 
            "ollama_url": OLLAMA_BASE_URL,
            "models": [model.get("name", "unknown") for model in models.get("models", [])]
        }
    except requests.exceptions.RequestException as e:
        return {"status": "ok", "ollama_reachable": False, "ollama_url": OLLAMA_BASE_URL, "error": str(e)}

@app.get("/v1/models")
async def get_models():
    """Get available models from Ollama."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        response.raise_for_status()
        ollama_models = response.json()
        
        # Convert Ollama format to OpenAI format
        openai_models = {
            "object": "list",
            "data": []
        }
        
        for model in ollama_models.get("models", []):
            openai_models["data"].append({
                "id": model.get("name", "unknown"),
                "object": "model",
                "owned_by": "ollama",
                "created": int(model.get("modified_at", 0)),
                "permission": []
            })
        
        return openai_models
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """Handle chat completions by converting OpenAI format to Ollama format."""
    try:
        # Get the request body
        body = await request.json()
        
        # Convert OpenAI format to Ollama format
        ollama_payload = {
            "model": body.get("model", "llama3.2:1b-instruct"),
            "messages": body.get("messages", []),
            "stream": False,
            "options": {
                "temperature": body.get("temperature", 0.7),
                "top_p": body.get("top_p", 0.9),
                "max_tokens": body.get("max_tokens", 1000)
            }
        }
        
        # Send to Ollama
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat", 
            json=ollama_payload, 
            timeout=60
        )
        response.raise_for_status()
        ollama_response = response.json()
        
        # Convert Ollama response back to OpenAI format
        openai_response = {
            "id": f"chatcmpl-{hash(str(ollama_response))}",
            "object": "chat.completion",
            "created": int(ollama_response.get("created_at", 0)),
            "model": ollama_payload["model"],
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": ollama_response.get("message", {}).get("content", "")
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,  # Ollama doesn't provide token counts
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
        
        return JSONResponse(content=openai_response)
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.api_route("/v1/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_ollama(path: str, request: Request):
    """Proxies other requests to Ollama."""
    target_url = f"{OLLAMA_BASE_URL}/api/{path}"
    headers = {k: v for k, v in request.headers.items() if k.lower() not in ["host", "content-length"]}

    try:
        if request.method == "POST":
            json_data = await request.json()
            response = requests.post(target_url, json=json_data, headers=headers, timeout=60)
        elif request.method == "GET":
            response = requests.get(target_url, headers=headers, timeout=60)
        else:
            raise HTTPException(status_code=405, detail="Method not allowed")

        response.raise_for_status()
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
