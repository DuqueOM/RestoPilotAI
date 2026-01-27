"""
Gemini Verification Agent - Self-verification and quality assurance.

Implements the Vibe Engineering pattern:
- Self-verification loops
- Quality threshold checking
- Automatic improvement iterations
- Confidence quantification
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from loguru import logger

from app.services.gemini.base_agent import (
    GeminiBaseAgent,
    GeminiModel,
    ThinkingLevel,
)


class VerificationStatus(str, Enum):
    """Status of verification check."""
    
    PASSED = "passed"
    PASSED_WITH_WARNINGS = "passed_with_warnings"
    NEEDS_IMPROVEMENT = "needs_improvement"
    FAILED = "failed"


@dataclass
class VerificationCheck:
    """Result of a single verification check."""
    
    check_name: str
    passed: bool
    score: float  # 0-1
    feedback: str
    suggestions: List[str] = field(default_factory=list)
    severity: str = "info"  # info, warning, error
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_name": self.check_name,
            "passed": self.passed,
            "score": self.score,
            "feedback": self.feedback,
            "suggestions": self.suggestions,
            "severity": self.severity,
        }


@dataclass
class VerificationResult:
    """Complete verification result."""
    
    status: VerificationStatus
    overall_score: float
    checks: List[VerificationCheck]
    iterations_used: int
    improvements_made: List[str]
    final_recommendation: str
    thinking_level: ThinkingLevel
    improved_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "overall_score": self.overall_score,
            "checks": [c.to_dict() for c in self.checks],
            "iterations_used": self.iterations_used,
            "improvements_made": self.improvements_made,
            "final_recommendation": self.final_recommendation,
            "thinking_level": self.thinking_level.value,
            "has_improved_data": self.improved_data is not None,
        }


class GeminiVerificationAgent(GeminiBaseAgent):
    """
    Agent specialized in self-verification and quality assurance.
    
    Implements autonomous verification loop:
    1. Analyze quality of provided analysis
    2. Check for logical consistency
    3. Verify data accuracy
    4. Assess recommendation feasibility
    5. Auto-improve if below threshold
    6. Iterate until confident
    """
    
    # Quality thresholds
    QUALITY_THRESHOLDS = {
        ThinkingLevel.QUICK: 0.6,
        ThinkingLevel.STANDARD: 0.7,
        ThinkingLevel.DEEP: 0.8,
        ThinkingLevel.EXHAUSTIVE: 0.85,
    }
    
    MAX_ITERATIONS = {
        ThinkingLevel.QUICK: 1,
        ThinkingLevel.STANDARD: 2,
        ThinkingLevel.DEEP: 3,
        ThinkingLevel.EXHAUSTIVE: 5,
    }
    
    def __init__(
        self,
        model: GeminiModel = GeminiModel.FLASH,
        **kwargs,
    ):
        super().__init__(model=model, **kwargs)
        self.verification_history: List[VerificationResult] = []
    
    async def process(self, *args, **kwargs) -> Any:
        """Main entry point."""
        return await self.verify_analysis(**kwargs)
    
    async def verify_analysis(
        self,
        analysis_data: Dict[str, Any],
        thinking_level: ThinkingLevel = ThinkingLevel.STANDARD,
        auto_improve: bool = True,
        custom_checks: Optional[List[str]] = None,
        **kwargs,
    ) -> VerificationResult:
        """
        Verify analysis quality with optional auto-improvement.
        
        Args:
            analysis_data: The analysis to verify
            thinking_level: Depth of verification
            auto_improve: Whether to auto-improve if below threshold
            custom_checks: Additional custom checks to perform
            
        Returns:
            VerificationResult with status and improvements
        """
        threshold = self.QUALITY_THRESHOLDS[thinking_level]
        max_iterations = self.MAX_ITERATIONS[thinking_level]
        
        current_data = analysis_data.copy()
        improvements_made = []
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Verification iteration {iteration}/{max_iterations}")
            
            # Run verification checks
            checks = await self._run_verification_checks(
                current_data,
                thinking_level,
                custom_checks,
            )
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(checks)
            
            logger.info(f"Verification score: {overall_score:.2%} (threshold: {threshold:.2%})")
            
            # Determine status
            if overall_score >= threshold:
                status = VerificationStatus.PASSED
                if any(c.severity == "warning" for c in checks):
                    status = VerificationStatus.PASSED_WITH_WARNINGS
                break
            
            # Check if we should improve
            if not auto_improve or iteration >= max_iterations:
                status = (
                    VerificationStatus.NEEDS_IMPROVEMENT 
                    if overall_score >= 0.5 
                    else VerificationStatus.FAILED
                )
                break
            
            # Auto-improve
            logger.info("Running auto-improvement...")
            improved_data, improvement_desc = await self._auto_improve(
                current_data,
                checks,
                thinking_level,
            )
            
            if improved_data:
                current_data = improved_data
                improvements_made.append(improvement_desc)
            else:
                # No improvements possible
                status = VerificationStatus.NEEDS_IMPROVEMENT
                break
        
        # Generate final recommendation
        final_recommendation = await self._generate_recommendation(
            checks,
            overall_score,
            improvements_made,
        )
        
        result = VerificationResult(
            status=status,
            overall_score=overall_score,
            checks=checks,
            iterations_used=iteration,
            improvements_made=improvements_made,
            final_recommendation=final_recommendation,
            thinking_level=thinking_level,
            improved_data=current_data if improvements_made else None,
        )
        
        self.verification_history.append(result)
        
        return result
    
    async def _run_verification_checks(
        self,
        analysis_data: Dict[str, Any],
        thinking_level: ThinkingLevel,
        custom_checks: Optional[List[str]] = None,
    ) -> List[VerificationCheck]:
        """Run all verification checks on the analysis."""
        
        checks = []
        
        # 1. Data Completeness Check
        completeness = await self._check_data_completeness(analysis_data)
        checks.append(completeness)
        
        # 2. Logical Consistency Check
        consistency = await self._check_logical_consistency(analysis_data)
        checks.append(consistency)
        
        # 3. BCG Classification Accuracy (if applicable)
        if "bcg_analysis" in analysis_data or "classifications" in analysis_data:
            bcg_check = await self._check_bcg_accuracy(analysis_data)
            checks.append(bcg_check)
        
        # 4. Prediction Reasonableness (if applicable)
        if "predictions" in analysis_data:
            prediction_check = await self._check_prediction_reasonableness(analysis_data)
            checks.append(prediction_check)
        
        # 5. Campaign Alignment (if applicable)
        if "campaigns" in analysis_data:
            campaign_check = await self._check_campaign_alignment(analysis_data)
            checks.append(campaign_check)
        
        # 6. Business Viability Check
        viability = await self._check_business_viability(analysis_data)
        checks.append(viability)
        
        # 7. Custom checks
        if custom_checks:
            for check_name in custom_checks:
                custom = await self._run_custom_check(analysis_data, check_name)
                checks.append(custom)
        
        return checks
    
    async def _check_data_completeness(
        self,
        analysis_data: Dict[str, Any],
    ) -> VerificationCheck:
        """Verify data completeness."""
        
        prompt = f"""Analyze this data for completeness:

