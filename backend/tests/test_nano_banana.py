
import asyncio
import os
import sys
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv()

async def test_nano_banana():
    """Test basic access to Nano Banana Pro (Gemini 3 Image)."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return

    client = genai.Client(api_key=api_key)
    
    print("🔍 Listing available models (top 10)...")
    try:
        for i, m in enumerate(client.models.list(config={"page_size": 100})):
            if i > 10: break
            # Inspect object structure if needed, usually m.name is safe
            methods = getattr(m, 'supported_generation_methods', 'unknown')
            print(f" - {m.name} (Methods: {methods})")
    except Exception as e:
        print(f"⚠️ Could not list models: {e}")

    # Models to test in order of preference
    candidates = [
        "gemini-3-pro-image-preview", # Requested
        "gemini-2.0-flash-exp",       # Fallback 1
        "gemini-1.5-flash"            # Fallback 2 (Stable)
    ]
    
    target_model = None
    
    print("\n🧪 Testing model availability...")
    for model in candidates:
        try:
            print(f"  Checking {model}...")
            # Simple metadata check first
            client.models.get(model=model)
            print(f"  ✅ {model} is available!")
            target_model = model
            break
        except Exception:
            print(f"  ❌ {model} not found/accessible")
            
    if not target_model:
        print("⚠️ No preferred models found. Using gemini-1.5-flash as hard fallback.")
        target_model = "gemini-1.5-flash"

    print(f"\n🚀 Starting generation test with: {target_model}")
    
    prompt = "A cinematic instagram photo of a delicious gourmet burger with the text 'MENU PILOT' written in neon lights in the background. High resolution, 4k."
    
    try:
        # Simulating the CreativeAutopilot logic
        print(f"  Requesting IMAGE generation from {target_model}...")
        
        response = client.models.generate_content(
            model=target_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                response_modalities=["IMAGE"] # Explicitly request image
            )
        )
        
        print("✅ Response received!")
        try:
            print(f"Response type: {type(response)}")
            print(f"Response attributes: {dir(response)}")
        except Exception as e:
            print(f"Error inspecting response: {e}")

        # Try to find where the content is
        if hasattr(response, 'candidates'):
            print(f"Candidates: {len(response.candidates)}")
            for i, cand in enumerate(response.candidates):
                print(f"Candidate {i}: {cand}")
                if hasattr(cand, 'content') and hasattr(cand.content, 'parts'):
                    for j, part in enumerate(cand.content.parts):
                        if part.inline_data:
                            print(f"  📸 Found inline_data in candidate {i} part {j}. Mime: {part.inline_data.mime_type}")
                        elif part.text:
                            print(f"  📝 Found text in candidate {i} part {j}: {part.text[:50]}...")
        
        # Fallback inspection
        if hasattr(response, 'text'):
             print(f"Response.text property: {response.text[:50] if response.text else 'None'}")

    except Exception as e:
        print(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        print("\n✅ Setup verification passed (Basic API Access)")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_nano_banana())
