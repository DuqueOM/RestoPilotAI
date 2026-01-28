"""
Gemini Reasoning Agent - Deep analysis and strategic reasoning.

Handles:
- BCG Matrix strategic analysis
- Competitive positioning analysis
- Business strategy recommendations
- Multi-perspective reasoning with thought traces
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from loguru import logger

from app.services.gemini.base_agent import GeminiBaseAgent, GeminiModel, ThinkingLevel


@dataclass
class ThoughtTrace:
    """Detailed thought trace for transparent reasoning."""

    step: str
    reasoning: str
    observations: List[str]
    decisions: List[str]
    confidence: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "reasoning": self.reasoning,
            "observations": self.observations,
            "decisions": self.decisions,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ReasoningResult:
    """Result from a reasoning operation."""

    analysis: Dict[str, Any]
    thought_traces: List[ThoughtTrace]
    thinking_level: ThinkingLevel
    confidence: float
    processing_time_ms: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "analysis": self.analysis,
            "thought_traces": [t.to_dict() for t in self.thought_traces],
            "thinking_level": self.thinking_level.value,
            "confidence": self.confidence,
            "processing_time_ms": self.processing_time_ms,
        }


class ReasoningAgent(GeminiBaseAgent):
    """
    Agent specialized in deep strategic analysis and reasoning.

    Implements multi-level thinking:
    - QUICK: Fast, surface-level analysis
    - STANDARD: Balanced analysis with key insights
    - DEEP: Multi-perspective analysis with detailed reasoning
    - EXHAUSTIVE: Comprehensive analysis with scenario planning
    """

    # Temperature settings per thinking level
    THINKING_CONFIGS = {
        ThinkingLevel.QUICK: {
            "temperature": 0.5,
            "max_tokens": 2048,
            "reasoning_depth": "surface",
        },
        ThinkingLevel.STANDARD: {
            "temperature": 0.6,
            "max_tokens": 4096,
            "reasoning_depth": "balanced",
        },
        ThinkingLevel.DEEP: {
            "temperature": 0.7,
            "max_tokens": 8192,
            "reasoning_depth": "multi-perspective",
        },
        ThinkingLevel.EXHAUSTIVE: {
            "temperature": 0.7,
            "max_tokens": 16384,
            "reasoning_depth": "comprehensive",
        },
    }

    def __init__(
        self,
        model: GeminiModel = GeminiModel.FLASH,
        **kwargs,
    ):
        super().__init__(model=model, **kwargs)
        self.thought_traces: List[ThoughtTrace] = []

    async def process(self, *args, **kwargs) -> Any:
        """Main entry point - routes to specific reasoning method."""
        task = kwargs.get("task", "bcg_analysis")

        if task == "bcg_analysis":
            return await self.analyze_bcg_strategy(**kwargs)
        elif task == "competitive_analysis":
            return await self.analyze_competitive_position(**kwargs)
        elif task == "strategic_recommendations":
            return await self.generate_strategic_recommendations(**kwargs)
        elif task == "executive_summary":
            return await self.generate_executive_summary(**kwargs)
        else:
            raise ValueError(f"Unknown task: {task}")

    async def create_thought_signature(
        self,
        task: str,
        context: Dict[str, Any],
        thinking_level: ThinkingLevel = ThinkingLevel.STANDARD,
    ) -> Dict[str, Any]:
        """
        Generate a Thought Signature - transparent reasoning trace.

        Shows the agent's planning and reasoning process before executing.
        """
        config = self.THINKING_CONFIGS[thinking_level]

        prompt = f"""You are MenuPilot, an AI assistant for restaurant optimization.

Before executing the following task, create a detailed thought signature that outlines your reasoning process.

Task: {task}

Context (summarized):
{json.dumps(self._summarize_context(context), indent=2, default=str)}

Create a thought signature with:
1. Plan of action (numbered steps)
2. Key observations from context
3. Main reasoning chain
4. Assumptions being made
5. Potential risks or uncertainties
6. Confidence level (0-1)

