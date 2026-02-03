"""
Advanced Reasoning Agent - TOP 1% Implementation.

Features that set us apart:
- Visible chain-of-thought reasoning (transparency)
- Multi-agent debate pattern (reduce bias)
- Uncertainty quantification (honest about limitations)
- Data quality assessment (garbage in, garbage out awareness)
- Audience-targeted executive summaries
"""

import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from loguru import logger
from pydantic import BaseModel, Field

from app.services.gemini.enhanced_agent import (
    EnhancedGeminiAgent,
    ThinkingLevel,
    ThoughtTrace
)
from app.core.config import GeminiModel


# ==================== Enums and Schemas ====================

class ConfidenceLevel(str, Enum):
    """Confidence levels for uncertainty quantification."""
    VERY_LOW = "very_low"      # < 0.4 - High uncertainty
    LOW = "low"                # 0.4-0.6 - Moderate uncertainty
    MEDIUM = "medium"          # 0.6-0.8 - Reasonable confidence
    HIGH = "high"              # 0.8-0.9 - High confidence
    VERY_HIGH = "very_high"    # > 0.9 - Very high confidence


class ConsensusLevel(str, Enum):
    """Consensus level across multiple perspectives."""
    UNANIMOUS = "unanimous"    # All perspectives agree
    STRONG = "strong"          # 75%+ agreement
    MODERATE = "moderate"      # 50-75% agreement
    WEAK = "weak"              # 25-50% agreement
    SPLIT = "split"            # < 25% agreement


class BCGCategory(str, Enum):
    """BCG Matrix categories."""
    STAR = "star"
    CASH_COW = "cash_cow"
    QUESTION_MARK = "question_mark"
    DOG = "dog"


class ProductClassification(BaseModel):
    """Individual product BCG classification."""
    product_name: str
    category: BCGCategory
    growth_rate: float
    relative_market_share: float
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    assumptions: List[str] = Field(default_factory=list)
    alternative_classification: Optional[BCGCategory] = None
    alternative_reasoning: Optional[str] = None


class DataQualityAssessment(BaseModel):
    """Assessment of input data quality."""
    completeness: float = Field(ge=0.0, le=1.0)
    consistency: float = Field(ge=0.0, le=1.0)
    recency: float = Field(ge=0.0, le=1.0)
    sample_size_adequacy: float = Field(ge=0.0, le=1.0)
    overall_quality: float = Field(ge=0.0, le=1.0)
    missing_fields: List[str] = Field(default_factory=list)
    data_gaps: List[str] = Field(default_factory=list)
    quality_issues: List[str] = Field(default_factory=list)
    improvement_recommendations: List[str] = Field(default_factory=list)


class StrategicRecommendation(BaseModel):
    """Strategic recommendation with metadata."""
    category: BCGCategory
    recommendations: List[str]
    consensus_level: ConsensusLevel
    confidence: float = Field(ge=0.0, le=1.0)
    key_assumptions: List[str] = Field(default_factory=list)
    alternative_views: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)


class BCGAnalysisSchema(BaseModel):
    """Comprehensive BCG analysis output."""
    products: List[ProductClassification]
    strategic_recommendations: Dict[str, StrategicRecommendation]
    market_positioning: Dict[str, Any]
    confidence_by_category: Dict[str, float]
    data_quality_assessment: DataQualityAssessment
    overall_confidence: float = Field(ge=0.0, le=1.0)
    assumptions_made: List[str] = Field(default_factory=list)
    alternative_interpretations: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    reasoning_chain: List[str] = Field(default_factory=list)


class PerspectiveAnalysis(BaseModel):
    """Analysis from a specific perspective."""
    perspective_name: str
    disagreements: List[str] = Field(default_factory=list)
    alternative_recommendations: Dict[str, List[str]] = Field(default_factory=dict)
    risks_identified: List[str] = Field(default_factory=list)
    opportunities_identified: List[str] = Field(default_factory=list)
    confidence_adjustments: Dict[str, float] = Field(default_factory=dict)


# ==================== Advanced Reasoning Agent ====================

