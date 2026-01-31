from app.services.gemini.base_agent import GeminiBaseAgent
from typing import Dict, Any, Optional
import json

class ContextProcessor(GeminiBaseAgent):
    """
    Processes text and audio context provided by the user.
    Integrates this context into ALL analyses for personalization.
    """
    
    async def process_audio_context(
        self,
        audio_file: bytes,
        context_type: str  # "history", "values", "challenges", etc.
    ) -> str:
        """
        Transcribe and extract insights from audio context.
        
        Uses Gemini's multimodal audio capabilities.
        """
        
        prompt = f"""
Transcribe this audio and extract key insights.

This is the restaurant owner talking about their business {context_type}.

Provide:
1. Full transcription
2. Key points extracted
3. Emotional tone
4. Important details for marketing/strategy

Format as JSON.
"""
        
        response = await self.generate(
            prompt,
            images=[audio_file],  # Gemini handles audio via same param in our base agent adapter
            thinking_level="STANDARD"
        )
        
        return response
    
    async def integrate_context_into_analysis(
        self,
        business_context: Dict[str, Any],
        analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Integrate user-provided context into analysis insights.
        
        Makes recommendations PERSONAL and CONTEXTUAL.
        """
        
        prompt = f"""
You are enhancing a restaurant analysis with deep business context.

BUSINESS CONTEXT (from owner):
History: {business_context.get('history_text', 'N/A')}
Values: {business_context.get('values_text', 'N/A')}
USPs: {business_context.get('unique_selling_points_text', 'N/A')}
Target Audience: {business_context.get('target_audience_text', 'N/A')}
Challenges: {business_context.get('challenges_text', 'N/A')}
Goals: {business_context.get('goals_text', 'N/A')}

CURRENT ANALYSIS (without context):
{json.dumps(analysis_data, indent=2, default=str)}

TASK:
Enhance the analysis by integrating the owner's context.

For example:
- If owner says "family recipes from grandmother", highlight authenticity in campaigns
- If owner mentions "struggling with Gen Z customers", tailor social media recommendations
- If owner's goal is "expand to 3 locations", recommend scalability in operations

PROVIDE:
1. Enhanced BCG insights (referencing their USPs)
2. Personalized campaign messages (using their voice/values)
3. Pricing strategy aligned with their goals
4. Competitive positioning that plays to their stated strengths

RESPONSE (JSON):
{{
  "context_integrated_insights": {{
    "bcg": ["..."],
    "pricing": ["..."],
    "positioning": ["..."]
  }},
  "personalized_campaigns": [
    {{
      "title": "...",
      "copy": "Uses owner's authentic family story",
      "why": "Aligns with stated value of authenticity"
    }}
  ],
  "strategic_alignment": {{
    "goals_addressed": ["expansion goal addressed by..."],
    "challenges_tackled": ["Gen Z engagement via TikTok strategy"]
  }}
}}
"""
        
        response = await self.generate(prompt, thinking_level="DEEP")
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            enhanced_analysis = json.loads(response)
        except:
            enhanced_analysis = {"error": "Context integration failed"}
        
        return enhanced_analysis
