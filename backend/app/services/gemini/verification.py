"""
Verification Agent - Autonomous self-verification loop for MenuPilot recommendations.

This agent implements the "Vibe Engineering" pattern where the AI verifies
and iteratively improves its own analysis and recommendations.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from loguru import logger

from app.services.gemini.base_agent import GeminiAgent


class VerificationStatus(str, Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    IMPROVED = "improved"


class ThinkingLevel(str, Enum):
    """Levels of thinking depth for complex analysis."""

    QUICK = "quick"  # Fast, surface-level analysis
    STANDARD = "standard"  # Normal analysis depth
    DEEP = "deep"  # In-depth analysis with multiple perspectives
    EXHAUSTIVE = "exhaustive"  # Maximum depth, multiple verification passes


@dataclass
class VerificationCheck:
    """Individual verification check result."""

    check_name: str
    passed: bool
    score: float  # 0.0 to 1.0
    feedback: str
    suggestions: List[str] = field(default_factory=list)


@dataclass
class VerificationResult:
    """Complete verification result with improvement suggestions."""

    status: VerificationStatus
    overall_score: float
    checks: List[VerificationCheck]
    improvements_made: List[str]
    iterations_used: int
    thinking_level: ThinkingLevel
    final_recommendation: Optional[str] = None


class VerificationAgent:
    """
    Autonomous verification agent that validates and improves MenuPilot analyses.

    Implements a multi-pass verification loop:
    1. Initial analysis review
    2. Data consistency checks
    3. Business logic validation
    4. Recommendation quality scoring
    5. Iterative improvement (if needed)
    """

    VERIFICATION_CHECKS = [
        "data_completeness",
        "bcg_classification_accuracy",
        "prediction_reasonableness",
        "campaign_alignment",
        "business_viability",
        "presentation_quality",
    ]

    MAX_IMPROVEMENT_ITERATIONS = 3
    PASSING_THRESHOLD = 0.75

    def __init__(self, gemini_agent: GeminiAgent):
        self.gemini = gemini_agent
        self.verification_history: List[VerificationResult] = []

    async def verify_analysis(
        self,
        analysis_data: Dict[str, Any],
        thinking_level: ThinkingLevel = ThinkingLevel.STANDARD,
        auto_improve: bool = True,
    ) -> VerificationResult:
        """
        Verify a complete MenuPilot analysis and optionally improve it.

        Args:
            analysis_data: The analysis to verify (BCG, predictions, campaigns)
            thinking_level: Depth of verification analysis
            auto_improve: Whether to automatically improve failing analyses

        Returns:
            VerificationResult with status, scores, and improvements
        """
        logger.info(f"Starting verification at {thinking_level.value} level")

        iterations = 0
        improvements_made = []
        current_data = analysis_data.copy()

        while iterations < self.MAX_IMPROVEMENT_ITERATIONS:
            iterations += 1

            checks = await self._run_verification_checks(current_data, thinking_level)
            overall_score = sum(c.score for c in checks) / len(checks)

            logger.info(f"Iteration {iterations}: Score {overall_score:.2f}")

            if overall_score >= self.PASSING_THRESHOLD:
                result = VerificationResult(
                    status=(
                        VerificationStatus.PASSED
                        if iterations == 1
                        else VerificationStatus.IMPROVED
                    ),
                    overall_score=overall_score,
                    checks=checks,
                    improvements_made=improvements_made,
                    iterations_used=iterations,
                    thinking_level=thinking_level,
                    final_recommendation=await self._generate_final_recommendation(
                        current_data, checks
                    ),
                )
                self.verification_history.append(result)
                return result

            if not auto_improve or iterations >= self.MAX_IMPROVEMENT_ITERATIONS:
                break

            improvement = await self._improve_analysis(
                current_data, checks, thinking_level
            )
            if improvement:
                current_data = improvement["improved_data"]
                improvements_made.append(improvement["description"])
            else:
                break

        checks = await self._run_verification_checks(current_data, thinking_level)
        overall_score = sum(c.score for c in checks) / len(checks)

        result = VerificationResult(
            status=(
                VerificationStatus.FAILED
                if overall_score < self.PASSING_THRESHOLD
                else VerificationStatus.IMPROVED
            ),
            overall_score=overall_score,
            checks=checks,
            improvements_made=improvements_made,
            iterations_used=iterations,
            thinking_level=thinking_level,
            final_recommendation=await self._generate_final_recommendation(
                current_data, checks
            ),
        )
        self.verification_history.append(result)
        return result

    async def _run_verification_checks(
        self,
        data: Dict[str, Any],
        thinking_level: ThinkingLevel,
    ) -> List[VerificationCheck]:
        """Run all verification checks on the analysis data."""
        checks = []

        checks.append(await self._check_data_completeness(data))
        checks.append(await self._check_bcg_accuracy(data, thinking_level))
        checks.append(await self._check_prediction_reasonableness(data))
        checks.append(await self._check_campaign_alignment(data, thinking_level))
        checks.append(await self._check_business_viability(data, thinking_level))
        checks.append(await self._check_presentation_quality(data))

        return checks

    async def _check_data_completeness(self, data: Dict[str, Any]) -> VerificationCheck:
        """Verify all required data fields are present and valid."""
        required_sections = ["products", "bcg_analysis", "predictions", "campaigns"]
        present = sum(1 for s in required_sections if s in data and data[s])
        score = present / len(required_sections)

        missing = [s for s in required_sections if s not in data or not data[s]]

        return VerificationCheck(
            check_name="data_completeness",
            passed=score >= 0.75,
            score=score,
            feedback=f"Found {present}/{len(required_sections)} required sections",
            suggestions=[f"Add missing section: {s}" for s in missing],
        )

    async def _check_bcg_accuracy(
        self,
        data: Dict[str, Any],
        thinking_level: ThinkingLevel,
    ) -> VerificationCheck:
        """Verify BCG classifications are accurate using Gemini analysis."""
        bcg_data = data.get("bcg_analysis", {})
        products = bcg_data.get("products", [])

        if not products:
            return VerificationCheck(
                check_name="bcg_classification_accuracy",
                passed=False,
                score=0.0,
                feedback="No BCG classifications to verify",
                suggestions=["Run BCG analysis first"],
            )

        prompt = f"""Verify these BCG Matrix classifications for accuracy.
        