class AdvancedReasoningAgent(EnhancedGeminiAgent):
    """
    🧠 ADVANCED REASONING AGENT - TOP 1%
    
    Unique features:
    - Transparent chain-of-thought (user sees the reasoning)
    - Multi-agent debate (reduces single-perspective bias)
    - Uncertainty quantification (honest about confidence)
    - Data quality awareness (GIGO prevention)
    - Audience-targeted communication
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            model=GeminiModel.FLASH_PREVIEW,
            enable_grounding=True,
            enable_cache=True,
            **kwargs
        )
        logger.info("advanced_reasoning_agent_initialized")
    
    # ==================== BCG ANALYSIS ====================
    
    async def analyse_bcg_strategy(
        self,
        sales_data: List[Dict[str, Any]],
        menu_data: List[Dict[str, Any]],
        market_context: Optional[Dict[str, Any]] = None,
        enable_multi_perspective: bool = True,
        show_reasoning: bool = True
    ) -> BCGAnalysisSchema:
        """
        🎯 BCG MATRIX WITH TRANSPARENT REASONING
        
        Shows step-by-step logic to user for full transparency.
        
        Args:
            sales_data: Historical sales data
            menu_data: Menu items with metadata
            market_context: Market information (optional)
            enable_multi_perspective: Run multi-agent debate
            show_reasoning: Include visible reasoning chain
            
        Returns:
            Comprehensive BCG analysis with confidence scores
        """
        
        logger.info(
            "bcg_analysis_started",
            products=len(sales_data),
            multi_perspective=enable_multi_perspective
        )
        
        # Step 1: Assess data quality
        data_quality = await self._assess_data_quality(sales_data, menu_data)
        
        logger.info(
            "data_quality_assessed",
            overall_quality=data_quality.overall_quality
        )
        
        # Step 2: Primary analysis with visible reasoning
        primary_analysis = await self._bcg_single_perspective(
            sales_data,
            menu_data,
            market_context,
            show_reasoning
        )
        
        # Step 3: Multi-perspective validation (if enabled)
        alternative_perspectives = []
        if enable_multi_perspective:
            alternative_perspectives = await self._bcg_multi_agent_debate(
                sales_data,
                menu_data,
                market_context,
                primary_analysis
            )
            
            logger.info(
                "multi_perspective_complete",
                perspectives=len(alternative_perspectives)
            )
        
        # Step 4: Synthesize final recommendation
        final_analysis = await self._synthesize_bcg_recommendation(
            primary_analysis,
            alternative_perspectives,
            data_quality
        )
        
        logger.info(
            "bcg_analysis_complete",
            overall_confidence=final_analysis.overall_confidence
        )
        
        return final_analysis
    
    async def _assess_data_quality(
        self,
        sales_data: List[Dict[str, Any]],
        menu_data: List[Dict[str, Any]]
    ) -> DataQualityAssessment:
        """
        Assess data quality before analysis.
        
        Critical for honest uncertainty quantification.
        """
        
        # Get sample fields
        sales_fields = list(sales_data[0].keys()) if sales_data else []
        menu_fields = list(menu_data[0].keys()) if menu_data else []
        
        prompt = f"""You are a data quality analyst assessing restaurant data for BCG analysis.

SALES DATA:
- Records: {len(sales_data)}
- Fields: {sales_fields}
- Sample: {json.dumps(sales_data[:3], indent=2) if sales_data else "No data"}

MENU DATA:
- Records: {len(menu_data)}
- Fields: {menu_fields}
- Sample: {json.dumps(menu_data[:3], indent=2) if menu_data else "No data"}

EVALUATE (score 0.0-1.0 for each):

1. **Completeness**: Are all required fields present?
   Required for BCG: product_name, units_sold, price, date
   Score: [0-1]

2. **Consistency**: Are there internal contradictions?
   Check: price consistency, naming consistency, date formats
   Score: [0-1]

3. **Recency**: How current is the data?
   Ideal: Last 30-90 days
   Score: [0-1]

4. **Sample Size**: Sufficient for statistical significance?
   Minimum: 30 products, 90 days of data
   Score: [0-1]

5. **Overall Quality**: Weighted average
   Score: [0-1]

IDENTIFY:
- Missing critical fields
- Data gaps (missing dates, products, etc.)
- Quality issues (outliers, errors, inconsistencies)
- Recommendations to improve quality

