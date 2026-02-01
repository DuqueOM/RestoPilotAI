from app.services.gemini.base_agent import GeminiBaseAgent
from typing import List, Dict, Any
import json
from datetime import datetime
import base64
from google.genai import types

class SocialAestheticsAnalyzer(GeminiBaseAgent):
    """
    Compares visual aesthetics of social media presence.
    Provides actionable feedback on photography, color schemes, composition.
    """

    async def predict_instagram_performance(
        self,
        dish_photo: bytes,
        restaurant_category: str,
        posting_time: datetime
    ) -> Dict[str, Any]:
        """
        Predice el performance de una foto en Instagram.
        
        ANÁLISIS MULTIMODAL:
        - Composición visual
        - Iluminación
        - Apetitosidad del plato
        - Contexto de posting (hora, día)
        - Tendencias actuales (grounded search)
        """
        
        prompt = f"""
        Analiza esta foto de plato de restaurante y predice su performance en Instagram.
        
        CONTEXTO:
        - Categoría del restaurante: {restaurant_category}
        - Hora de publicación planeada: {posting_time.strftime('%H:%M, %A')}
        
        INVESTIGACIÓN (usa Google Search):
        1. Busca las tendencias actuales de food photography en Instagram
        2. Identifica qué estilos están generando más engagement este mes
        3. Revisa ejemplos de posts exitosos en la categoría {restaurant_category}
        
        ANÁLISIS DE LA FOTO:
        Evalúa en escala 0-10:
        1. COMPOSICIÓN
           - Regla de tercios
           - Balance visual
           - Punto focal claro
        
        2. ILUMINACIÓN
           - Calidad de luz
           - Sombras apropiadas
           - Brillo general
        
        3. APETITOSIDAD
           - Colores vibrantes
           - Textura visible
           - Presentación del plato
        
        4. "INSTAGRAMABILIDAD"
           - Estética trending
           - Elementos visuales únicos
           - Potencial de compartir
        
        5. TIMING
           - ¿Es buena hora para este tipo de contenido?
           - ¿Qué día de la semana funciona mejor?
        
        PREDICCIÓN:
        Devuelve JSON con:
        {{
            "predicted_performance": {{
                "likes_estimate": "rango estimado de likes",
                "engagement_rate": "% estimado",
                "virality_score": 0-10,
                "confidence": 0-1
            }},
            "scores": {{
                "composition": 0-10,
                "lighting": 0-10,
                "appetizing": 0-10,
                "instagramability": 0-10,
                "timing": 0-10
            }},
            "improvements": [
                {{
                    "issue": "problema detectado",
                    "suggestion": "cómo mejorarlo",
                    "impact": "alto|medio|bajo"
                }}
            ],
            "optimal_posting_time": "mejor hora/día para publicar",
            "trending_hashtags": ["#hashtag1", "#hashtag2", ...],
            "comparison_to_trends": "cómo se compara con tendencias actuales"
        }}
        """
        
        try:
            # We use the client directly to enable Google Search tool
            response = self.client.models.generate_content(
                model=self.model_name, # Inherited from GeminiBaseAgent
                contents=[
                    types.Content(parts=[
                        types.Part(text=prompt),
                        types.Part(inline_data=types.Blob(
                            mime_type="image/jpeg",
                            data=dish_photo
                        ))
                    ])
                ],
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    response_mime_type="application/json",
                    temperature=0.7
                )
            )
            
            return json.loads(response.text)
            
        except Exception as e:
            # Fallback to standard generation if tool/client fails or image issue
            return {"error": str(e)}

    async def compare_visual_aesthetics(
        self,
        user_photos: List[bytes],
        competitor_photos: Dict[str, List[bytes]],
        context: str
    ) -> Dict[str, Any]:
        """
        Deep visual comparison of social media aesthetics.
        
        Args:
            user_photos: User's Instagram/social photos
            competitor_photos: Dict of {competitor_name: [photos]}
            context: Business context (e.g., "casual taquería")
        """
        
        # Combine all photos for batch analysis
        all_photos = []
        
        # User photos
        for i, photo in enumerate(user_photos[:10]):  # Limit to 10
            all_photos.append(photo)
        
        # Competitor photos
        for comp_name, photos in competitor_photos.items():
            for i, photo in enumerate(photos[:5]):  # 5 per competitor
                all_photos.append(photo)
        
        prompt = f"""
You are a professional food photographer and social media consultant.
Analyze these restaurant photos for visual aesthetics and engagement potential.

CONTEXT: {context}

PHOTOS PROVIDED:
- User's photos: {len(user_photos)} images
- Competitor photos: {sum(len(p) for p in competitor_photos.values())} images

ANALYZE:

1. **Lighting Quality:**
   - Natural vs artificial light
   - Brightness and exposure
   - Shadows and highlights
   - Warmth/coolness of tones

2. **Composition:**
   - Rule of thirds application
   - Framing and angles
   - Use of negative space
   - Focus and depth of field

3. **Color Palette:**
   - Dominant colors
   - Color harmony
   - Saturation levels
   - Brand consistency

4. **Subject Presentation:**
   - Food plating quality
   - Portion visibility
   - Garnish and details
   - Context (table setting, background)

5. **Emotional Impact:**
   - Appetizing factor (1-10)
   - Mood evoked
   - Brand personality communicated

6. **Competitive Comparison:**
   - How does user compare to competitors?
   - What are competitors doing better?
   - What's your unique visual strength?

7. **Actionable Recommendations:**
   - Specific changes to lighting
   - Composition improvements
   - Color adjustments
   - Props/styling suggestions

RESPONSE (JSON):
{{
  "user_aesthetic_score": {{
    "overall": 6.5,
    "lighting": 5.0,
    "composition": 7.0,
    "color": 6.0,
    "presentation": 7.5,
    "emotional_impact": 6.0
  }},
  
  "competitor_benchmark": {{
    "Competitor A": {{
      "overall": 8.2,
      "strengths": ["Warm, rustic lighting", "Consistent earth tones"],
      "weaknesses": ["Repetitive angles"]
    }}
  }},
  
  "comparative_analysis": {{
    "you_do_better": ["Close-up details", "Variety of dishes shown"],
    "they_do_better": ["Lighting consistency", "Brand color scheme"],
    "competitive_gap": 1.7
  }},
  
  "actionable_feedback": [
    {{
      "issue": "Your photos are too dark (avg brightness: 40/100)",
      "solution": "Shoot near windows during daytime or add ring light",
      "priority": "high",
      "expected_impact": "+2 points in lighting score"
    }},
    {{
      "issue": "Inconsistent color temperature (some warm, some cool)",
      "solution": "Use consistent lighting or apply warm filter in editing",
      "priority": "medium",
      "expected_impact": "+1.5 points in cohesion"
    }},
    {{
      "issue": "No establishing shots (restaurant ambiance)",
      "solution": "Add 30% ambiance/lifestyle shots to your feed",
      "priority": "medium",
      "expected_impact": "Better storytelling, +15% engagement"
    }}
  ],
  
  "quick_wins": [
    "Increase brightness by 20% in all photos",
    "Apply a warm filter for brand consistency",
    "Shoot from 45-degree angle instead of straight-on"
  ],
  
  "style_recommendation": "warm-rustic-casual",
  "reference_accounts": ["@comp_best_visuals"],
  
  "confidence": 0.88
}}
"""
        
        response = await self.generate(
            prompt, 
            images=all_photos,
            thinking_level="DEEP"
        )
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            analysis = json.loads(response)
        except:
            analysis = {"error": "Failed to parse aesthetic analysis"}
        
        return analysis