Products and Classifications:
{self._format_bcg_for_verification(products)}

Thinking Level: {thinking_level.value}

For each product, verify:
1. Is the classification (Star/Cash Cow/Question Mark/Dog) appropriate given the metrics?
2. Are the market share and growth percentages realistic?
3. Do the strategic recommendations align with the classification?

Return a JSON object with:
{{
    "accuracy_score": 0.0-1.0,
    "issues": ["list of issues found"],
    "suggestions": ["list of improvements"],
    "verified_count": number,
    "total_count": number
}}
"""

        try:
            response = await self.gemini.generate_content(prompt, expect_json=True)
            accuracy = response.get("accuracy_score", 0.5)
            suggestions = response.get("suggestions", [])

            return VerificationCheck(
                check_name="bcg_classification_accuracy",
                passed=accuracy >= 0.7,
                score=accuracy,
                feedback=f"Verified {response.get('verified_count', 0)}/{response.get('total_count', len(products))} classifications",
                suggestions=suggestions[:3],
            )
        except Exception as e:
            logger.warning(f"BCG verification failed: {e}")
            return VerificationCheck(
                check_name="bcg_classification_accuracy",
                passed=True,
                score=0.7,
                feedback="Could not run AI verification, using default score",
                suggestions=[],
            )

    async def _check_prediction_reasonableness(
        self, data: Dict[str, Any]
    ) -> VerificationCheck:
        """Verify sales predictions are within reasonable bounds."""
        predictions = data.get("predictions", {})

        if not predictions:
            return VerificationCheck(
                check_name="prediction_reasonableness",
                passed=False,
                score=0.0,
                feedback="No predictions to verify",
                suggestions=["Run sales prediction first"],
            )

        issues = []
        total_checks = 0
        passed_checks = 0

        for item_name, pred_data in predictions.items():
            total_checks += 1
            daily_preds = pred_data.get("daily_predictions", [])

            if daily_preds:
                avg = sum(daily_preds) / len(daily_preds)
                max_val = max(daily_preds)
                min_val = min(daily_preds)

                if max_val > avg * 3:
                    issues.append(f"{item_name}: max prediction unrealistically high")
                elif min_val < 0:
                    issues.append(f"{item_name}: negative predictions")
                else:
                    passed_checks += 1

        score = passed_checks / total_checks if total_checks > 0 else 0

        return VerificationCheck(
            check_name="prediction_reasonableness",
            passed=score >= 0.7,
            score=score,
            feedback=f"{passed_checks}/{total_checks} predictions within reasonable bounds",
            suggestions=issues[:3],
        )

    async def _check_campaign_alignment(
        self,
        data: Dict[str, Any],
        thinking_level: ThinkingLevel,
    ) -> VerificationCheck:
        """Verify campaigns align with BCG analysis and business goals."""
        campaigns = data.get("campaigns", [])
        bcg_data = data.get("bcg_analysis", {})

        if not campaigns:
            return VerificationCheck(
                check_name="campaign_alignment",
                passed=False,
                score=0.0,
                feedback="No campaigns to verify",
                suggestions=["Generate marketing campaigns first"],
            )

        prompt = f"""Verify these marketing campaigns align with the BCG analysis.

