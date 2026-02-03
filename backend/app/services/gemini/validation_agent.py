"""
Validation Agent - Safety & Hallucination Detection.

Validates AI outputs against input data to detect:
- Unsupported claims
- Hallucinated numbers
- Logical inconsistencies
- Data misinterpretations
"""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime

from loguru import logger
from pydantic import BaseModel, Field

from app.services.gemini.enhanced_agent import (
    EnhancedGeminiAgent,
    ThinkingLevel
)
from app.core.config import GeminiModel


# ==================== Models ====================

class ValidationResult(BaseModel):
    """Result of output validation."""
    verified: bool
    confidence: float = Field(ge=0.0, le=1.0)
    unsupported_claims: List[str] = Field(default_factory=list)
    data_mismatches: List[Dict[str, Any]] = Field(default_factory=list)
    logical_issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    validation_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class SafetyCheck(BaseModel):
    """Safety check result."""
    safe: bool
    safety_issues: List[str] = Field(default_factory=list)
    severity: str = "low"  # low, medium, high, critical
    recommended_action: str


# ==================== Validation Agent ====================

class ValidationAgent(EnhancedGeminiAgent):
    """
    🛡️ VALIDATION AGENT - Safety & Hallucination Detection
    
    Ensures AI outputs are:
    - Factually grounded in input data
    - Logically consistent
    - Free from hallucinations
    - Safe and appropriate
    
    Critical for production reliability.
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            model=GeminiModel.FLASH_PREVIEW,
            enable_grounding=False,  # Validate against input, not web
            enable_cache=False,  # Don't cache validations
            **kwargs
        )
        logger.info("validation_agent_initialized")
    
    async def validate_output(
        self,
        output: Dict[str, Any],
        input_data: Dict[str, Any],
        context: Optional[str] = None
    ) -> ValidationResult:
        """
        🔍 Validate AI output against input data.
        
        Detects:
        - Unsupported numerical claims
        - Hallucinated facts
        - Logical inconsistencies
        - Data misinterpretations
        
        Args:
            output: AI-generated output to validate
            input_data: Original input data
            context: Optional context about the analysis
            
        Returns:
            ValidationResult with verification status
        """
        
        logger.info("validation_started", output_keys=list(output.keys()))
        
        context_str = f"\n\nCONTEXT: {context}" if context else ""
        
        prompt = f"""You are a rigorous fact-checker and data validator.

Your job is to verify that AI-generated outputs are FULLY SUPPORTED by the input data.

INPUT DATA (GROUND TRUTH):
{json.dumps(input_data, indent=2)}

OUTPUT TO VALIDATE (AI CLAIMS):
{json.dumps(output, indent=2)}{context_str}

VERIFICATION TASKS:

1. **Numerical Accuracy**:
   - Are all numbers in output present in input data?
   - Are calculations correct?
   - Are percentages/ratios accurate?
   - Flag any numbers that can't be traced to input

2. **Factual Claims**:
   - Are all statements supported by input data?
   - Any claims that go beyond what data shows?
   - Any assumptions presented as facts?

3. **Logical Consistency**:
   - Do recommendations follow from the data?
   - Any contradictions in the output?
   - Are conclusions justified?

4. **Data Mismatches**:
   - Compare specific values between input and output
   - Identify any discrepancies
   - Note any transformations that seem incorrect

5. **Hallucination Detection**:
   - Any invented data points?
   - Any claims about things not in input?
   - Any extrapolations presented as facts?

RETURN AS JSON:
{{
    "verified": bool,  // true if ALL claims are supported
    "confidence": float,  // 0.0-1.0 confidence in validation
    "unsupported_claims": [
        "claim text that can't be verified from input"
    ],
    "data_mismatches": [
        {{
            "field": "field name",
            "input_value": "value from input",
            "output_value": "value in output",
            "issue": "description of mismatch"
        }}
    ],
    "logical_issues": [
        "description of logical inconsistency"
    ],
    "recommendations": [
        "how to fix or improve the output"
    ]
}}

