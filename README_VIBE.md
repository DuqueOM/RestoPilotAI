# Vibe Engineering - Autonomous Quality Assurance

This document details the implementation of **Vibe Engineering** in RestoPilotAI, a loop-based autonomous system that verifies and improves AI analysis quality using Gemini 3.

## 🔄 The Loop

The Vibe Engineering loop (`verify_and_improve_analysis`) operates autonomously:

1.  **Verification**: The AI acts as a critical auditor, evaluating the analysis against 4 dimensions:
    *   **Precision**: Factual and calculation accuracy.
    *   **Completeness**: Coverage of required aspects.
    *   **Applicability**: Actionability of recommendations.
    *   **Clarity**: Communication quality.
2.  **Decision**: If the `quality_score` is below the threshold (0.85), the improvement process triggers.
3.  **Improvement**: The AI acts as a senior analyst, fixing the specific issues identified by the auditor.
4.  **Iteration**: The improved analysis is re-verified. This continues for up to 3 iterations.

## 🛠️ Implementation Details

### Backend
- **Service**: `backend/app/services/gemini/vibe_engineering.py`
- **Agent**: `VibeEngineeringAgent`
- **Integration**: Integrated into all major analysis endpoints (`/analyze/bcg`, `/predict/sales`, `/campaigns/generate`).

### Frontend
- **Components**:
    - `VerificationPanel`: Shows the current status and overall score.
    - `QualityMetrics`: Visualizes scores for Precision, Completeness, Applicability, and Clarity.
    - `ImprovementHistory`: Displays the timeline of autonomous fixes.
- **Hook**: `useVibeEngineering` manages the verification state.

## 📄 Example Iteration Log

Here is an example of what the system captures during a Vibe Engineering run:

```json
{
  "final_analysis": { ... },
  "quality_achieved": 0.92,
  "iterations_required": 2,
  "auto_improved": true,
  "improvement_iterations": [
    {
      "iteration": 1,
      "timestamp": "2023-10-27T10:00:00Z",
      "quality_before": 0.72,
      "quality_after": 0.92,
      "issues_fixed": [
        "Inconsistent profit margin calculation for 'Tacos Al Pastor'",
        "Recommendation for 'Happy Hour' lacked specific timing details",
        "Missing competitor price comparison in rationale"
      ],
      "duration_ms": 4500
    }
  ],
  "verification_history": [
    {
      "quality_score": 0.72,
      "identified_issues": [
        {
          "issue": "Inconsistent profit margin calculation",
          "severity": "high",
          "suggestion": "Recalculate using cost 25 and price 100"
        }
      ]
    },
    {
      "quality_score": 0.92,
      "identified_issues": [],
      "overall_assessment": "Excellent analysis with precise calculations and actionable advice."
    }
  ]
}
```

## 🚦 Usage

The feature is enabled by default. To control it per request:

```http
POST /api/v1/analyze/bcg
Content-Type: application/json

{
  "session_id": "...",
  "auto_verify": true
}
```

If `auto_verify` is true, the response will include a `vibe_verification` object containing the history and metrics.