Thinking depth: {config['reasoning_depth']}

RESPOND WITH VALID JSON:
{{
    "plan": ["Step 1: ...", "Step 2: ...", "Step 3: ..."],
    "observations": ["Key observation 1", "Key observation 2"],
    "reasoning": "Main reasoning explanation connecting observations to conclusions...",
    "assumptions": ["Assumption 1", "Assumption 2"],
    "risks": ["Potential risk 1", "Uncertainty 1"],
    "confidence": 0.85,
    "estimated_complexity": "medium"
}}"""

        try:
            response = await self._generate_content(
                prompt=prompt,
                temperature=config["temperature"],
                max_output_tokens=2048,
                feature="thought_signature",
            )

            result = self._parse_json_response(response)

            # Record thought trace
            trace = ThoughtTrace(
                step=f"Planning: {task}",
                reasoning=result.get("reasoning", ""),
                observations=result.get("observations", []),
                decisions=result.get("plan", []),
                confidence=result.get("confidence", 0.7),
            )
            self.thought_traces.append(trace)

            return result

        except Exception as e:
            logger.error(f"Thought signature generation failed: {e}")
            return {
                "plan": [f"Execute {task}"],
                "observations": ["Context provided"],
                "reasoning": "Standard analysis approach",
                "assumptions": ["Data is accurate"],
                "confidence": 0.6,
            }

    async def analyze_bcg_strategy(
        self,
        products: List[Dict[str, Any]],
        sales_data: Optional[List[Dict[str, Any]]] = None,
        bcg_classifications: Optional[Dict[str, Any]] = None,
        thinking_level: ThinkingLevel = ThinkingLevel.STANDARD,
        **kwargs,
    ) -> ReasoningResult:
        """
        Generate strategic BCG insights with deep reasoning.

        Args:
            products: List of product data
            sales_data: Historical sales data
            bcg_classifications: Pre-computed BCG classifications
            thinking_level: Depth of analysis

        Returns:
            ReasoningResult with strategic insights
        """
        import time

        start_time = time.time()

        config = self.THINKING_CONFIGS[thinking_level]

        # Create thought signature first
        await self.create_thought_signature(
            task="BCG Strategic Analysis",
            context={"products": len(products), "has_sales": bool(sales_data)},
            thinking_level=thinking_level,
        )

        prompt = f"""You are a senior restaurant business strategist using the BCG Matrix framework.

PRODUCT DATA ({len(products)} items):
{json.dumps(products[:30], indent=2, default=str)}

{"SALES DATA (sample):" + chr(10) + json.dumps(sales_data[:50] if sales_data else [], indent=2, default=str) if sales_data else "No historical sales data available."}

{"CURRENT BCG CLASSIFICATIONS:" + chr(10) + json.dumps(bcg_classifications, indent=2, default=str) if bcg_classifications else ""}

Perform a {config['reasoning_depth']} BCG strategic analysis:

THINKING PROCESS (show your work):
1. First, identify market dynamics and growth patterns
2. Calculate relative market share indicators
3. Classify each significant product
4. Identify strategic opportunities and risks
5. Develop actionable recommendations

