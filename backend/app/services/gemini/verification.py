from app.services.gemini.base_agent import GeminiBaseAgent
from app.core.logging_config import logger
from typing import Dict, Any, List
import json
from dataclasses import dataclass, field
from enum import Enum

class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    NEEDS_REVISION = "needs_revision"
    REJECTED = "rejected"

@dataclass
class VerificationCheck:
    check_name: str
    passed: bool
    score: float
    feedback: str

@dataclass
class VerificationResult:
    status: VerificationStatus
    overall_score: float
    checks: List[VerificationCheck]
    final_recommendation: str
    iterations_used: int = 0
    improvements_made: List[str] = field(default_factory=list)

class VerificationAgent(GeminiBaseAgent):
    """
    Autonomous agent that verifies analysis quality and data consistency.
    Prevents hallucinations and logical errors.
    """
    
    async def verify_analysis(
        self,
        analysis_data: Dict[str, Any],
        thinking_level: str = "STANDARD",
        auto_improve: bool = False
    ) -> VerificationResult:
        """
        Verify the complete analysis package (BCG, Predictions, Campaigns).
        """
        prompt = f"""
        You are a Chief Strategy Officer auditing a restaurant analysis report.
        
        ANALYSIS DATA:
        {json.dumps(analysis_data, indent=2, default=str)[:10000]} # Truncate if too large
        
        Verify the following dimensions:
        1. **Completeness**: Are all required sections (BCG, Predictions, Campaigns) present and populated?
        2. **Consistency**: Do the campaigns align with the BCG classification? (e.g. Star products getting investment)
        3. **Viability**: Are the sales predictions realistic given the context?
        4. **Actionability**: Are the recommendations specific and executable?
        
        Provide a structured verification report.
        
        RESPONSE JSON FORMAT:
        {{
            "status": "verified" | "needs_revision" | "rejected",
            "overall_score": 0.9,
            "final_recommendation": "Ready for implementation",
            "checks": [
                {{
                    "name": "Strategy Alignment",
                    "passed": true,
                    "score": 0.95,
                    "feedback": "Campaigns perfectly match BCG strategy."
                }},
                {{
                    "name": "Data Completeness",
                    "passed": true,
                    "score": 1.0,
                    "feedback": "All sections populated."
                }}
            ],
            "improvements_made": [] 
        }}
        """
        
        response = await self.generate(prompt, thinking_level=thinking_level)
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
                
            data = json.loads(response)
            
            checks = [
                VerificationCheck(
                    check_name=c["name"],
                    passed=c["passed"],
                    score=c["score"],
                    feedback=c["feedback"]
                ) for c in data.get("checks", [])
            ]
            
            return VerificationResult(
                status=VerificationStatus(data.get("status", "needs_revision")),
                overall_score=data.get("overall_score", 0.0),
                checks=checks,
                final_recommendation=data.get("final_recommendation", ""),
                iterations_used=1, # Mock for single pass
                improvements_made=data.get("improvements_made", [])
            )
            
        except Exception as e:
            logger.error(f"Verification parsing failed: {e}")
            # Fallback result
            return VerificationResult(
                status=VerificationStatus.NEEDS_REVISION,
                overall_score=0.0,
                checks=[VerificationCheck("Parsing", False, 0.0, f"Error: {str(e)}")],
                final_recommendation="Verification failed due to technical error."
            )

    async def verify_competitor_data(
        self, 
        competitor_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verify competitor data for consistency and quality.
        
        Checks:
        1. Price inflation over time
        2. Data source conflicts
        3. Logical inconsistencies
        4. Data completeness
        """
        
        prompt = f"""
You are a data verification specialist. Analyze this competitor data for inconsistencies, 
hallucinations, and data quality issues.

COMPETITOR DATA:
{json.dumps(competitor_data, indent=2, default=str)}

VERIFY THE FOLLOWING:

1. **Price Consistency:**
   - If multiple price data points exist from different time periods, calculate inflation rate
   - Flag if prices decreased (unlikely unless business struggling)
   - Identify outlier prices that don't match pattern

2. **Data Source Conflicts:**
   - If Google Places says "$$$" but scraped menu shows $5 items, FLAG inconsistency
   - Cross-check ratings from multiple sources
   - Validate address consistency

3. **Logical Errors:**
   - Can't have 500 reviews but 0 rating
   - Distance can't be negative
   - Can't be open 25 hours/day
   - Menu items should have reasonable prices

4. **Data Quality Scores:**
   - Rate each competitor's data completeness (0-1)
   - Identify which fields are missing
   - Suggest which competitors need re-scraping

5. **Temporal Analysis:**
   - If menu from 2023 and menu from 2025, calculate % price changes
   - Detect market trends (are ALL competitors raising prices?)

RESPONSE FORMAT (JSON):
{{
  "overall_quality_score": 0.85,
  "issues_found": [
    {{
      "competitor": "Taco Shop X",
      "severity": "high|medium|low",
      "issue": "Price data from 2023 vs 2025 shows 40% inflation",
      "recommendation": "Accept but flag as market trend"
    }}
  ],
  "data_quality_by_competitor": {{
    "Competitor 1": 0.9,
    "Competitor 2": 0.6
  }},
  "market_trends_detected": [
    "Average price increase of 25% across all competitors in last 2 years"
  ],
  "confidence_score": 0.92,
  "verified": true
}}
"""
        
        response = await self.generate(prompt, thinking_level="DEEP")
        
        try:
            # Clean response if it contains markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
                
            verification_result = json.loads(response)
        except Exception:
            # Fallback if JSON parsing fails
            verification_result = {
                "overall_quality_score": 0.5,
                "issues_found": [{"issue": "Failed to parse verification response"}],
                "verified": False
            }
        
        logger.info(
            "verification_completed",
            quality_score=verification_result.get("overall_quality_score"),
            issues_count=len(verification_result.get("issues_found", []))
        )
        
        return verification_result
    
    async def verify_analysis_logic(
        self,
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify the logic of final analysis and recommendations.
        
        Checks:
        1. BCG classification makes sense
        2. Campaigns align with BCG strategy
        3. Pricing recommendations are reasonable
        4. No contradictory insights
        """
        
        prompt = f"""
You are a business strategy auditor. Review this restaurant analysis for logical consistency.

ANALYSIS RESULTS:
{json.dumps(analysis_results, indent=2, default=str)}

VERIFY:

1. **BCG Logic:**
   - Stars should have high growth + high share
   - Cash Cows should have low growth + high share
   - Question Marks should have high growth + low share
   - Dogs should have low growth + low share
   - FLAG any misclassifications

2. **Campaign Alignment:**
   - Star campaigns should focus on growth/momentum
   - Cash Cow campaigns should maximize profit
   - Question Mark campaigns should test/invest
   - Dog campaigns should pivot or sunset
   - FLAG campaigns that don't match strategy

3. **Pricing Recommendations:**
   - Can't recommend raising prices if sentiment is negative
   - Can't recommend lowering if already cheapest in area
   - Must consider competitor pricing
   - FLAG illogical pricing advice

4. **Contradiction Detection:**
   - Can't say "best presentation" but score 3/10
   - Can't say "underpriced" if already most expensive
   - Can't recommend "more photos" if social media is active
   
5. **Data Sufficiency:**
   - Were recommendations based on enough data?
   - FLAG recommendations with low confidence

RESPONSE (JSON):
{{
  "logic_verified": true,
  "contradictions_found": [],
  "confidence_by_section": {{
    "bcg": 0.95,
    "campaigns": 0.88,
    "pricing": 0.75
  }},
  "recommendations_quality": "high|medium|low",
  "needs_revision": false,
  "revision_suggestions": []
}}
"""
        
        response = await self.generate(prompt, thinking_level="EXHAUSTIVE")
        
        try:
            # Clean response if it contains markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
                
            verification = json.loads(response)
        except Exception:
            verification = {"logic_verified": False, "error": "Parse failed"}
        
        return verification

# Alias for backward compatibility
GeminiVerificationAgent = VerificationAgent
