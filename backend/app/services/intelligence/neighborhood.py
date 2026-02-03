from app.services.gemini.base_agent import GeminiBaseAgent
from typing import Dict, Any, List
import json

class NeighborhoodAnalyzer(GeminiBaseAgent):
    """
    Analyzes the neighborhood/barrio context to understand:
    - Demographics (students, office workers, families)
    - Time patterns (lunch rush, dinner crowd, late night)
    - Economic level
    - Cultural preferences
    - Competitive dynamics specific to the area
    """
    
    async def analyze_neighborhood(
        self,
        location_data: Dict[str, Any],
        nearby_businesses: List[Dict[str, Any]],
        competitor_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Deep analysis of the neighborhood character.
        
        Uses:
        - Types of nearby businesses (universities, offices, hotels, etc.)
        - Competitor density and types
        - Area characteristics from Google Places
        """
        
        prompt = f"""
You are an urban sociologist and restaurant consultant. Analyze this neighborhood 
to understand WHO lives/works here and HOW they consume.

LOCATION:
{json.dumps(location_data, indent=2)}

NEARBY BUSINESSES (non-restaurant):
{json.dumps(nearby_businesses, indent=2)}

RESTAURANT COMPETITORS:
{json.dumps(competitor_data, indent=2)}

ANALYZE:

1. **Demographic Profile:**
   - Age groups (students, young professionals, families, seniors)
   - Income level (budget, middle, affluent)
   - Cultural/ethnic composition
   - Residential vs commercial area

2. **Daily Patterns:**
   - Morning: Who's here? (commuters, students, residents)
   - Lunch: Office workers? Students? Quick service or sit-down?
   - Evening: Dinner crowd or nightlife?
   - Weekend: Different demographics?

3. **Competitor Landscape:**
   - Is it oversaturated? (too many restaurants)
   - Price tiers represented
   - Cuisine gaps
   - Service model gaps (fast-casual, fine-dining, etc.)

4. **Marketing Implications:**
   - Best times to promote
   - Message tone (formal, casual, trendy)
   - Which platforms? (Instagram for young, Facebook for families)
   - Price sensitivity

5. **Strategic Positioning:**
   - Underserved niches in THIS neighborhood
   - Optimal price point for THIS area
   - Differentiation opportunities

RESPONSE (JSON):
{{
  "neighborhood_type": "university_district|business_district|residential|tourist|mixed",
  "primary_demographics": ["students", "young_professionals"],
  "income_level": "budget|middle|affluent",
  
  "daily_patterns": {{
    "morning_peak": "7-9am: Students grabbing breakfast",
    "lunch_peak": "12-2pm: Office workers, quick service preferred",
    "dinner_peak": "7-10pm: Mix of students and dates",
    "late_night": "10pm-12am: Bar crowd"
  }},
  
  "competitor_analysis": {{
    "saturation_level": "high|medium|low",
    "dominant_cuisines": ["Mexican", "Fast food"],
    "price_gaps": ["Missing affordable healthy options"],
    "service_gaps": ["No late-night sit-down options"]
  }},
  
  "marketing_strategy": {{
    "best_platforms": ["Instagram", "TikTok"],
    "tone": "casual|trendy|sophisticated",
    "best_promotion_times": ["Thursday-Saturday evenings"],
    "price_sensitivity": "high|medium|low",
    "key_selling_points": ["Late night hours", "Student discounts"]
  }},
  
  "positioning_recommendation": {{
    "niche": "Late-night healthy fast-casual for students",
    "optimal_price_point": "$8-12",
    "differentiation": "Only place open past midnight with fresh ingredients"
  }},
  
  "confidence": 0.87
}}
"""
        
        response = await self.generate(prompt, thinking_level="DEEP")
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            analysis = json.loads(response)
        except Exception:
            analysis = {"error": "Failed to parse neighborhood analysis"}
        
        return analysis
