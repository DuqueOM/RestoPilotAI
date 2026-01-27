# Model Card - MenuPilot

## Model Overview

MenuPilot uses two primary model components:

1. **Google Gemini 3** - Multimodal AI for extraction, analysis, and generation
2. **XGBoost Sales Predictor** - Local ML model for sales forecasting

---

## Model 1: Gemini 3 Integration

### Model Details

| Attribute | Value |
|-----------|-------|
| **Model Name** | `gemini-3-flash-preview` |
| **Provider** | Google DeepMind |
| **Type** | Multimodal Large Language Model |
| **Capabilities** | Text, Vision, Function Calling |

### Usage in MenuPilot

| Task | Input | Output |
|------|-------|--------|
| **Menu Extraction** | Menu image + OCR text | Structured item list (JSON) |
| **Dish Analysis** | Dish photograph | Attractiveness scores, quality assessment |
| **BCG Insights** | Product metrics | Strategic recommendations |
| **Campaign Generation** | BCG analysis + constraints | Marketing campaigns with copy |
| **Self-Verification** | Analysis results | Verification checks, corrections |

### Function Calling Tools

```python
tools = [
    "extract_menu",        # OCR + structure extraction
    "analyze_dish_image",  # Visual appeal scoring
    "classify_bcg",        # BCG matrix classification
    "generate_campaign",   # Marketing campaign creation
    "verify_analysis",     # Self-verification step
]
```

### Thought Signatures

Gemini 3 generates transparent reasoning traces:

```json
{
  "plan": ["Step 1: ...", "Step 2: ..."],
  "observations": ["Key finding 1", "Key finding 2"],
  "reasoning": "Main reasoning chain...",
  "assumptions": ["Assumption 1", "Assumption 2"],
  "confidence": 0.85
}
```

### Limitations (Gemini 3)

- **Rate Limits**: Subject to API quotas (see pricing docs)
- **Hallucination**: May generate plausible but incorrect information
- **Context Window**: Large but finite token limit
- **Latency**: Network-dependent response times

---

## Model 2: XGBoost Sales Predictor

### Model Details

| Attribute | Value |
|-----------|-------|
| **Algorithm** | XGBoost Regressor |
| **Library** | `xgboost==2.0.3` |
| **Task** | Sales volume prediction |
| **Output** | Daily unit predictions |

### Hyperparameters

```python
XGBRegressor(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    objective="reg:squarederror",
    random_state=42
)
```

### Features

| Feature | Type | Description |
|---------|------|-------------|
| `day_of_week` | int | 0-6 (Monday-Sunday) |
| `is_weekend` | binary | 1 if Saturday/Sunday |
| `price` | float | Item price |
| `promo_flag` | binary | 1 if promotion active |
| `promo_discount` | float | Discount percentage (0-1) |
| `image_score` | float | Visual attractiveness (0-1) |
| `rolling_avg_7d` | float | 7-day rolling average |
| `rolling_avg_30d` | float | 30-day rolling average |
| `lag_1d` | float | Previous day sales |
| `lag_7d` | float | Sales 7 days ago |

### Training

- **Data Split**: 80% train / 20% test
- **Minimum Samples**: 10 records (uses synthetic data if fewer)
- **Retraining**: Per session with user data

### Evaluation Metrics

| Metric | Description |
|--------|-------------|
| **MAE** | Mean Absolute Error (primary) |
| **RMSE** | Root Mean Squared Error |

### Scenario Predictions

The model supports scenario-based forecasting:

```python
scenarios = [
    {"name": "baseline"},
    {"name": "10%_discount", "promotion_active": True, "promotion_discount": 0.1},
    {"name": "marketing_boost", "marketing_boost": 1.3}
]
```

### Limitations (XGBoost)

- **Cold Start**: New items have no historical data
- **Feature Engineering**: Requires proper date parsing
- **Seasonality**: Limited capture of long-term patterns
- **Overfitting**: Risk with small datasets

---

## Ethical Considerations

### Intended Use
- Small/medium restaurant business optimization
- Marketing decision support (not replacement)
- Menu engineering assistance

### Misuse Potential
- Over-reliance on predictions without business judgment
- Price manipulation without customer consideration
- Using as sole decision-maker for menu changes

### Bias Considerations
- Training data may not represent all cuisine types
- Image attractiveness scores reflect training data biases
- Recommendations based on profitability may neglect nutrition

### Recommendations
- Use as decision support, not automation
- Validate predictions with domain expertise
- Consider factors beyond profit (health, sustainability)
- Monitor for unexpected model behavior

---

## Model Updates

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01 | Initial release with Gemini 3 + XGBoost |

---

## References

- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [BCG Matrix](https://en.wikipedia.org/wiki/Growth%E2%80%93share_matrix)

## Citation

```
@software{menupilot2026,
  title = {MenuPilot: AI-Powered Restaurant Menu Optimization},
  author = {MenuPilot Team},
  year = {2026},
  note = {Built for Gemini 3 Hackathon}
}
```
