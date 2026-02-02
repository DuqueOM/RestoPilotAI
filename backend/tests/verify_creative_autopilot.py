
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

async def verify_creative_autopilot():
    """Verify CreativeAutopilotAgent generation capabilities."""
    
    print("🚀 Initializing CreativeAutopilotAgent...")
    agent = CreativeAutopilotAgent()
    
    print(f"  - Reasoning Model: {agent.reasoning_model}")
    print(f"  - Image Model: {agent.image_model}")
    
    # Mock data
    restaurant_name = "El Sabor Auténtico"
    dish_data = {
        "name": "Tacos al Pastor Gourmet",
        "description": "Tacos tradicionales con carne marinada 24 horas, piña asada y salsa de aguacate.",
        "price": 15.00,
        "category": "Main Course"
    }
    bcg_class = "star"
    
    print("\n🧪 Testing _generate_instagram_post (Direct Call)...")
    
    concept = {
        "headline": "Sabor que Enamora",
        "main_message": "Descubre el verdadero sabor de México en cada mordida.",
        "visual_description": "Close-up of three delicious tacos al pastor on a rustic wooden board, garnished with fresh cilantro, onions, and roasted pineapple. Warm, inviting lighting highlighting the juicy meat.",
        "photo_style": "Warm and rustic food photography",
        "key_elements": "Tacos, pineapple, salsa, rustic wood"
    }
    
    try:
        result = await agent._generate_instagram_post(concept)
        
        print("✅ Generation Result:")
        print(f"  - Type: {result.get('type')}")
        print(f"  - Format: {result.get('format')}")
        
        image_data = result.get('image_data')
        if image_data:
            print(f"  - Image Data: {len(image_data)} bytes")
            # Save to file for visual inspection
            output_path = "test_generated_taco.jpg"
            with open(output_path, "wb") as f:
                f.write(image_data)
            print(f"  - Saved to: {output_path}")
        else:
            print("  ⚠️ No image data returned.")
            
        if result.get('reasoning'):
            print(f"  - Reasoning: {result.get('reasoning')[:100]}...")
            
    except Exception as e:
        print(f"❌ _generate_instagram_post failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_creative_autopilot())