RETURN ONLY VALID JSON:
{{
    "completeness": float,
    "consistency": float,
    "recency": float,
    "sample_size_adequacy": float,
    "overall_quality": float,
    "missing_fields": ["string"],
    "data_gaps": ["string"],
    "quality_issues": ["string"],
    "improvement_recommendations": ["string"]
}}
"""
        
        result = await self.generate(
            prompt=prompt,
            thinking_level=ThinkingLevel.STANDARD,
            enable_grounding=False
        )
        
        try:
            return DataQualityAssessment(**result["data"])
        except Exception as e:
            logger.error("data_quality_validation_failed", error=str(e))
            return DataQualityAssessment(
                completeness=0.5,
                consistency=0.5,
                recency=0.5,
                sample_size_adequacy=0.5,
                overall_quality=0.5
            )
    
    async def _bcg_single_perspective(
        self,
        sales_data: List[Dict[str, Any]],
        menu_data: List[Dict[str, Any]],
        market_context: Optional[Dict[str, Any]],
        show_reasoning: bool
    ) -> Dict[str, Any]:
        """
        Primary BCG analysis with VISIBLE chain-of-thought.
        """
        
        # Prepare data summary
        sales_summary = json.dumps(sales_data[:10], indent=2) if len(sales_data) <= 10 else \
                       f"{json.dumps(sales_data[:5], indent=2)}\n... ({len(sales_data)} total products)"
        
        menu_summary = json.dumps(menu_data[:10], indent=2) if len(menu_data) <= 10 else \
                      f"{json.dumps(menu_data[:5], indent=2)}\n... ({len(menu_data)} total items)"
        
        prompt = f"""You are a McKinsey-level strategy consultant specializing in restaurant BCG analysis.

SALES DATA:
{sales_summary}

MENU DATA:
{menu_summary}

MARKET CONTEXT:
{json.dumps(market_context, indent=2) if market_context else "Limited market context available"}

TASK: Perform BCG Matrix Classification with TRANSPARENT REASONING

{"**SHOW YOUR REASONING STEP-BY-STEP** (this will be visible to the user):" if show_reasoning else ""}