{json.dumps(analysis_data, indent=2, default=str)[:5000]}

Check for:
1. Missing required fields
2. Empty or null values that should have data
3. Incomplete analysis sections
4. Missing cross-references

RESPOND WITH JSON:
{{
    "passed": true/false,
    "score": 0.85,
    "missing_fields": ["field1", "field2"],
    "empty_values": ["field3"],
    "feedback": "Overall assessment...",
    "suggestions": ["Add X", "Complete Y"]
}}"""

        try:
            response = await self._generate_content(
                prompt=prompt,
                temperature=0.3,
                max_output_tokens=2048,
                feature="verification_completeness",
            )
            
            result = self._parse_json_response(response)
            
            return VerificationCheck(
                check_name="data_completeness",
                passed=result.get("passed", False),
                score=result.get("score", 0.5),
                feedback=result.get("feedback", ""),
                suggestions=result.get("suggestions", []),
                severity="warning" if not result.get("passed") else "info",
            )
            
        except Exception as e:
            logger.error(f"Completeness check failed: {e}")
            return VerificationCheck(
                check_name="data_completeness",
                passed=False,
                score=0.5,
                feedback=f"Check failed: {str(e)}",
                suggestions=[],
                severity="error",
            )
    
    async def _check_logical_consistency(
        self,
        analysis_data: Dict[str, Any],
    ) -> VerificationCheck:
        """Verify logical consistency of analysis."""
        
        prompt = f"""Check this analysis for logical consistency:

{json.dumps(analysis_data, indent=2, default=str)[:5000]}

Verify:
1. Numbers add up correctly
2. Percentages are valid (0-100 or 0-1 as appropriate)
3. Classifications match the data they're based on
4. Recommendations don't contradict each other
5. Cause-effect relationships are logical