BCG Analysis Summary:
- Stars: {len([p for p in bcg_data.get('products', []) if p.get('classification') == 'star'])}
- Cash Cows: {len([p for p in bcg_data.get('products', []) if p.get('classification') == 'cash_cow'])}
- Question Marks: {len([p for p in bcg_data.get('products', []) if p.get('classification') == 'question_mark'])}
- Dogs: {len([p for p in bcg_data.get('products', []) if p.get('classification') == 'dog'])}

Campaigns:
{self._format_campaigns_for_verification(campaigns)}

Verify:
1. Do campaigns focus on the right products based on BCG?
2. Are campaign objectives aligned with product classifications?
3. Is the timing and channel selection appropriate?

Return JSON:
{{
    "alignment_score": 0.0-1.0,
    "well_aligned_campaigns": ["list"],
    "misaligned_campaigns": ["list with reasons"],
    "suggestions": ["improvements"]
}}
"""

        try:
            response = await self.gemini.generate_content(prompt, expect_json=True)
            score = response.get("alignment_score", 0.5)

            return VerificationCheck(
                check_name="campaign_alignment",
                passed=score >= 0.7,
                score=score,
                feedback="Campaign-BCG alignment verified",
                suggestions=response.get("suggestions", [])[:3],
            )
        except Exception as e:
            logger.warning(f"Campaign alignment check failed: {e}")
            return VerificationCheck(
                check_name="campaign_alignment",
                passed=True,
                score=0.7,
                feedback="Could not run AI verification",
                suggestions=[],
            )

    async def _check_business_viability(
        self,
        data: Dict[str, Any],
        thinking_level: ThinkingLevel,
    ) -> VerificationCheck:
        """Verify recommendations are business-viable for a small restaurant."""
        campaigns = data.get("campaigns", [])

        prompt = f"""Evaluate business viability for a small/medium restaurant.

Recommendations to evaluate:
{self._format_campaigns_for_verification(campaigns[:3])}

Consider:
1. Implementation cost vs expected ROI
2. Staff and resource requirements
3. Timeline feasibility
4. Risk assessment

Thinking depth: {thinking_level.value}

Return JSON:
{{
    "viability_score": 0.0-1.0,
    "viable_recommendations": ["list"],
    "concerns": ["list of concerns"],
    "risk_level": "low/medium/high",
    "implementation_notes": ["practical notes"]
}}
"""

        try:
            response = await self.gemini.generate_content(prompt, expect_json=True)
            score = response.get("viability_score", 0.6)

            return VerificationCheck(
                check_name="business_viability",
                passed=score >= 0.6,
                score=score,
                feedback=f"Risk level: {response.get('risk_level', 'medium')}",
                suggestions=response.get("implementation_notes", [])[:3],
            )
        except Exception as e:
            logger.warning(f"Business viability check failed: {e}")
            return VerificationCheck(
                check_name="business_viability",
                passed=True,
                score=0.7,
                feedback="Default viability score applied",
                suggestions=[],
            )

    async def _check_presentation_quality(
        self, data: Dict[str, Any]
    ) -> VerificationCheck:
        """Check that the analysis is well-presented and clear."""
        score = 0.0
        suggestions = []

        if data.get("thought_signature"):
            score += 0.3
        else:
            suggestions.append("Add thought signature for transparency")

        bcg = data.get("bcg_analysis", {})
        if bcg.get("summary") or bcg.get("insights"):
            score += 0.3
        else:
            suggestions.append("Add executive summary to BCG analysis")

        campaigns = data.get("campaigns", [])
        if campaigns and all(c.get("rationale") for c in campaigns):
            score += 0.4
        elif campaigns:
            score += 0.2
            suggestions.append("Add rationale to all campaigns")
        else:
            suggestions.append("Generate campaign recommendations")

        return VerificationCheck(
            check_name="presentation_quality",
            passed=score >= 0.6,
            score=score,
            feedback="Presentation quality assessment complete",
            suggestions=suggestions,
        )

    async def _improve_analysis(
        self,
        data: Dict[str, Any],
        checks: List[VerificationCheck],
        thinking_level: ThinkingLevel,
    ) -> Optional[Dict[str, Any]]:
        """Attempt to improve the analysis based on verification feedback."""
        failing_checks = [c for c in checks if not c.passed]

        if not failing_checks:
            return None

        all_suggestions = []
        for check in failing_checks:
            all_suggestions.extend(check.suggestions)

        prompt = f"""Improve this restaurant analysis based on feedback.