RESPOND WITH VALID JSON:
{{
    "thinking_trace": {{
        "market_analysis": "Analysis of overall market dynamics...",
        "key_patterns": ["Pattern 1", "Pattern 2"],
        "classification_rationale": "How classifications were determined..."
    }},
    "portfolio_assessment": {{
        "health_score": 7.5,
        "balance": "slightly_unbalanced",
        "risk_level": "moderate",
        "growth_potential": "high",
        "summary": "Portfolio overview..."
    }},
    "quadrant_analysis": {{
        "stars": {{
            "items": ["Item 1", "Item 2"],
            "strategy": "Invest heavily to maintain leadership",
            "key_insight": "These drive future growth",
            "risks": ["Risk of over-investment"]
        }},
        "cash_cows": {{
            "items": ["Item 3", "Item 4"],
            "strategy": "Harvest profits, minimal investment",
            "key_insight": "Fund other quadrants",
            "risks": ["May decline if neglected"]
        }},
        "question_marks": {{
            "items": ["Item 5"],
            "strategy": "Selective investment or divest",
            "key_insight": "Require decision and resources",
            "risks": ["Could become dogs"]
        }},
        "dogs": {{
            "items": ["Item 6"],
            "strategy": "Consider phasing out or repositioning",
            "key_insight": "Drain resources",
            "opportunities": ["Niche market potential"]
        }}
    }},
    "strategic_recommendations": [
        {{
            "priority": 1,
            "action": "Specific action to take",
            "target_items": ["Item 1"],
            "expected_impact": "Revenue increase of 15%",
            "timeframe": "30 days",
            "investment_required": "low",
            "rationale": "Why this action..."
        }}
    ],
    "market_opportunities": [
        {{
            "opportunity": "Gap in menu",
            "potential_impact": "high",
            "recommendation": "Add trending item type"
        }}
    ],
    "risk_assessment": {{
        "high_risk_items": ["Item with issues"],
        "market_risks": ["Competitive pressure"],
        "mitigation_strategies": ["Strategy 1"]
    }},
    "confidence_scores": {{
        "overall": 0.85,
        "data_quality": 0.9,
        "market_assumptions": 0.75
    }}
}}

Think step-by-step. Be specific with numbers and item names."""

        try:
            response = await self._generate_content(
                prompt=prompt,
                temperature=config["temperature"],
                max_output_tokens=config["max_tokens"],
                feature="bcg_strategy",
            )

            analysis = self._parse_json_response(response)

            # Record thought trace
            trace = ThoughtTrace(
                step="BCG Strategic Analysis",
                reasoning=analysis.get("thinking_trace", {}).get("market_analysis", ""),
                observations=analysis.get("thinking_trace", {}).get("key_patterns", []),
                decisions=[
                    r.get("action", "")
                    for r in analysis.get("strategic_recommendations", [])[:3]
                ],
                confidence=analysis.get("confidence_scores", {}).get("overall", 0.7),
            )
            self.thought_traces.append(trace)

            processing_time = int((time.time() - start_time) * 1000)

            return ReasoningResult(
                analysis=analysis,
                thought_traces=self.thought_traces.copy(),
                thinking_level=thinking_level,
                confidence=analysis.get("confidence_scores", {}).get("overall", 0.7),
                processing_time_ms=processing_time,
            )

        except Exception as e:
            logger.error(f"BCG strategy analysis failed: {e}")
            return ReasoningResult(
                analysis={"error": str(e)},
                thought_traces=self.thought_traces.copy(),
                thinking_level=thinking_level,
                confidence=0,
                processing_time_ms=int((time.time() - start_time) * 1000),
            )

    async def analyze_competitive_position(
        self,
        our_menu: Dict[str, Any],
        competitor_menus: List[Dict[str, Any]],
        our_sentiment: Optional[Dict[str, Any]] = None,
        thinking_level: ThinkingLevel = ThinkingLevel.DEEP,
        **kwargs,
    ) -> ReasoningResult:
        """
        Analyze competitive positioning with strategic recommendations.

        Args:
            our_menu: Our restaurant's menu data
            competitor_menus: List of competitor menu data
            our_sentiment: Our customer sentiment data
            thinking_level: Depth of analysis

        Returns:
            ReasoningResult with competitive insights
        """
        import time

        start_time = time.time()

        config = self.THINKING_CONFIGS[thinking_level]

        prompt = f"""You are a restaurant competitive intelligence analyst.

OUR MENU:
{json.dumps(our_menu, indent=2, default=str)[:10000]}

COMPETITOR MENUS ({len(competitor_menus)} competitors):
{json.dumps(competitor_menus, indent=2, default=str)[:15000]}

{"OUR CUSTOMER SENTIMENT:" + chr(10) + json.dumps(our_sentiment, indent=2, default=str)[:3000] if our_sentiment else ""}

Perform {config['reasoning_depth']} competitive analysis:

