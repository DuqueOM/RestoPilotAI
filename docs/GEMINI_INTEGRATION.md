# Gemini 3 Integration Guide

## Overview

MenuPilot leverages **Google Gemini 3's** advanced capabilities through a modular, production-ready agent architecture. This document details how each Gemini feature is used and integrated.

### Hackathon Highlights 🏆

| Feature | Gemini 3 Capability Used |
|---------|-------------------------|
| **Marathon Agent** | 1M token context window for long-term restaurant memory |
| **Business Profiling** | Multimodal understanding of voice/text business context |
| **Multi-PDF Menus** | Vision API for multi-page PDF processing |
| **Professional BCG** | Deep reasoning for gross profit analysis |
| **Personalized Campaigns** | Function calling for specific, actionable recommendations |
| **Agent Dashboard** | Real-time thought trace visualization |
| **Vibe Engineering** | Self-verification with auto-correction loop |

## Agent Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     GeminiBaseAgent                                 │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │ Core Infrastructure:                                       │     │
│  │ • Retry logic with exponential backoff                     │     │
│  │ • Rate limiting (token bucket algorithm)                   │     │
│  │ • Response caching with TTL                                │     │
│  │ • Token usage tracking & cost estimation                   │     │
│  │ • Error handling & recovery                                │     │
│  └────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────────────┐
│ Multimodal    │   │ Reasoning     │   │ Verification          │
│ Agent         │   │ Agent         │   │ Agent                 │
├───────────────┤   ├───────────────┤   ├───────────────────────┤
│ • Menu OCR    │   │ • BCG Strategy│   │ • Self-verification   │
│ • Dish photos │   │ • Competitive │   │ • Quality thresholds  │
│ • Competitor  │   │ • Predictions │   │ • Auto-improvement    │
│   extraction  │   │ • Campaigns   │   │ • Confidence scores   │
└───────────────┘   └───────────────┘   └───────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Orchestrator    │
                    │ Agent           │
                    ├─────────────────┤
                    │ • Pipeline      │
                    │   coordination  │
                    │ • Checkpoints   │
                    │ • WebSocket     │
                    │   progress      │
                    └─────────────────┘
```

## Gemini 3 Features Used

### 1. Multimodal Vision (gemini-2.0-flash)

**Menu Extraction**
```python
from app.services.gemini import MultimodalAgent

agent = MultimodalAgent()
result = await agent.extract_menu_from_image(
    image_source=menu_image_bytes,
    additional_context="Mexican restaurant in Mexico City",
    language_hint="es"
)
# Returns: items[], categories[], extraction_quality{}
```

**Dish Photo Analysis**
```python
analysis = await agent.analyze_dish_image(
    image_source=dish_photo,
    dish_name="Tacos al Pastor",
    menu_context=["Tacos al Pastor", "Guacamole", ...]
)
# Returns: visual_scores{}, marketability{}, improvement_suggestions[]
```

**Competitor Menu Extraction**
```python
competitor_data = await agent.extract_competitor_menu(
    image_source=competitor_menu_image,
    competitor_name="La Taqueria"
)
# Returns: items[], pricing_analysis{}, competitive_observations[]
```

### 2. Deep Reasoning (gemini-2.0-flash / gemini-2.5-pro-preview)

**Thinking Levels**
```python
from app.services.gemini import ThinkingLevel

# Quick analysis (fast, surface-level)
await agent.analyze(..., thinking_level=ThinkingLevel.QUICK)

# Standard analysis (balanced)
await agent.analyze(..., thinking_level=ThinkingLevel.STANDARD)

# Deep analysis (multi-perspective)
await agent.analyze(..., thinking_level=ThinkingLevel.DEEP)

# Exhaustive analysis (comprehensive with verification)
await agent.analyze(..., thinking_level=ThinkingLevel.EXHAUSTIVE)
```

**BCG Strategic Analysis**
```python
from app.services.gemini import ReasoningAgent

reasoning = ReasoningAgent()
result = await reasoning.analyze_bcg_strategy(
    products=menu_items,
    sales_data=historical_sales,
    thinking_level=ThinkingLevel.DEEP
)
# Returns: ReasoningResult with thought_traces[], confidence, analysis{}
```

**Competitive Analysis**
```python
result = await reasoning.analyze_competitive_position(
    our_menu=our_data,
    competitor_menus=competitor_data,
    thinking_level=ThinkingLevel.DEEP
)
# Returns: market_position, price_gaps[], strategic_recommendations[]
```

### 3. Agentic Function Calling

**Autonomous Verification Loop**
```python
from app.services.gemini import GeminiVerificationAgent

verifier = GeminiVerificationAgent()
result = await verifier.verify_analysis(
    analysis_data=complete_analysis,
    thinking_level=ThinkingLevel.EXHAUSTIVE,
    auto_improve=True,  # Automatically fix issues
    custom_checks=["price_reasonableness"]
)
# Iterates until quality threshold met or max iterations
```

**Verification Checks Performed:**
- Data completeness
- Logical consistency
- BCG classification accuracy
- Prediction reasonableness
- Campaign alignment with strategy
- Business viability

### 4. Long Context Handling & Marathon Agent

**Marathon Agent Pattern with Long-Term Memory**

The Marathon Agent leverages Gemini 3's **1M token context window** to maintain persistent memory across sessions, enabling:

- Historical trend analysis across multiple visits
- Strategic recommendations based on past performance
- Campaign effectiveness tracking over time
- Personalized advice that improves with each interaction

```python
from app.services.gemini import OrchestratorAgent, PipelineStage