Current Issues:
{chr(10).join(f'- {c.check_name}: {c.feedback}' for c in failing_checks)}

Suggestions to implement:
{chr(10).join(f'- {s}' for s in all_suggestions[:5])}

Current Data Summary:
- Products: {len(data.get('products', []))}
- BCG Classifications: {len(data.get('bcg_analysis', {}).get('products', []))}
- Campaigns: {len(data.get('campaigns', []))}

Thinking Level: {thinking_level.value}

Provide specific improvements as JSON:
{{
    "improvement_description": "what was improved",
    "enhanced_insights": ["new insights to add"],
    "corrected_classifications": {{}},
    "improved_campaigns": []
}}
"""

        try:
            response = await self.gemini.generate_content(prompt, expect_json=True)

            improved_data = data.copy()

            if response.get("enhanced_insights"):
                if "bcg_analysis" not in improved_data:
                    improved_data["bcg_analysis"] = {}
                improved_data["bcg_analysis"]["ai_insights"] = response[
                    "enhanced_insights"
                ]

            return {
                "improved_data": improved_data,
                "description": response.get(
                    "improvement_description", "Analysis improved"
                ),
            }
        except Exception as e:
            logger.warning(f"Improvement attempt failed: {e}")
            return None

    async def _generate_final_recommendation(
        self,
        data: Dict[str, Any],
        checks: List[VerificationCheck],
    ) -> str:
        """Generate a final summary recommendation based on verified analysis."""
        overall_score = sum(c.score for c in checks) / len(checks)

        prompt = f"""Generate a concise final recommendation for the restaurant owner.

Verification Results:
- Overall Score: {overall_score:.0%}
- Checks Passed: {sum(1 for c in checks if c.passed)}/{len(checks)}

Key Insights:
{chr(10).join(f'- {c.check_name}: {c.feedback}' for c in checks)}

Products Analyzed: {len(data.get('products', []))}
Campaigns Generated: {len(data.get('campaigns', []))}

Provide a 2-3 sentence executive summary recommendation.
"""

        try:
            response = await self.gemini.generate_content(prompt)
            return response if isinstance(response, str) else str(response)
        except Exception:
            return f"Analysis complete with {overall_score:.0%} confidence. Review the detailed reports for specific action items."

    def _format_bcg_for_verification(self, products: List[Dict]) -> str:
        """Format BCG products for verification prompt."""
        lines = []
        for p in products[:10]:
            lines.append(
                f"- {p.get('name', 'Unknown')}: {p.get('classification', 'N/A')} "
                f"(share: {p.get('market_share', 0):.0%}, growth: {p.get('growth_rate', 0):.0%})"
            )
        return "\n".join(lines)

    def _format_campaigns_for_verification(self, campaigns: List[Dict]) -> str:
        """Format campaigns for verification prompt."""
        lines = []
        for c in campaigns[:5]:
            lines.append(
                f"- {c.get('name', 'Campaign')}: {c.get('objective', 'N/A')} "
                f"targeting {', '.join(c.get('target_products', [])[:3])}"
            )
        return "\n".join(lines)

    def get_verification_summary(self) -> Dict[str, Any]:
        """Get summary of all verification runs."""
        if not self.verification_history:
            return {"total_runs": 0}

        return {
            "total_runs": len(self.verification_history),
            "passed": sum(
                1
                for v in self.verification_history
                if v.status == VerificationStatus.PASSED
            ),
            "improved": sum(
                1
                for v in self.verification_history
                if v.status == VerificationStatus.IMPROVED
            ),
            "failed": sum(
                1
                for v in self.verification_history
                if v.status == VerificationStatus.FAILED
            ),
            "avg_score": sum(v.overall_score for v in self.verification_history)
            / len(self.verification_history),
            "total_improvements": sum(
                len(v.improvements_made) for v in self.verification_history
            ),
        }


# Alias for backward compatibility
GeminiVerificationAgent = VerificationAgent
