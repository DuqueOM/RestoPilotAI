
import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.gemini.creative_autopilot import CreativeAutopilotAgent

# Load environment variables
load_dotenv()

async def test_full_creative_autopilot():
    """Verify all CreativeAutopilotAgent capabilities."""
    
    print("🚀 Initializing CreativeAutopilotAgent...")
    agent = CreativeAutopilotAgent()
    
    # Mock Concept
    concept = {
        "headline": "Sabor Supremo",
        "main_message": "La mejor hamburguesa de la ciudad.",
        "visual_description": "A juicy gourmet burger with melting cheese, crispy bacon, and fresh lettuce on a brioche bun. Professional food photography, dark background, dramatic lighting.",
        "photo_style": "Dark mood food photography",
        "key_elements": "Burger, cheese, bacon, brioche bun"
    }
    
    brand_guidelines = {
        "colors": "Gold, Black, and Red",
        "logo_path": None # Skipping logo for this test to avoid file issues
    }

    print("\n---------------------------------------------------------")
    print("🧪 1. Testing Generation of All 4 Asset Types")
    print("---------------------------------------------------------")
    
    try:
        assets = await agent._generate_visual_assets(concept, brand_guidelines)
        print(f"✅ Generated {len(assets)} assets")
        for asset in assets:
            print(f"  - {asset.get('type')} ({asset.get('format')}): {'✅ Image Data Present' if asset.get('image_data') else '❌ No Image Data'} - Reason: {asset.get('reasoning')[:50] if asset.get('reasoning') else 'N/A'}...")
            
            # Save generic asset for inspection
            if asset.get('image_data'):
                fname = f"test_asset_{asset.get('type')}.jpg"
                with open(fname, "wb") as f:
                    f.write(asset.get('image_data'))
                print(f"    Saved to {fname}")
                
    except Exception as e:
        print(f"❌ Asset generation failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n---------------------------------------------------------")
    print("🧪 2. Testing A/B Variants")
    print("---------------------------------------------------------")
    
    try:
        # Using the first asset from previous step or a mock one
        base_asset = assets[0] if 'assets' in locals() and assets else {"concept": "Sabor Supremo"}
        
        variants = await agent._generate_ab_variants(base_asset, strategy={"objective": "Sales"})
        print(f"✅ Generated {len(variants)} variants")
        for variant in variants:
            print(f"  - Variant: {variant.get('variant_type')} - {variant.get('type')}")
            if variant.get('image_data'):
                fname = f"test_variant_{variant.get('variant_type')}.jpg"
                with open(fname, "wb") as f:
                    f.write(variant.get('image_data'))
                print(f"    Saved to {fname}")

    except Exception as e:
        print(f"❌ A/B Variant generation failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n---------------------------------------------------------")
    print("🧪 3. Testing Visual Localization")
    print("---------------------------------------------------------")
    
    target_languages = ["en", "fr"]
    
    try:
        # Use assets from step 1
        input_assets = assets[:1] if 'assets' in locals() and assets else []
        if not input_assets:
            print("⚠️ No input assets available for localization test. Skipping.")
        else:
            print(f"Localizing {len(input_assets)} assets to {target_languages}...")
            localized = await agent.localize_campaign(input_assets, target_languages)
            
            for lang, lang_assets in localized.items():
                print(f"  ✅ Language: {lang} - Generated {len(lang_assets)} assets")
                for asset in lang_assets:
                    print(f"    - Headline: {asset.get('concept')}")
                    if asset.get('image_data'):
                        fname = f"test_localized_{lang}_{asset.get('type')}.jpg"
                        with open(fname, "wb") as f:
                            f.write(asset.get('image_data'))
                        print(f"      Saved to {fname}")

    except Exception as e:
        print(f"❌ Localization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_creative_autopilot())