orchestrator = OrchestratorAgent()

# Create persistent session with long-term context
session_id = await orchestrator.create_session(
    restaurant_id="restaurant_123",
    load_history=True  # Load up to 6 months of past interactions
)

# Marathon Agent context includes:
marathon_context = {
    "session_count": 15,  # Previous sessions
    "total_analyses": 42,
    "long_term_insights": [
        "Restaurant has shown 12% growth in last 3 months",
        "Taco Tuesday campaign increased traffic 18%",
        "Question Marks from Q3 (Birria) evolving to Stars"
    ],
    "memory_context": "Gemini 3 context window (1M tokens) enables 6+ months of strategic memory"
}

# Run with checkpoints for recovery
result = await orchestrator.run_full_pipeline(
    session_id=session_id,
    menu_images=[...],
    sales_csv=csv_content,
    business_context="Restaurante mexicano en zona universitaria, público joven...",
    thinking_level=ThinkingLevel.DEEP,
    auto_verify=True
)

# Resume from last checkpoint if interrupted
result = await orchestrator.resume_session(session_id)
```

**Pipeline Stages:**
1. `MENU_EXTRACTION` - Extract menu items from images
2. `DISH_ANALYSIS` - Analyze dish photos
3. `SALES_PROCESSING` - Process sales data
4. `BCG_CLASSIFICATION` - Strategic classification
5. `COMPETITOR_ANALYSIS` - Competitive intelligence
6. `SENTIMENT_ANALYSIS` - Customer sentiment
7. `SALES_PREDICTION` - Forecast generation
8. `CAMPAIGN_GENERATION` - Marketing campaigns
9. `EXECUTIVE_SUMMARY` - Final summary
10. `VERIFICATION` - Quality assurance

## Rate Limiting & Cost Optimization

### Token Bucket Rate Limiter
```python
# Automatically applied to all Gemini calls
rate_limiter = RateLimiter(
    requests_per_minute=60,
    tokens_per_minute=1_000_000
)
```

### Response Caching
```python
# Responses cached by default (1 hour TTL)
result = await agent.extract_menu(
    image_data,
    use_cache=True  # Default: True
)

# Force fresh request
result = await agent.extract_menu(
    image_data,
    use_cache=False
)
```

### Cost Tracking
```python
# Get usage statistics
stats = agent.get_usage_stats()
print(f"Total tokens: {stats['tokens']['total']}")
print(f"Estimated cost: ${stats['estimated_cost_usd']:.4f}")
print(f"Cache hit rate: {stats['cache_hit_rate']:.1%}")
```

## Thought Signatures

Every AI decision includes transparent reasoning:

```python
# Access thought traces from any reasoning operation
result = await reasoning.analyze_bcg_strategy(...)

for trace in result.thought_traces:
    print(f"Step: {trace.step}")
    print(f"Reasoning: {trace.reasoning}")
    print(f"Observations: {trace.observations}")
    print(f"Decisions: {trace.decisions}")
    print(f"Confidence: {trace.confidence:.0%}")
```

## Error Handling

**Automatic Retry with Backoff**
```python
@with_retry(max_attempts=3, base_delay=2.0, max_delay=30.0)
async def _generate_content(...):
    # Automatically retries on:
    # - Rate limit errors (429)
    # - Server errors (5xx)
    # - Temporary failures
```

**Graceful Degradation**
```python
try:
    result = await agent.analyze(...)
except GeminiRateLimitError:
    # Automatic wait and retry
except GeminiAPIError as e:
    # Log and return partial results
    return partial_result_with_error(e)
```

## WebSocket Progress Streaming

```python
# Connect to progress WebSocket
ws = await websocket.connect(f"/api/v1/ws/analysis/{session_id}")

# Receive real-time updates
{
    "type": "progress",
    "stage": "bcg_classification",
    "progress": 45,
    "message": "Running BCG strategic analysis...",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## Environment Configuration

```env
# Required
GEMINI_API_KEY=your_api_key

# Optional - defaults shown
GEMINI_MODEL=gemini-2.0-flash
GEMINI_MAX_RETRIES=3
GEMINI_RATE_LIMIT_RPM=60
GEMINI_RATE_LIMIT_TPM=1000000
GEMINI_CACHE_TTL_SECONDS=3600
```

## Best Practices

1. **Use appropriate thinking levels** - Don't use EXHAUSTIVE for simple tasks
2. **Enable caching** for repeated similar requests
3. **Monitor token usage** to stay within budget
4. **Use checkpoints** for long-running pipelines
5. **Enable auto_verify** for production quality assurance
6. **Stream progress** to provide user feedback during analysis

## Model Selection

| Task | Recommended Model | Thinking Level |
|------|-------------------|----------------|
| Menu extraction | gemini-2.0-flash | STANDARD |
| Dish analysis | gemini-2.0-flash | STANDARD |
| BCG strategy | gemini-2.0-flash | DEEP |
| Competitive analysis | gemini-2.0-flash | DEEP |
| Executive summary | gemini-2.0-flash | EXHAUSTIVE |
| Verification | gemini-2.0-flash | EXHAUSTIVE |