RESPOND WITH VALID JSON:
{{
    "competitive_landscape": {{
        "market_position": "Where we stand (leader/challenger/follower/niche)",
        "competitive_intensity": "high/medium/low",
        "key_differentiators": ["Our unique advantage 1", "Our advantage 2"],
        "competitive_gaps": ["Where we fall short 1"]
    }},
    "price_analysis": {{
        "our_positioning": "premium/mid-range/budget",
        "vs_competitors": {{
            "competitor_name": {{
                "price_difference_percent": -5,
                "interpretation": "We are 5% cheaper overall"
            }}
        }},
        "price_gaps": [
            {{
                "item_category": "Tacos",
                "our_avg_price": 85,
                "competitor_avg_price": 75,
                "gap_percent": 13,
                "recommendation": "Consider price adjustment"
            }}
        ],
        "pricing_opportunities": ["Opportunity 1"]
    }},
    "product_analysis": {{
        "our_unique_items": ["Item only we offer"],
        "competitor_unique_items": {{
            "competitor_name": ["Their unique items"]
        }},
        "category_gaps": [
            {{
                "category": "Vegan options",
                "competitors_offering": 3,
                "our_count": 0,
                "opportunity": "Add vegan menu section"
            }}
        ],
        "trending_items_missing": ["Popular item we don't have"]
    }},
    "strategic_recommendations": [
        {{
            "priority": 1,
            "type": "pricing/product/positioning",
            "recommendation": "Specific actionable recommendation",
            "expected_impact": "Quantified impact",
            "competitive_response_risk": "How competitors might react",
            "implementation_difficulty": "easy/medium/hard"
        }}
    ],
    "competitive_threats": [
        {{
            "threat": "Specific competitive threat",
            "severity": "high/medium/low",
            "recommended_response": "How to counter"
        }}
    ],
    "market_positioning_matrix": {{
        "x_axis": "price",
        "y_axis": "quality_perception",
        "our_position": {{"x": 0.6, "y": 0.75}},
        "competitors": {{
            "competitor_name": {{"x": 0.5, "y": 0.7}}
        }},
        "optimal_position": {{"x": 0.65, "y": 0.85}},
        "repositioning_strategy": "How to move to optimal position"
    }},
    "confidence": 0.82
}}

Be specific with competitor names, prices, and item references."""

        try:
            response = await self._generate_content(
                prompt=prompt,
                temperature=config["temperature"],
                max_output_tokens=config["max_tokens"],
                feature="competitive_analysis",
            )

            analysis = self._parse_json_response(response)

            trace = ThoughtTrace(
                step="Competitive Position Analysis",
                reasoning="Analyzed competitive landscape across price, product, and positioning dimensions",
                observations=analysis.get("competitive_landscape", {}).get(
                    "key_differentiators", []
                ),
                decisions=[
                    r.get("recommendation", "")
                    for r in analysis.get("strategic_recommendations", [])[:3]
                ],
                confidence=analysis.get("confidence", 0.7),
            )
            self.thought_traces.append(trace)

            processing_time = int((time.time() - start_time) * 1000)

            return ReasoningResult(
                analysis=analysis,
                thought_traces=self.thought_traces.copy(),
                thinking_level=thinking_level,
                confidence=analysis.get("confidence", 0.7),
                processing_time_ms=processing_time,
            )

        except Exception as e:
            logger.error(f"Competitive analysis failed: {e}")
            return ReasoningResult(
                analysis={"error": str(e)},
                thought_traces=self.thought_traces.copy(),
                thinking_level=thinking_level,
                confidence=0,
                processing_time_ms=int((time.time() - start_time) * 1000),
            )

    async def generate_strategic_recommendations(
        self,
        bcg_analysis: Dict[str, Any],
        competitive_analysis: Optional[Dict[str, Any]] = None,
        sentiment_analysis: Optional[Dict[str, Any]] = None,
        predictions: Optional[Dict[str, Any]] = None,
        thinking_level: ThinkingLevel = ThinkingLevel.DEEP,
        **kwargs,
    ) -> ReasoningResult:
        """
        Generate comprehensive strategic recommendations.

        Synthesizes all available data into actionable strategy.
        """
        import time

        start_time = time.time()

        config = self.THINKING_CONFIGS[thinking_level]

        prompt = f"""You are a senior restaurant strategy consultant creating actionable recommendations.

