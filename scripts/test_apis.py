import os
import asyncio
import httpx
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load from root .env
load_dotenv()

async def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    # Get model from env or fallback to what we set in config
    model = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
    
    print(f"🤖 Testing Gemini API (Model: {model})...")
    
    if not api_key:
        print("❌ GEMINI_API_KEY is missing.")
        return False
    if "your_" in api_key:
        print("⚠️ GEMINI_API_KEY looks like a placeholder.")
        # Proceeding anyway to confirm failure, or return False immediately
        return False

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents="Reply with 'Operational' if you receive this.",
        )
        print(f"✅ Gemini Response: {response.text.strip()}")
        return True
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        return False

async def test_places():
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    print(f"\n🗺️  Testing Google Places API...")
    
    if not api_key:
        print("❌ GOOGLE_PLACES_API_KEY is missing.")
        return False
    if "your_" in api_key:
        print("⚠️ GOOGLE_PLACES_API_KEY looks like a placeholder.")
        return False

    try:
        # Test 1: Legacy API (used by current backend)
        print("   [1/2] Testing Legacy Places API (maps.googleapis.com)...")
        url_legacy = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        params = {
            "input": "Eiffel Tower",
            "inputtype": "textquery",
            "fields": "place_id,name,formatted_address",
            "key": api_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url_legacy, params=params)
            data = response.json()
            
            if data.get("status") == "OK":
                print(f"   ✅ Legacy API Success: Found '{data['candidates'][0]['name']}'")
                return True
            else:
                print(f"   ❌ Legacy API Failed: {data.get('status')} - {data.get('error_message', '')}")
                
        # Test 2: New Places API (fallback check)
        print("   [2/2] Testing New Places API (places.googleapis.com)...")
        url_new = "https://places.googleapis.com/v1/places:searchText"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress"
        }
        body = {"textQuery": "Eiffel Tower"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url_new, headers=headers, json=body)
            if response.status_code == 200:
                print(f"   ✅ New API Success: Key is valid for Places API (New).")
                return True
            else:
                print(f"   ❌ New API Failed: {response.status_code} - {response.text}")
                return False

    except Exception as e:
        print(f"❌ Places API Connection Failed: {e}")
        return False

async def test_geocoding():
    api_key = os.getenv("GOOGLE_PLACES_API_KEY") # Usually same key
    print(f"\n🌍 Testing Geocoding API...")
    
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": "Eiffel Tower",
        "key": api_key
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()
            
            if data.get("status") == "OK":
                print(f"   ✅ Geocoding Success: Found '{data['results'][0]['formatted_address']}'")
                return True
            else:
                print(f"   ❌ Geocoding Failed: {data.get('status')} - {data.get('error_message', '')}")
                return False
    except Exception as e:
        print(f"   ❌ Geocoding Error: {e}")
        return False

async def main():
    print("=== RestoPilotAI Connectivity Check ===\n")
    g_ok = await test_gemini()
    p_ok = await test_places()
    geo_ok = await test_geocoding()
    
    print("\n" + "="*40)
    if g_ok and p_ok and geo_ok:
        print("🚀 SYSTEM READY: All APIs Operational.")
    else:
        print("⚠️ SYSTEM ISSUES DETECTED:")
        if not g_ok: print("   - Gemini API: FAILED")
        if not p_ok: print("   - Places API: FAILED (Check Legacy vs New)")
        if not geo_ok: print("   - Geocoding API: FAILED (Must enable 'Geocoding API' in Console)")

if __name__ == "__main__":
    asyncio.run(main())