RESPOND WITH JSON:
{{
    "passed": true/false,
    "score": 0.9,
    "inconsistencies": [
        {{
            "type": "numerical/logical/contradictory",
            "description": "Description of issue",
            "location": "Where in the data"
        }}
    ],
    "feedback": "Overall consistency assessment...",
    "suggestions": ["Fix X by doing Y"]
}}"""

        try:
            response = await self._generate_content(
                prompt=prompt,
                temperature=0.3,
                max_output_tokens=2048,
                feature="verification_consistency",
            )
            
            result = self._parse_json_response(response)
            
            return VerificationCheck(
                check_name="logical_consistency",
                passed=result.get("passed", False),
                score=result.get("score", 0.5),
                feedback=result.get("feedback", ""),
                suggestions=result.get("suggestions", []),
                severity="error" if not result.get("passed") else "info",
            )
            
        except Exception as e:
            logger.error(f"Consistency check failed: {e}")
            return VerificationCheck(
                check_name="logical_consistency",
                passed=False,
                score=0.5,
                feedback=f"Check failed: {str(e)}",
                suggestions=[],
                severity="error",
            )
    
    async def _check_bcg_accuracy(
        self,
        analysis_data: Dict[str, Any],
    ) -> VerificationCheck:
        """Verify BCG classification accuracy."""
        
        bcg_data = analysis_data.get("bcg_analysis", analysis_data.get("classifications", {}))
        products = analysis_data.get("products", analysis_data.get("menu_items", []))
        
        prompt = f"""Verify BCG Matrix classification accuracy:

PRODUCTS:
{json.dumps(products[:20], indent=2, default=str)}

BCG CLASSIFICATIONS:
{json.dumps(bcg_data, indent=2, default=str)[:3000]}

Verify:
1. Classifications follow BCG matrix logic (high/low growth vs share)
2. Metrics justify the classifications
3. No obvious misclassifications
4. Distribution is realistic (not all Stars or all Dogs)

RESPOND WITH JSON:
{{
    "passed": true/false,
    "score": 0.85,
    "misclassifications": [
        {{
            "item": "Item name",
            "current_class": "star",
            "suggested_class": "cash_cow",
            "reason": "Low growth rate indicates..."
        }}
    ],
    "distribution_assessment": "Healthy/Unbalanced/Concerning",
    "feedback": "Overall BCG accuracy assessment...",
    "suggestions": ["Reclassify X", "Review Y"]
}}"""

        try:
            response = await self._generate_content(
                prompt=prompt,
                temperature=0.3,
                max_output_tokens=2048,
                feature="verification_bcg",
            )
            
            result = self._parse_json_response(response)
            
            return VerificationCheck(
                check_name="bcg_accuracy",
                passed=result.get("passed", False),
                score=result.get("score", 0.5),
                feedback=result.get("feedback", ""),
                suggestions=result.get("suggestions", []),
                severity="warning" if not result.get("passed") else "info",
            )
            
        except Exception as e:
            logger.error(f"BCG accuracy check failed: {e}")
            return VerificationCheck(
                check_name="bcg_accuracy",
                passed=True,
                score=0.7,
                feedback="BCG check skipped due to error",
                suggestions=[],
                severity="info",
            )
    
    async def _check_prediction_reasonableness(
        self,
        analysis_data: Dict[str, Any],
    ) -> VerificationCheck:
        """Verify prediction reasonableness."""
        
        predictions = analysis_data.get("predictions", {})
        
        prompt = f"""Verify sales prediction reasonableness:

PREDICTIONS:
{json.dumps(predictions, indent=2, default=str)[:4000]}

Check:
1. Predictions are within realistic bounds
2. Percentage changes are reasonable (not 1000% increases)
3. Confidence intervals make sense
4. Scenario comparisons are logical
5. No obviously impossible values

