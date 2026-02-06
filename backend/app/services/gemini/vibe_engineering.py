from typing import Dict, List
import json
from google import genai
from google.genai import types
from loguru import logger
from app.core.config import get_settings

class VibeEngineeringAgent:
    """
    Implements the hackathon 'Vibe Engineering' pattern.
    
    Features:
    - Output auto-verification
    - Iterative improvement loops
    - Autonomous testing
    - Quality validation without human intervention
    """
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.gemini_api_key
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-3-flash-preview"
        self.max_iterations = 3
        self.quality_threshold = 0.85
    
    async def verify_and_improve_analysis(
        self,
        analysis_type: str,
        analysis_result: Dict,
        source_data: Dict,
        auto_improve: bool = True
    ) -> Dict:
        """
        Verifies the quality of an analysis and improves it iteratively.
        
        AUTONOMOUS LOOP:
        1. Verify initial analysis quality
        2. If quality_score < threshold:
           a. Identify specific issues
           b. Regenerate analysis with corrections
           c. Go back to step 1
        3. Continue until reaching threshold or max_iterations
        """
        import time
        from datetime import datetime
        
        start_time = time.time()
        iteration = 0
        current_analysis = analysis_result
        verification_history = []
        improvement_iterations = []
        
        while iteration < self.max_iterations:
            iter_start = time.time()
            
            # AUTONOMOUS VERIFICATION
            verification = await self._autonomous_verify(
                analysis_type,
                current_analysis,
                source_data
            )
            
            verification_history.append(verification)
            quality_score = verification.get('quality_score', 0)
            
            # If quality is sufficient, stop
            if quality_score >= self.quality_threshold:
                break
            
            # If auto-improve is disabled, stop (return with current verification)
            if not auto_improve:
                break
            
            # If this is the last iteration, do not attempt an improvement
            # to avoid wasting tokens without a subsequent re-verification
            if iteration == self.max_iterations - 1:
                break

            # AUTONOMOUS IMPROVEMENT
            identified_issues = verification.get('identified_issues', [])
            improved_analysis = await self._autonomous_improve(
                analysis_type,
                current_analysis,
                identified_issues,
                source_data
            )
            
            # Record improvement metrics
            iter_duration = (time.time() - iter_start) * 1000
            improvement_iterations.append({
                "iteration": iteration + 1,
                "timestamp": datetime.now().isoformat(),
                "quality_before": quality_score,
                "quality_after": 0, # Will be updated in next loop or final check
                "issues_fixed": [i.get('issue', 'Issue') for i in identified_issues],
                "duration_ms": iter_duration
            })
            
            current_analysis = improved_analysis
            iteration += 1
        
        # Update final quality score in last improvement iteration if we verified it
        if improvement_iterations and verification_history:
             last_quality = verification_history[-1].get('quality_score', 0)
             # This is an approximation as we verified 'current_analysis' which IS 'improved_analysis' from previous step
             improvement_iterations[-1]['quality_after'] = last_quality

        total_duration = (time.time() - start_time) * 1000
        
        return {
            "final_analysis": current_analysis,
            "verification_history": verification_history,
            "iterations_required": iteration + 1,
            "quality_achieved": verification_history[-1].get('quality_score', 0) if verification_history else 0,
            "auto_improved": auto_improve and iteration > 0,
            "improvement_iterations": improvement_iterations,
            "total_duration_ms": total_duration
        }
    
    async def _autonomous_verify(
        self,
        analysis_type: str,
        analysis: Dict,
        source_data: Dict
    ) -> Dict:
        """
        Autonomous quality verification using Gemini 3.
        
        The model acts as a "critical reviewer" and evaluates:
        - Logical consistency
        - Factual accuracy
        - Completeness
        - Practical applicability
        """
        
        # Safe serialization for prompt
        def default_serializer(obj):
            return str(obj)

        verification_prompt = f"""
        You are an EXPERT AUDITOR evaluating the quality of a restaurant analysis.
        
        ANALYSIS TYPE: {analysis_type}
        
        ORIGINAL DATA:
        {json.dumps(source_data, indent=2, default=default_serializer)}
        
        ANALYSIS TO VERIFY:
        {json.dumps(analysis, indent=2, default=default_serializer)}
        
        Your task is to evaluate the QUALITY of the analysis across multiple dimensions:
        
        1. FACTUAL ACCURACY (0-1):
           - Are numbers and calculations correct?
           - Do conclusions logically follow from the data?
        
        2. COMPLETENESS (0-1):
           - Were all relevant aspects analyzed?
           - Are there any important insights missing?
        
        3. APPLICABILITY (0-1):
           - Are the recommendations actionable?
           - Does it make sense for a real restaurant owner?
        
        4. CLARITY (0-1):
           - Is the explanation understandable?
           - Are technical terms well explained?
        
        Return a JSON with the following structure:
        {{
            "quality_score": float (average of the 4 dimensions),
            "precision_score": float,
            "completeness_score": float,
            "applicability_score": float,
            "clarity_score": float,
            "identified_issues": [
                {{
                    "issue": "description of the problem",
                    "severity": "high|medium|low",
                    "category": "precision|completeness|applicability|clarity",
                    "suggestion": "how to fix it"
                }}
            ],
            "strengths": ["strength 1", "strength 2", ...],
            "overall_assessment": "executive summary of 2-3 lines"
        }}
        
        BE RIGOROUS AND CRITICAL. A mediocre analysis should receive a score < 0.7.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=verification_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3  # Low temperature for consistency
                )
            )
            
            result = json.loads(response.text)
            
            # Ensure result is a dict, not a list
            if isinstance(result, list):
                logger.warning(f"Verification returned a list instead of dict: {result}")
                return {"quality_score": 0, "error": "Invalid response format (list instead of dict)"}
            
            return result
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return {"quality_score": 0, "error": str(e)}
    
    async def _autonomous_improve(
        self,
        analysis_type: str,
        current_analysis: Dict,
        identified_issues: List[Dict],
        source_data: Dict
    ) -> Dict:
        """
        Autonomous improvement of the analysis based on identified issues.
        """
        
        # Prioritize issues by severity
        high_priority = [i for i in identified_issues if i.get('severity') == 'high']
        medium_priority = [i for i in identified_issues if i.get('severity') == 'medium']
        
        # Safe serialization
        def default_serializer(obj):
            return str(obj)

        improvement_prompt = f"""
        You are a SENIOR ANALYST correcting a previous analysis.
        
        ORIGINAL ANALYSIS:
        {json.dumps(current_analysis, indent=2, default=default_serializer)}
        
        IDENTIFIED ISSUES (HIGH PRIORITY):
        {json.dumps(high_priority, indent=2)}
        
        IDENTIFIED ISSUES (MEDIUM PRIORITY):
        {json.dumps(medium_priority, indent=2)}
        
        ORIGINAL REFERENCE DATA:
        {json.dumps(source_data, indent=2, default=default_serializer)}
        
        Your task is to REGENERATE the analysis correcting ALL identified issues.
        
        Guidelines:
        1. Maintain the correct aspects of the original analysis
        2. SPECIFICALLY correct each listed issue
        3. If information is missing, incorporate it
        4. If there are calculation errors, fix them
        5. If recommendations are not actionable, make them more concrete
        
        IMPORTANT: 
        - Return the complete improved analysis, not just the changes
        - Maintain the same JSON structure as the original analysis
        - Add an "improvements_made" field listing what you fixed
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=improvement_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.5  # Higher creativity for improvements
                )
            )
            
            result = json.loads(response.text)
            
            # Ensure result is a dict, not a list
            if isinstance(result, list):
                logger.warning("Improvement returned a list instead of dict, using current analysis")
                return current_analysis
            
            return result
        except Exception as e:
            logger.error(f"Improvement failed: {e}")
            return current_analysis
    
    async def verify_campaign_assets(
        self,
        campaign_assets: List[Dict],
        brand_guidelines: Dict,
        auto_improve: bool = True
    ) -> Dict:
        """
        Verifies the quality of generated visual assets.
        
        AUTONOMOUS CHECKS:
        - Is the text legible?
        - Do the colors respect the brand?
        - Is the composition professional?
        - Is the message clear?
        """
        
        verified_assets = []
        
        for asset in campaign_assets:
            # Skip assets without image data
            if not asset.get('image_data'):
                verified_assets.append(asset)
                continue

            # Visual verification using Gemini Vision
            verification = await self._verify_visual_asset(
                asset,
                brand_guidelines
            )
            
            # If quality is low and auto_improve is enabled
            if verification.get('quality_score', 0) < self.quality_threshold and auto_improve:
                # Improve the asset (Placeholder - requires re-generation logic which might be complex)
                # For now, we just tag it. In a full implementation, this would call CreativeAutopilot to regenerate.
                # Since we don't have direct access to regenerate here without circular deps or complex passing,
                # we'll flag it.
                
                # improved = await self._improve_visual_asset(asset, verification['issues'])
                # verified_assets.append(improved)
                
                verified_assets.append({
                    **asset,
                    "verification": verification,
                    "needs_improvement": True
                })
            else:
                verified_assets.append({
                    **asset,
                    "verification": verification
                })
        
        # Avoid division by zero
        count = len(verified_assets)
        avg_quality = sum(a.get('verification', {}).get('quality_score', 0) for a in verified_assets) / count if count > 0 else 0
        
        return {
            "verified_assets": verified_assets,
            "overall_quality": avg_quality
        }
    
    async def _verify_visual_asset(
        self,
        asset: Dict,
        brand_guidelines: Dict
    ) -> Dict:
        """
        Verify a visual asset using Gemini Vision.
        """
        
        prompt = f"""
        You are a CREATIVE DIRECTOR evaluating a marketing asset.
        
        BRAND GUIDELINES:
        {json.dumps(brand_guidelines, indent=2)}
        
        Evaluate this image on the following dimensions:
        
        1. TEXT LEGIBILITY (0-1):
           - Is the text completely legible?
           - Are there spelling errors?
        
        2. BRAND ADHERENCE (0-1):
           - Does it respect the color palette?
           - Is the style consistent with the brand?
        
        3. TECHNICAL QUALITY (0-1):
           - Is the resolution adequate?
           - Is the composition professional?
        
        4. MESSAGE EFFECTIVENESS (0-1):
           - Is the message clear immediately?
           - Does it generate a desire to act?
        
        Return JSON:
        {{
            "quality_score": float,
            "text_legibility": float,
            "brand_adherence": float,
            "technical_quality": float,
            "message_effectiveness": float,
            "issues": [
                {{"issue": "...", "severity": "high|medium|low", "suggestion": "..."}}
            ],
            "assessment": "2-3 line assessment"
        }}
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Content(
                        parts=[
                            types.Part(text=prompt),
                            types.Part(inline_data=types.Blob(
                                mime_type="image/jpeg",
                                data=asset['image_data']
                            ))
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            result = json.loads(response.text)
            
            # Ensure result is a dict, not a list
            if isinstance(result, list):
                logger.warning("Visual verification returned a list instead of dict")
                return {"quality_score": 0, "error": "Invalid response format (list instead of dict)"}
            
            return result
        except Exception as e:
            logger.error(f"Visual verification failed: {e}")
            return {"quality_score": 0, "error": str(e)}
