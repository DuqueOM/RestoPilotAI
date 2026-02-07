#!/usr/bin/env python3
"""
Test script to verify Gemini API is working correctly.
This will help diagnose if the API key is valid and if Gemini can process images.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

import base64

from google import genai
from google.genai import types


def test_api_key():
    """Test if API key is configured and valid."""
    print("=" * 60)
    print("TEST 1: API Key Configuration")
    print("=" * 60)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return False

    print(f"✅ API Key found: {api_key[:20]}...{api_key[-4:]}")
    return True


def test_simple_text_generation():
    """Test basic text generation with Gemini."""
    print("\n" + "=" * 60)
    print("TEST 2: Simple Text Generation")
    print("=" * 60)

    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents="Say 'Hello from Gemini!' in exactly those words.",
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=100,
            ),
        )

        print(f"✅ Response received: {response.text[:100]}")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_json_structured_output():
    """Test if Gemini can return structured JSON."""
    print("\n" + "=" * 60)
    print("TEST 3: JSON Structured Output")
    print("=" * 60)

    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        prompt = """Return a JSON object with exactly this structure:
{
  "items": [
    {"name": "Test Item", "price": 100}
  ],
  "confidence": 0.9
}

Return ONLY the JSON, no other text."""

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=500,
            ),
        )

        print(f"✅ Response: {response.text[:200]}")

        # Try to parse as JSON
        import json

        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        parsed = json.loads(text.strip())
        print(f"✅ Successfully parsed JSON with {len(parsed.get('items', []))} items")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_image_analysis():
    """Test if Gemini can analyze an image."""
    print("\n" + "=" * 60)
    print("TEST 4: Image Analysis (Multimodal)")
    print("=" * 60)

    # Find a test image
    test_images = [
        "backend/data/uploads/07f9bf0b-dc66-4689-a4b3-4996f635a321/menu_Platos Fuertes_page1.png",
        "backend/data/uploads/test123/menu_Platos Fuertes_page1.png",
        "docs/Platos Fuertes.pdf",
    ]

    image_path = None
    for path in test_images:
        full_path = Path(__file__).parent / path
        if full_path.exists() and full_path.suffix == ".png":
            image_path = full_path
            break

    if not image_path:
        print("⚠️  No test image found, skipping image test")
        return None

    print(f"Using test image: {image_path}")

    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        # Read and encode image
        image_data = image_path.read_bytes()
        image_base64 = base64.b64encode(image_data).decode()

        prompt = """Describe what you see in this image in one sentence."""

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                types.Content(
                    parts=[
                        types.Part(text=prompt),
                        types.Part(
                            inline_data=types.Blob(
                                mime_type="image/png",
                                data=base64.b64decode(image_base64),
                            )
                        ),
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=500,
            ),
        )

        print(f"✅ Image analysis response: {response.text[:200]}")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_menu_extraction():
    """Test menu extraction with the exact prompt used in the app."""
    print("\n" + "=" * 60)
    print("TEST 5: Menu Extraction (Real Scenario)")
    print("=" * 60)

    # Find a test image
    test_images = [
        "backend/data/uploads/07f9bf0b-dc66-4689-a4b3-4996f635a321/menu_Platos Fuertes_page1.png",
        "backend/data/uploads/test123/menu_Platos Fuertes_page1.png",
    ]

    image_path = None
    for path in test_images:
        full_path = Path(__file__).parent / path
        if full_path.exists():
            image_path = full_path
            break

    if not image_path:
        print("⚠️  No test image found, skipping menu extraction test")
        return None

    print(f"Using test image: {image_path}")

    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        # Read and encode image
        image_data = image_path.read_bytes()
        image_base64 = base64.b64encode(image_data).decode()

        prompt = """Analyze this restaurant menu image and extract ALL menu items you can see.

IMPORTANT: You MUST respond with valid JSON in this exact format:
{
  "items": [
    {
      "name": "Item name exactly as written",
      "price": 12000,
      "description": "Item description if available",
      "category": "category name"
    }
  ],
  "confidence": 0.85
}

For each item, identify:
- Name (exactly as written on the menu)
- Price (as a number, remove currency symbols)
- Description (if available, otherwise use empty string)
- Category (appetizers, mains, desserts, drinks, etc.)

Extract EVERY visible item on the menu. If you see text but it's unclear, make your best interpretation.
If the menu is in Spanish, keep the original Spanish names.

Return ONLY the JSON, no other text."""

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                types.Content(
                    parts=[
                        types.Part(text=prompt),
                        types.Part(
                            inline_data=types.Blob(
                                mime_type="image/png",
                                data=base64.b64decode(image_base64),
                            )
                        ),
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=4096,
            ),
        )

        print(f"Raw response (first 500 chars):\n{response.text[:500]}\n")

        # Try to parse as JSON
        import json

        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        parsed = json.loads(text.strip())
        items_count = len(parsed.get("items", []))

        if items_count > 0:
            print(f"✅ Successfully extracted {items_count} menu items!")
            print("\nFirst 3 items:")
            for item in parsed["items"][:3]:
                print(f"  - {item.get('name', 'N/A')}: ${item.get('price', 0)}")
            return True
        else:
            print("⚠️  Gemini returned 0 items. This is the problem!")
            print(f"Full response:\n{response.text}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n🔍 GEMINI API DIAGNOSTIC TOOL")
    print("=" * 60)

    # Load .env file
    from dotenv import load_dotenv

    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded .env from {env_path}")
    else:
        print(f"⚠️  No .env file found at {env_path}")

    results = []

    # Run tests
    results.append(("API Key", test_api_key()))
    results.append(("Text Generation", test_simple_text_generation()))
    results.append(("JSON Output", test_json_structured_output()))
    results.append(("Image Analysis", test_image_analysis()))
    results.append(("Menu Extraction", test_menu_extraction()))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for test_name, result in results:
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⚠️  SKIP"
        print(f"{status} - {test_name}")

    passed = sum(1 for _, r in results if r is True)
    total = sum(1 for _, r in results if r is not None)

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n✅ All tests passed! API is working correctly.")
        print("The problem might be in the application code or image processing.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        print("Common issues:")
        print("  1. Invalid or expired API key")
        print("  2. API quota exceeded")
        print("  3. Network/firewall issues")
        print("  4. Wrong model name or permissions")


if __name__ == "__main__":
    main()