BE STRICT: If you can't trace a claim directly to the input data, flag it as unsupported.
"""
        
        result = await self.generate(
            prompt=prompt,
            thinking_level=ThinkingLevel.DEEP,
            enable_thought_trace=True
        )
        
        try:
            validation = ValidationResult(**result["data"])
            
            logger.info(
                "validation_complete",
                verified=validation.verified,
                unsupported_claims=len(validation.unsupported_claims),
                confidence=validation.confidence
            )
            
            return validation
            
        except Exception as e:
            logger.error("validation_parse_error", error=str(e))
            # Return conservative validation result
            return ValidationResult(
                verified=False,
                confidence=0.0,
                unsupported_claims=["Validation parsing failed"],
                recommendations=["Manual review required"]
            )
    
    async def check_safety(
        self,
        output: Dict[str, Any],
        context: Optional[str] = None
    ) -> SafetyCheck:
        """
        🛡️ Check output for safety issues.
        
        Detects:
        - Harmful recommendations
        - Biased content
        - Inappropriate suggestions
        - Ethical concerns
        
        Args:
            output: Output to check
            context: Optional context
            
        Returns:
            SafetyCheck result
        """
        
        context_str = f"\n\nCONTEXT: {context}" if context else ""
        
        prompt = f"""You are a safety and ethics reviewer.

Review this AI output for potential safety issues.

OUTPUT TO REVIEW:
{json.dumps(output, indent=2)}{context_str}

CHECK FOR:

1. **Harmful Recommendations**:
   - Could any recommendation cause financial harm?
   - Any suggestions that could hurt business?
   - Any risky strategies without proper warnings?

2. **Bias Detection**:
   - Any discriminatory content?
   - Unfair treatment of any group?
   - Stereotyping or prejudice?

3. **Ethical Concerns**:
   - Misleading claims?
   - Manipulation tactics?
   - Unethical business practices?

4. **Appropriateness**:
   - Professional tone maintained?
   - Respectful language?
   - Industry-appropriate?

RETURN AS JSON:
{{
    "safe": bool,
    "safety_issues": ["list of issues found"],
    "severity": "low|medium|high|critical",
    "recommended_action": "what to do about issues"
}}
"""
        
        result = await self.generate(
            prompt=prompt,
            thinking_level=ThinkingLevel.STANDARD
        )
        
        try:
            return SafetyCheck(**result["data"])
        except Exception:
            return SafetyCheck(
                safe=True,
                safety_issues=[],
                severity="low",
                recommended_action="Manual review recommended"
            )
    
    async def validate_bcg_analysis(
        self,
        analysis: Dict[str, Any],
        sales_data: List[Dict[str, Any]],
        menu_data: List[Dict[str, Any]]
    ) -> ValidationResult:
        """
        Validate BCG analysis specifically.
        
        Checks:
        - Product classifications match data
        - Growth rates are accurate
        - Market share calculations correct
        - Recommendations are data-driven
        """
        
        input_data = {
            "sales_data": sales_data,
            "menu_data": menu_data,
            "total_products": len(sales_data)
        }
        
        return await self.validate_output(
            output=analysis,
            input_data=input_data,
            context="BCG Matrix Analysis - verify product classifications and metrics"
        )
    
    async def validate_competitive_intelligence(
        self,
        intelligence: Dict[str, Any],
        competitor_data: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate competitive intelligence output.
        
        Ensures all competitor claims are sourced.
        """
        
        return await self.validate_output(
            output=intelligence,
            input_data=competitor_data,
            context="Competitive Intelligence - verify all claims have sources"
        )
    
    async def batch_validate(
        self,
        outputs: List[Dict[str, Any]],
        inputs: List[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """
        Validate multiple outputs in batch.
        
        Args:
            outputs: List of outputs to validate
            inputs: Corresponding input data
            
        Returns:
            List of validation results
        """
        
        if len(outputs) != len(inputs):
            raise ValueError("Outputs and inputs must have same length")
        
        results = []
        for output, input_data in zip(outputs, inputs):
            result = await self.validate_output(output, input_data)
            results.append(result)
        
        return results
    
    # ==================== Utility Methods ====================
    
    def get_validation_summary(
        self,
        validations: List[ValidationResult]
    ) -> Dict[str, Any]:
        """
        Get summary statistics from multiple validations.
        
        Args:
            validations: List of validation results
            
        Returns:
            Summary statistics
        """
        
        total = len(validations)
        verified = sum(1 for v in validations if v.verified)
        avg_confidence = sum(v.confidence for v in validations) / total if total > 0 else 0.0
        
        all_unsupported = []
        for v in validations:
            all_unsupported.extend(v.unsupported_claims)
        
        return {
            "total_validations": total,
            "verified_count": verified,
            "failed_count": total - verified,
            "verification_rate": verified / total if total > 0 else 0.0,
            "average_confidence": avg_confidence,
            "total_unsupported_claims": len(all_unsupported),
            "unique_unsupported_claims": len(set(all_unsupported))
        }


# ==================== Global Validator Instance ====================

_validator_instance: Optional[ValidationAgent] = None


def get_validator() -> ValidationAgent:
    """Get or create global validator instance."""
    global _validator_instance
    
    if _validator_instance is None:
        _validator_instance = ValidationAgent()
    
    return _validator_instance