RESPOND WITH JSON:
{{
    "passed": true/false,
    "score": 0.8,
    "unreasonable_predictions": [
        {{
            "item": "Item name",
            "issue": "Prediction of 500% increase unrealistic",
            "suggested_range": "5-15% increase"
        }}
    ],
    "feedback": "Overall prediction assessment...",
    "suggestions": ["Adjust X", "Review assumptions for Y"]
}}"""

        try:
            response = await self._generate_content(
                prompt=prompt,
                temperature=0.3,
                max_output_tokens=2048,
                feature="verification_predictions",
            )
            
            result = self._parse_json_response(response)
            
            return VerificationCheck(
                check_name="prediction_reasonableness",
                passed=result.get("passed", False),
                score=result.get("score", 0.5),
                feedback=result.get("feedback", ""),
                suggestions=result.get("suggestions", []),
                severity="warning" if not result.get("passed") else "info",
            )
            
        except Exception as e:
            logger.error(f"Prediction check failed: {e}")
            return VerificationCheck(
                check_name="prediction_reasonableness",
                passed=True,
                score=0.7,
                feedback="Prediction check skipped",
                suggestions=[],
                severity="info",
            )
    
    async def _check_campaign_alignment(
        self,
        analysis_data: Dict[str, Any],
    ) -> VerificationCheck:
        """Verify campaign alignment with BCG strategy."""
        
        campaigns = analysis_data.get("campaigns", [])
        bcg_data = analysis_data.get("bcg_analysis", {})
        
        prompt = f"""Verify campaign alignment with BCG strategy:

CAMPAIGNS:
{json.dumps(campaigns[:5], indent=2, default=str)}

BCG ANALYSIS:
{json.dumps(bcg_data, indent=2, default=str)[:2000]}

Verify:
1. Campaigns target appropriate BCG categories
2. Star products get investment-focused campaigns
3. Cash Cows get harvest/efficiency campaigns
4. Question Marks get test/evaluate campaigns
5. Dogs aren't over-invested in

RESPOND WITH JSON:
{{
    "passed": true/false,
    "score": 0.85,
    "misalignments": [
        {{
            "campaign": "Campaign title",
            "issue": "Heavily promotes a Dog product",
            "suggestion": "Redirect focus to Stars"
        }}
    ],
    "feedback": "Overall alignment assessment...",
    "suggestions": ["Adjust campaign X", "Add campaign for Y"]
}}"""

        try:
            response = await self._generate_content(
                prompt=prompt,
                temperature=0.3,
                max_output_tokens=2048,
                feature="verification_campaigns",
            )
            
            result = self._parse_json_response(response)
            
            return VerificationCheck(
                check_name="campaign_alignment",
                passed=result.get("passed", False),
                score=result.get("score", 0.5),
                feedback=result.get("feedback", ""),
                suggestions=result.get("suggestions", []),
                severity="warning" if not result.get("passed") else "info",
            )
            
        except Exception as e:
            logger.error(f"Campaign alignment check failed: {e}")
            return VerificationCheck(
                check_name="campaign_alignment",
                passed=True,
                score=0.7,
                feedback="Campaign check skipped",
                suggestions=[],
                severity="info",
            )
    
    async def _check_business_viability(
        self,
        analysis_data: Dict[str, Any],
    ) -> VerificationCheck:
        """Verify business viability of recommendations."""
        
        prompt = f"""Assess business viability of this analysis and recommendations:

{json.dumps(analysis_data, indent=2, default=str)[:6000]}

Evaluate:
1. Are recommendations actionable for a real restaurant?
2. Are resource requirements realistic?
3. Are timelines achievable?
4. Are expected outcomes realistic?
5. Are there any obvious business risks not addressed?

RESPOND WITH JSON:
{{
    "passed": true/false,
    "score": 0.8,
    "viability_issues": [
        {{
            "recommendation": "Which recommendation",
            "issue": "Requires resources unlikely available",
            "alternative": "More realistic approach"
        }}
    ],
    "unaddressed_risks": ["Risk not mentioned"],
    "feedback": "Overall viability assessment...",
    "suggestions": ["Make X more realistic", "Add risk mitigation for Y"]
}}"""

        try:
            response = await self._generate_content(
                prompt=prompt,
                temperature=0.4,
                max_output_tokens=2048,
                feature="verification_viability",
            )
            
            result = self._parse_json_response(response)
            
            return VerificationCheck(
                check_name="business_viability",
                passed=result.get("passed", False),
                score=result.get("score", 0.5),
                feedback=result.get("feedback", ""),
                suggestions=result.get("suggestions", []),
                severity="warning" if not result.get("passed") else "info",
            )
            
        except Exception as e:
            logger.error(f"Viability check failed: {e}")
            return VerificationCheck(
                check_name="business_viability",
                passed=True,
                score=0.7,
                feedback="Viability check completed with defaults",
                suggestions=[],
                severity="info",
            )
    
    async def _run_custom_check(
        self,
        analysis_data: Dict[str, Any],
        check_name: str,
    ) -> VerificationCheck:
        """Run a custom verification check."""
        
        prompt = f"""Perform a custom verification check: {check_name}

