import asyncio
import os
import sys
from todo_backend.config.setting import settings

# Ensure using env key if present
API_KEY = os.environ.get("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
if not API_KEY:
    print("ERROR: GEMINI_API_KEY not set in env or settings.")
    sys.exit(1)

try:
    # import inside try to get clearer error if package missing or shadowed
    from google import genai
except Exception as e:
    print("Import error for google.genai:", e)
    raise

async def list_models_async(client):
    try:
        models = await client.aio.models.list()
        return models
    except Exception:
        return None

def list_models_sync(client):
    try:
        return client.models.list()
    except Exception:
        return None

async def main():
    client = genai.Client(api_key=API_KEY)
    models = await list_models_async(client)
    if models is None:
        models = list_models_sync(client)
    if not models:
        print("No models returned (empty). Check API key, network, or account permissions.")
        return

    print("=== Available Models ===")
    for m in models:
        name = getattr(m, "name", getattr(m, "id", str(m)))
        # Try to show supported generation methods if available
        supported = getattr(m, "supported_generation_methods", None) or getattr(m, "capabilities", None)
        print(f"- {name}")
        if supported:
            print("   supported:", supported)
        # Quick check string match for multimodal
        if "generateContent" in str(supported):
            print("   -> SUPPORTS generateContent")
    # filter common candidates
    candidates = [getattr(m, "name", getattr(m, "id", str(m))) for m in models if "gemini-1.5" in getattr(m, "name", getattr(m,"id",""))]
    print("\nMultimodal candidates (contains 'gemini-1.5'):", candidates)

if __name__ == "__main__":
    asyncio.run(main())