STEP 1: Calculate Market Growth Rate
- Methodology: [Explain how you'll calculate growth]
- Data used: [Which fields and time periods]
- Calculation: [Show the math]
- Result: X% growth rate
- Confidence: [0.0-1.0]
- Assumptions: [List all assumptions made]

STEP 2: Calculate Relative Market Share
- Approach: [How to determine market leader and relative position]
- Challenges: [Data limitations encountered]
- Calculation: [Show the math]
- Result: [Relative market share values]
- Confidence: [0.0-1.0]
- Assumptions: [List assumptions]

STEP 3: Classify Each Product
For EACH product, provide:
- Product name
- Growth rate: [%]
- Relative market share: [value]
- BCG Category: star | cash_cow | question_mark | dog
- Confidence: [0.0-1.0]
- Reasoning: [1-2 sentences explaining classification]
- Key assumption: [Main assumption for this classification]
- Alternative classification: [If confidence < 0.8, what else could it be?]

STEP 4: Strategic Recommendations
For each category (Stars, Cash Cows, Question Marks, Dogs):
- Specific actions (not generic advice)
- Expected impact
- Resource requirements
- Timeline
- Confidence in recommendation: [0.0-1.0]

STEP 5: Uncertainty & Limitations
CRITICAL - Be honest about:
- What data is missing or incomplete?
- What assumptions did you make?
- What could change your recommendation?
- What alternative interpretations exist?
- What's your overall confidence? [0.0-1.0]

RETURN AS VALID JSON with this structure:
{{
    "reasoning_chain": ["step 1 summary", "step 2 summary", ...],
    "products": [
        {{
            "product_name": "string",
            "category": "star|cash_cow|question_mark|dog",
            "growth_rate": float,
            "relative_market_share": float,
            "confidence": float,
            "reasoning": "string",
            "assumptions": ["string"],
            "alternative_classification": "category or null",
            "alternative_reasoning": "string or null"
        }}
    ],
    "strategic_recommendations": {{
        "stars": ["specific action 1", "specific action 2"],
        "cash_cows": ["specific action 1", "specific action 2"],
        "question_marks": ["specific action 1", "specific action 2"],
        "dogs": ["specific action 1", "specific action 2"]
    }},
    "market_positioning": {{
        "overall_market_growth": float,
        "competitive_intensity": "low|medium|high",
        "market_maturity": "emerging|growth|mature|declining"
    }},
    "confidence_by_category": {{
        "stars": float,
        "cash_cows": float,
        "question_marks": float,
        "dogs": float
    }},
    "assumptions_made": ["assumption 1", "assumption 2"],
    "alternative_interpretations": ["alternative view 1", "alternative view 2"],
    "limitations": ["limitation 1", "limitation 2"],
    "overall_confidence": float
}}
"""
        
        result = await self.generate(
            prompt=prompt,
            thinking_level=ThinkingLevel.EXHAUSTIVE,
            enable_thought_trace=True,
            enable_grounding=market_context is None  # Use grounding if no market context
        )
        
        return result
    
    async def _bcg_multi_agent_debate(
        self,
        sales_data: List[Dict[str, Any]],
        menu_data: List[Dict[str, Any]],
        market_context: Optional[Dict[str, Any]],
        primary_analysis: Dict[str, Any]
    ) -> List[PerspectiveAnalysis]:
        """
        🔥 MULTI-AGENT DEBATE PATTERN
        
        Simulate different expert perspectives to reduce bias.
        This is a unique feature that competitors don't have.
        """
        
        perspectives = [
            {
                "role": "Aggressive Growth Strategist",
                "bias": "Favor investing heavily in Question Marks for market share capture",
                "context": "Believes in aggressive expansion and market dominance at any cost",
                "risk_tolerance": "high"
            },
            {
                "role": "Conservative CFO",
                "bias": "Favor Cash Cows and maximize short-term profitability",
                "context": "Focused on financial stability, cash flow, and risk minimization",
                "risk_tolerance": "low"
            },
            {
                "role": "Customer-Centric CMO",
                "bias": "Favor products with best customer reviews regardless of current financials",
                "context": "Believes brand reputation and customer satisfaction trump short-term profits",
                "risk_tolerance": "medium"
            }
        ]
        
        alternative_analyses = []
        
        for perspective in perspectives:
            prompt = f"""You are a **{perspective['role']}** reviewing a BCG analysis.

YOUR PERSPECTIVE: {perspective['context']}
YOUR BIAS: {perspective['bias']}
YOUR RISK TOLERANCE: {perspective['risk_tolerance']}

PRIMARY BCG ANALYSIS TO REVIEW:
{json.dumps(primary_analysis['data'], indent=2)}

TASK: Critique and provide alternative recommendations from YOUR UNIQUE PERSPECTIVE.

1. **Disagreements**: What do you DISAGREE with in this analysis?
   - Which classifications seem wrong from your perspective?
   - Which recommendations are too conservative/aggressive?
   - What risks are being ignored?

2. **Alternative Recommendations**: What would YOU recommend differently?
   For each category (stars, cash_cows, question_marks, dogs):
   - Your alternative strategy
   - Why it's better from your perspective
   - What the primary analysis misses

3. **Risks Identified**: What risks does the primary analysis overlook?
   - Financial risks
   - Market risks
   - Execution risks
   - Opportunity costs

4. **Opportunities Identified**: What opportunities are being missed?
   - Untapped potential
   - Market gaps
   - Competitive advantages

5. **Confidence Adjustments**: For each category, how would you adjust confidence?
   {{
       "stars": +0.1 or -0.2 (your adjustment),
       "cash_cows": ...,
       ...
   }}

BE SPECIFIC. Challenge assumptions. Provide concrete alternatives.

RETURN ONLY VALID JSON:
{{
    "perspective_name": "{perspective['role']}",
    "disagreements": ["specific disagreement 1", "specific disagreement 2"],
    "alternative_recommendations": {{
        "stars": ["alternative action 1", "alternative action 2"],
        "cash_cows": ["alternative action 1", "alternative action 2"],
        "question_marks": ["alternative action 1", "alternative action 2"],
        "dogs": ["alternative action 1", "alternative action 2"]
    }},
    "risks_identified": ["risk 1", "risk 2"],
    "opportunities_identified": ["opportunity 1", "opportunity 2"],
    "confidence_adjustments": {{
        "stars": float,
        "cash_cows": float,
        "question_marks": float,
        "dogs": float
    }}
}}
"""
            
            result = await self.generate(
                prompt=prompt,
                thinking_level=ThinkingLevel.DEEP,
                enable_grounding=False
            )
            
            try:
                analysis = PerspectiveAnalysis(**result["data"])
                alternative_analyses.append(analysis)
            except Exception as e:
                logger.error(
                    "perspective_analysis_validation_failed",
                    perspective=perspective['role'],
                    error=str(e)
                )
        
        return alternative_analyses
    
    async def _synthesize_bcg_recommendation(
        self,
        primary: Dict[str, Any],
        alternatives: List[PerspectiveAnalysis],
        data_quality: DataQualityAssessment
    ) -> BCGAnalysisSchema:
        """
        Synthesize final recommendation considering all perspectives.
        """
        
        alternatives_json = [alt.model_dump() for alt in alternatives]
        
        prompt = f"""You are synthesizing BCG recommendations from multiple expert perspectives.

PRIMARY ANALYSIS:
{json.dumps(primary['data'], indent=2)}

ALTERNATIVE PERSPECTIVES ({len(alternatives)} experts):
{json.dumps(alternatives_json, indent=2)}

DATA QUALITY ASSESSMENT:
{json.dumps(data_quality.model_dump(), indent=2)}

TASK: Create FINAL recommendation that:
1. Considers ALL perspectives (primary + alternatives)
2. Identifies consensus areas
3. Flags areas of disagreement
4. Quantifies uncertainty for each recommendation
5. Provides confidence scores per category
6. Acknowledges limitations

For EACH strategic recommendation, state:
- Consensus level: unanimous | strong | moderate | weak | split
- Confidence score: [0.0-1.0]
- Key assumptions
- Alternative interpretations (if any)
- Risks to consider

ADJUST confidence scores based on:
- Data quality (lower quality = lower confidence)
- Perspective agreement (more disagreement = lower confidence)
- Assumptions required (more assumptions = lower confidence)

RETURN AS VALID JSON matching BCGAnalysisSchema structure.
Include reasoning_chain showing how you synthesized the perspectives.
"""
        
        result = await self.generate(
            prompt=prompt,
            thinking_level=ThinkingLevel.EXHAUSTIVE,
            enable_grounding=False
        )
        
        try:
            # Parse and validate
            data = result["data"]
            
            # Convert strategic recommendations to proper format
            strategic_recs = {}
            for category, recs in data.get("strategic_recommendations", {}).items():
                if isinstance(recs, list):
                    # Simple list format, convert to StrategicRecommendation
                    strategic_recs[category] = StrategicRecommendation(
                        category=BCGCategory(category.lower()),
                        recommendations=recs,
                        consensus_level=ConsensusLevel.MODERATE,
                        confidence=data.get("confidence_by_category", {}).get(category, 0.7),
                        key_assumptions=data.get("assumptions_made", [])[:2],
                        alternative_views=data.get("alternative_interpretations", [])[:2]
                    )
                else:
                    # Already in proper format
                    strategic_recs[category] = StrategicRecommendation(**recs)
            
            data["strategic_recommendations"] = strategic_recs
            data["data_quality_assessment"] = data_quality
            
            return BCGAnalysisSchema(**data)
        except Exception as e:
            logger.error("bcg_synthesis_validation_failed", error=str(e))
            # Return minimal valid schema
            return BCGAnalysisSchema(
                products=[],
                strategic_recommendations={},
                market_positioning={},
                confidence_by_category={},
                data_quality_assessment=data_quality,
                overall_confidence=0.5
            )
    
    # ==================== EXECUTIVE SUMMARIES ====================
    
    async def generate_executive_summary(
        self,
        full_analysis: Dict[str, Any],
        audience: str = "restaurant_owner",
        max_words: int = 500
    ) -> str:
        """
        Generate audience-targeted executive summary.
        
        Tailored to audience's sophistication level and priorities.
        """
        
        audience_profiles = {
            "restaurant_owner": {
                "description": "Non-technical, action-oriented, wants ROI and practical steps",
                "priorities": ["profitability", "customer satisfaction", "operational simplicity"],
                "avoid": ["jargon", "complex metrics", "theoretical concepts"]
            },
            "investor": {
                "description": "Financial metrics focus, risk-aware, growth potential oriented",
                "priorities": ["ROI", "market share", "scalability", "exit strategy"],
                "avoid": ["operational details", "day-to-day tactics"]
            },
            "consultant": {
                "description": "Methodology-focused, wants data sources, limitations, rigor",
                "priorities": ["analytical rigor", "data quality", "assumptions", "alternatives"],
                "avoid": ["oversimplification", "unsubstantiated claims"]
            },
            "operations_manager": {
                "description": "Tactical, implementable steps, resource requirements",
                "priorities": ["actionability", "resource needs", "timeline", "team impact"],
                "avoid": ["high-level strategy", "financial jargon"]
            }
        }
        
        profile = audience_profiles.get(audience, audience_profiles["restaurant_owner"])
        
        prompt = f"""You are writing an executive summary for a **{audience}**.

AUDIENCE PROFILE:
- Description: {profile['description']}
- Priorities: {', '.join(profile['priorities'])}
- Avoid: {', '.join(profile['avoid'])}

FULL ANALYSIS:
{json.dumps(full_analysis, indent=2)}

CONSTRAINTS:
- Maximum {max_words} words
- Use simple, clear language
- Focus on actionable insights
- Include 2-3 key numbers/metrics
- End with clear next steps

STRUCTURE:
1. **Situation** (1 sentence): Current state in plain language
2. **Key Finding** (1-2 sentences): Most important insight
3. **Recommendation** (2-3 sentences): What to do and why
4. **Expected Impact** (1 sentence): What will change/improve
5. **Next Steps** (3-5 bullet points): Specific, actionable items

TONE:
- Conversational, NOT corporate jargon
- Confident but honest about limitations
- Specific, not vague
- Action-oriented

Example of GOOD vs BAD:
❌ "Leverage synergies to optimize portfolio allocation"
✅ "Focus your marketing budget on your 3 best-selling tacos"

❌ "Implement strategic repositioning initiatives"
✅ "Stop promoting the burrito - it's losing money"

WRITE THE SUMMARY:
"""
        
        result = await self.generate(
            prompt=prompt,
            thinking_level=ThinkingLevel.STANDARD,
            enable_grounding=False
        )
        
        summary = result["data"].get("text", str(result["data"]))
        
        # Ensure it's within word limit
        words = summary.split()
        if len(words) > max_words:
            summary = " ".join(words[:max_words]) + "..."
        
        return summary
    
    # ==================== COMPETITIVE ANALYSIS ====================
    
    async def analyse_competitive_position(
        self,
        your_data: Dict[str, Any],
        competitor_data: List[Dict[str, Any]],
        market_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze competitive position with multi-perspective reasoning.
        """
        
        prompt = f"""You are analyzing competitive positioning for a restaurant.

YOUR RESTAURANT:
{json.dumps(your_data, indent=2)}

COMPETITORS ({len(competitor_data)}):
{json.dumps(competitor_data, indent=2)}

MARKET CONTEXT:
{json.dumps(market_context, indent=2) if market_context else "Limited context"}

ANALYSIS FRAMEWORK:

1. **Competitive Positioning**:
   - Where do you rank overall? (1-{len(competitor_data) + 1})
   - Strengths vs competitors
   - Weaknesses vs competitors
   - Unique differentiators

2. **Market Gaps**:
   - Underserved customer segments
   - Unmet needs
   - White space opportunities

3. **Threat Assessment**:
   - Which competitors are most dangerous?
   - Why are they threats?
   - How to defend against them?

4. **Strategic Recommendations**:
   - Compete head-on or differentiate?
   - Which competitors to target?
   - Which to avoid?

5. **Confidence & Uncertainty**:
   - Overall confidence: [0.0-1.0]
   - Key assumptions
   - Data limitations
   - Alternative interpretations

RETURN AS JSON with detailed competitive analysis.
"""
        
        result = await self.generate(
            prompt=prompt,
            thinking_level=ThinkingLevel.DEEP,
            enable_grounding=True,  # Use grounding for market research
            enable_thought_trace=True
        )
        
        return result["data"]