BCG ANALYSIS:
{json.dumps(bcg_analysis, indent=2, default=str)[:5000]}

{"COMPETITIVE INTELLIGENCE:" + chr(10) + json.dumps(competitive_analysis, indent=2, default=str)[:4000] if competitive_analysis else ""}

{"CUSTOMER SENTIMENT:" + chr(10) + json.dumps(sentiment_analysis, indent=2, default=str)[:3000] if sentiment_analysis else ""}

{"SALES PREDICTIONS:" + chr(10) + json.dumps(predictions, indent=2, default=str)[:3000] if predictions else ""}

Synthesize all data into a comprehensive strategic plan:

RESPOND WITH VALID JSON:
{{
    "executive_summary": "2-3 sentence overview of strategic situation and key recommendation",
    
    "immediate_actions": [
        {{
            "action": "Specific action to take",
            "rationale": "Why this action based on data",
            "data_support": ["BCG shows X", "Sentiment indicates Y"],
            "expected_outcome": "Quantified expected result",
            "timeline": "Within 7 days",
            "owner": "Role responsible",
            "success_metrics": ["Metric 1", "Metric 2"]
        }}
    ],
    
    "short_term_initiatives": [
        {{
            "initiative": "Initiative name",
            "description": "Detailed description",
            "objectives": ["Objective 1", "Objective 2"],
            "timeline": "30 days",
            "resources_required": "Budget, people, etc.",
            "risk_factors": ["Risk 1"],
            "mitigation_plan": "How to handle risks"
        }}
    ],
    
    "long_term_strategy": {{
        "vision": "Where we want to be in 90 days",
        "strategic_pillars": [
            {{
                "pillar": "Strategic focus area",
                "initiatives": ["Initiative 1", "Initiative 2"],
                "target_metrics": {{"metric": "value"}}
            }}
        ],
        "investment_priorities": ["Priority 1", "Priority 2"],
        "competitive_moat": "How we'll differentiate long-term"
    }},
    
    "menu_recommendations": {{
        "items_to_promote": [
            {{
                "item": "Item name",
                "reason": "Why promote (Star status, high margin)",
                "promotion_strategy": "How to promote"
            }}
        ],
        "items_to_improve": [
            {{
                "item": "Item name", 
                "issue": "Sentiment shows portion complaints",
                "improvement": "Increase portion by 15%"
            }}
        ],
        "items_to_consider_removing": [
            {{
                "item": "Item name",
                "reason": "Dog status, negative sentiment, low sales",
                "alternative": "Consider replacing with trending item"
            }}
        ],
        "new_items_to_consider": ["Based on competitive gaps"]
    }},
    
    "pricing_strategy": {{
        "overall_direction": "maintain/increase/decrease",
        "specific_adjustments": [
            {{
                "item": "Item name",
                "current_price": 85,
                "recommended_price": 79,
                "rationale": "Competitive pressure"
            }}
        ],
        "bundle_opportunities": ["Bundle idea 1"]
    }},
    
    "financial_projections": {{
        "revenue_impact": {{
            "optimistic": "+25%",
            "realistic": "+15%",
            "conservative": "+8%"
        }},
        "cost_implications": "Expected additional costs",
        "roi_timeline": "When to expect returns"
    }},
    
    "risk_matrix": [
        {{
            "risk": "Risk description",
            "probability": "high/medium/low",
            "impact": "high/medium/low",
            "mitigation": "How to mitigate"
        }}
    ],
    
    "confidence": 0.85
}}