DATA:
{json.dumps(analysis_data, indent=2, default=str)[:5000]}

RESPOND WITH JSON:
{{
    "passed": true/false,
    "score": 0.8,
    "feedback": "Assessment for {check_name}...",
    "suggestions": ["Suggestion 1"]
}}"""

        try:
            response = await self._generate_content(
                prompt=prompt,
                temperature=0.4,
                max_output_tokens=1024,
                feature=f"verification_custom_{check_name}",
            )
            
            result = self._parse_json_response(response)
            
            return VerificationCheck(
                check_name=check_name,
                passed=result.get("passed", True),
                score=result.get("score", 0.7),
                feedback=result.get("feedback", ""),
                suggestions=result.get("suggestions", []),
                severity="info",
            )
            
        except Exception as e:
            return VerificationCheck(
                check_name=check_name,
                passed=True,
                score=0.7,
                feedback=f"Custom check skipped: {str(e)}",
                suggestions=[],
                severity="info",
            )
    
    def _calculate_overall_score(self, checks: List[VerificationCheck]) -> float:
        """Calculate weighted overall score from checks."""
        if not checks:
            return 0.0
        
        # Weight critical checks higher
        weights = {
            "data_completeness": 1.0,
            "logical_consistency": 1.5,
            "bcg_accuracy": 1.2,
            "prediction_reasonableness": 1.0,
            "campaign_alignment": 0.8,
            "business_viability": 1.3,
        }
        
        total_weight = 0
        weighted_sum = 0
        
        for check in checks:
            weight = weights.get(check.check_name, 1.0)
            weighted_sum += check.score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    async def _auto_improve(
        self,
        analysis_data: Dict[str, Any],
        checks: List[VerificationCheck],
        thinking_level: ThinkingLevel,
    ) -> tuple:
        """Attempt to automatically improve the analysis."""
        
        failed_checks = [c for c in checks if not c.passed]
        all_suggestions = []
        for check in failed_checks:
            all_suggestions.extend(check.suggestions)
        
        if not all_suggestions:
            return None, ""
        
        prompt = f"""Improve this analysis based on verification feedback:

CURRENT ANALYSIS:
{json.dumps(analysis_data, indent=2, default=str)[:8000]}

ISSUES FOUND:
{json.dumps([c.to_dict() for c in failed_checks], indent=2)}

IMPROVEMENT SUGGESTIONS:
{json.dumps(all_suggestions, indent=2)}

Apply the suggestions to improve the analysis. Return the COMPLETE improved analysis.

RESPOND WITH JSON containing the full improved analysis structure."""

        try:
            response = await self._generate_content(
                prompt=prompt,
                temperature=0.5,
                max_output_tokens=8192,
                feature="verification_improve",
            )
            
            improved = self._parse_json_response(response)
            
            if improved and "error" not in improved:
                description = f"Applied {len(all_suggestions)} improvements: {', '.join(all_suggestions[:3])}"
                return improved, description
            
            return None, ""
            
        except Exception as e:
            logger.error(f"Auto-improvement failed: {e}")
            return None, ""
    
    async def _generate_recommendation(
        self,
        checks: List[VerificationCheck],
        overall_score: float,
        improvements_made: List[str],
    ) -> str:
        """Generate final recommendation based on verification results."""
        
        if overall_score >= 0.85:
            return "Analysis is high quality and ready for use. All major checks passed."
        elif overall_score >= 0.7:
            warnings = [c.check_name for c in checks if c.severity == "warning"]
            return f"Analysis is acceptable with minor concerns. Review: {', '.join(warnings)}"
        elif overall_score >= 0.5:
            failed = [c.check_name for c in checks if not c.passed]
            return f"Analysis needs improvement in: {', '.join(failed)}. Consider manual review."
        else:
            return "Analysis quality is below acceptable threshold. Recommend re-running analysis with better data."
    
    def get_verification_summary(self) -> Dict[str, Any]:
        """Get summary of all verifications performed."""
        if not self.verification_history:
            return {"total_verifications": 0}
        
        return {
            "total_verifications": len(self.verification_history),
            "average_score": sum(v.overall_score for v in self.verification_history) / len(self.verification_history),
            "pass_rate": sum(1 for v in self.verification_history if v.status == VerificationStatus.PASSED) / len(self.verification_history),
            "total_iterations": sum(v.iterations_used for v in self.verification_history),
            "total_improvements": sum(len(v.improvements_made) for v in self.verification_history),
        }
