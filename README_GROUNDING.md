# RestoPilotAI - Grounding & Thought Signatures

This document outlines the implementation of **Grounding** (using Google Search) and **Thought Signatures** (transparent reasoning traces) in RestoPilotAI, leveraging Gemini 3's capabilities.

## 🧠 Thought Signatures

Thought Signatures provide a transparent window into the AI's reasoning process *before* it executes a task. This ensures alignment with user intent and allows for debugging complex decision-making.

### Implementation
- **Method**: `GeminiBaseAgent.create_thought_signature(task, context)`
- **Output**: A structured JSON object containing:
  - `plan`: Step-by-step execution plan.
  - `observations`: Key insights from the provided context.
  - `reasoning`: The logical chain connecting observations to the plan.
  - `assumptions`: Explicit assumptions made by the agent.
  - `confidence`: Numeric score (0-1) indicating certainty.

### Usage Example
```python
# In any agent method:
await self.create_thought_signature(
    task="Strategic Analysis",
    context={"market_data": ..., "sales": ...},
    thinking_level=ThinkingLevel.DEEP
)
```

## 🌍 Grounding (Google Search)

Grounding connects the AI's analysis to real-time, verifiable information from the web. This is critical for competitive intelligence and market trend analysis.

### Implementation
- **Configuration**: Enabled via `GEMINI_ENABLE_GROUNDING=True` in `config.py`.
- **Method**: `ReasoningAgent.analyze_competitive_position` now supports grounding.
- **Mechanism**:
  1. The agent uses the `GoogleSearch` tool to fetch live data (competitor prices, reviews, local events).
  2. It synthesizes this real-time data with internal knowledge.
  3. The result includes a list of `grounding_sources` (URLs) used for verification.

### Usage Example
```python
result = await reasoning_agent.analyze_competitive_position(
    our_menu=...,
    competitor_menus=...,
    thinking_level=ThinkingLevel.DEEP,
    enable_grounding=True  # Default
)

# Access sources
print(result.analysis["grounding_sources"])
```

## 🛠️ Configuration

Update `.env` or `config.py` to control these features:

```python
# app/core/config.py
GEMINI_ENABLE_GROUNDING: bool = True
GEMINI_ENABLE_STREAMING: bool = True
```

## ✅ Verification

- **Thought Signatures**: Verify that `thought_traces` are populated in the agent's state or returned results.
- **Grounding**: Check `grounding_sources` in the output of competitive analysis. Ensure sources are relevant and recent.