Be specific, actionable, and data-driven."""

        try:
            response = await self._generate_content(
                prompt=prompt,
                temperature=config["temperature"],
                max_output_tokens=config["max_tokens"],
                feature="strategic_recommendations",
            )

            analysis = self._parse_json_response(response)

            trace = ThoughtTrace(
                step="Strategic Recommendations",
                reasoning=analysis.get("executive_summary", ""),
                observations=[
                    a.get("rationale", "")
                    for a in analysis.get("immediate_actions", [])[:3]
                ],
                decisions=[
                    a.get("action", "")
                    for a in analysis.get("immediate_actions", [])[:3]
                ],
                confidence=analysis.get("confidence", 0.7),
            )
            self.thought_traces.append(trace)

            processing_time = int((time.time() - start_time) * 1000)

            return ReasoningResult(
                analysis=analysis,
                thought_traces=self.thought_traces.copy(),
                thinking_level=thinking_level,
                confidence=analysis.get("confidence", 0.7),
                processing_time_ms=processing_time,
            )

        except Exception as e:
            logger.error(f"Strategic recommendations failed: {e}")
            return ReasoningResult(
                analysis={"error": str(e)},
                thought_traces=self.thought_traces.copy(),
                thinking_level=thinking_level,
                confidence=0,
                processing_time_ms=int((time.time() - start_time) * 1000),
            )

    async def generate_executive_summary(
        self,
        complete_analysis: Dict[str, Any],
        restaurant_name: str = "Restaurant",
        thinking_level: ThinkingLevel = ThinkingLevel.EXHAUSTIVE,
        **kwargs,
    ) -> str:
        """
        Generate comprehensive executive summary from all analysis data.

        Args:
            complete_analysis: All analysis results combined
            restaurant_name: Name of the restaurant
            thinking_level: Depth of summary

        Returns:
            Formatted executive summary text
        """
        config = self.THINKING_CONFIGS[thinking_level]

        prompt = f"""You are a senior restaurant consultant creating an executive summary for {restaurant_name}.

COMPLETE ANALYSIS DATA:
{json.dumps(complete_analysis, indent=2, default=str)[:20000]}

Create a comprehensive executive summary (500-800 words) that:

1. SITUATION ANALYSIS
   - Current menu performance highlights
   - Competitive position
   - Customer perception summary

2. KEY FINDINGS
   - Top 3 opportunities (with specific numbers)
   - Top 3 risks (with severity)
   - Hidden insights discovered from data

3. STRATEGIC RECOMMENDATIONS
   - Immediate actions (next 7 days) - specific and actionable
   - Short-term initiatives (30 days) 
   - Long-term strategy (90 days)

4. FINANCIAL IMPACT
   - Revenue opportunities identified (with estimates)
   - Cost optimization potential
   - ROI expectations

5. NEXT STEPS
   - Prioritized action items
   - Key decisions needed
   - Success metrics to track

FORMAT REQUIREMENTS:
- Use professional business language
- Include specific numbers and percentages from the data
- Be actionable and concrete
- Use bullet points for clarity where appropriate
- End with clear call to action

Write the executive summary now:"""

        try:
            response = await self._generate_content(
                prompt=prompt,
                temperature=0.6,
                max_output_tokens=config["max_tokens"],
                feature="executive_summary",
            )

            return response

        except Exception as e:
            logger.error(f"Executive summary generation failed: {e}")
            return f"Error generating executive summary: {str(e)}"

    def _summarize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize context for thought signature generation."""
        summary = {}

        for key, value in context.items():
            if isinstance(value, list):
                summary[key] = f"List with {len(value)} items"
            elif isinstance(value, dict):
                summary[key] = f"Dict with keys: {list(value.keys())[:5]}"
            elif isinstance(value, str) and len(value) > 200:
                summary[key] = value[:200] + "..."
            else:
                summary[key] = value

        return summary

    def get_thought_traces(self) -> List[Dict[str, Any]]:
        """Get all thought traces from this session."""
        return [t.to_dict() for t in self.thought_traces]

    def clear_thought_traces(self) -> None:
        """Clear thought traces for new session."""
        self.thought_traces = []
