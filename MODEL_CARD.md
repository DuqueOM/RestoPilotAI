# Model Card — RestoPilotAI

> Comprehensive documentation of all AI and ML models used in the RestoPilotAI platform.

**Version**: 1.0.0  
**Last Updated**: 2026-02-06  
**Framework**: Google Gemini 3 API + PyTorch + scikit-learn/XGBoost

---

## 1. Model Overview

RestoPilotAI uses a **hybrid AI architecture** combining:
- **Large Language Models (LLMs)** — Google Gemini 3 Pro for reasoning, multimodal analysis, and generation
- **Traditional ML** — XGBoost for feature-engineered sales prediction
- **Deep Learning** — PyTorch LSTM/Transformer for time-series forecasting
- **Native Image Generation** — Gemini 3 Pro Image for campaign visual assets

---

## 2. Gemini 3 Models

### 2.1 Gemini 3 Pro Preview (`gemini-3-pro-preview`)

| Attribute | Value |
|-----------|-------|
| **Provider** | Google DeepMind |
| **Model ID** | `gemini-3-pro-preview` |
| **Type** | Multimodal LLM (text, image, audio, video, PDF) |
| **Context Window** | 128,000 tokens (input) |
| **Max Output** | Up to 16,384 tokens (task-dependent) |
| **Role in System** | Primary model for ALL reasoning tasks |

**Used For**:
- Menu extraction from images/PDFs (DEEP thinking, 8192 tokens)
- BCG matrix classification and menu engineering (DEEP thinking, 8192 tokens)
- Competitive analysis with Google Search grounding (EXHAUSTIVE thinking, 16384 tokens)
- Sentiment analysis from reviews and photos (DEEP thinking, 8192 tokens)
- Campaign strategy and copywriting (EXHAUSTIVE thinking, 8192 tokens)
- Video analysis — restaurant environment, kitchen, service (EXHAUSTIVE thinking, 16384 tokens)
- Audio transcription and context extraction (DEEP thinking, 8192 tokens)
- Multi-agent debate for higher-quality conclusions
- Self-verification and hallucination detection
- Vibe Engineering quality assurance loops
- Conversational chat with session context

**Configuration by Task**:

| Task | Thinking Level | Temperature | Max Output Tokens |
|------|---------------|-------------|-------------------|
| Menu Extraction | DEEP | 0.7 | 8,192 |
| Dish Photo Analysis | DEEP | 0.7 | 8,192 |
| BCG Classification | DEEP | 0.7 | 8,192 |
| Competitive Intelligence | EXHAUSTIVE | 0.8 | 16,384 |
| Sentiment Analysis | DEEP | 0.7 | 8,192 |
| Campaign Strategy | EXHAUSTIVE | 0.8 | 8,192 |
| Video Analysis | EXHAUSTIVE | 0.8 | 16,384 |
| Audio Context | DEEP | 0.7 | 8,192 |
| Quick Formatting | QUICK | 0.3 | 2,048 |
| Standard Tasks | STANDARD | 0.5 | 4,096 |

**Grounding**: When enabled, uses Google Search integration for competitive intelligence, pricing benchmarks, and trend research. Auto-cites web sources in responses.

### 2.2 Gemini 3 Pro Image Preview (`gemini-3-pro-image-preview`)

| Attribute | Value |
|-----------|-------|
| **Provider** | Google DeepMind |
| **Model ID** | `gemini-3-pro-image-preview` |
| **Type** | Multimodal generation (text + image output) |
| **Modalities** | `['IMAGE', 'TEXT']` response modalities |
| **Role in System** | Campaign visual asset generation |

**Used For**:
- Marketing campaign image generation (Instagram posts, stories, web banners, flyers)
- A/B variant generation for creative testing
- Multi-language visual localization
- Menu style transformation

**Generation Config**:
```python
config = types.GenerateContentConfig(
    response_modalities=['IMAGE', 'TEXT'],
    temperature=0.9,
    top_p=0.9
)
```

**Output**: Base64-encoded images with graceful fallback on generation failure.

### 2.3 Gemini 2.0 Flash Exp (`gemini-2.0-flash-exp`)

| Attribute | Value |
|-----------|-------|
| **Model ID** | `gemini-2.0-flash-exp` |
| **Role** | Emergency fallback only |
| **When Used** | If both Gemini 3 Pro and Flash fail after all retries |

---

## 3. Model Fallback Chain

```
gemini-3-pro-preview (Primary)
  ↓ on failure (3 retries with exponential backoff)
gemini-3-pro-preview (Retry with different parameters)
  ↓ on persistent failure
gemini-2.0-flash-exp (Emergency fallback)
```

**Retry Configuration**:
- Max retries: 3
- Backoff factor: 2.0 (exponential)
- Rate limit: 15 RPM, 1M TPM
- Max concurrent requests: 3
- Standard timeout: 120s
- Marathon timeout: 600s (10 min)

---

## 4. Traditional ML Models

### 4.1 XGBoost Sales Predictor

| Attribute | Value |
|-----------|-------|
| **Library** | XGBoost 2.0.3 |
| **Type** | Gradient Boosted Regression |
| **Training** | Per-session, on uploaded sales data |
| **Prediction Horizon** | Configurable, default 14 days |

**Features Engineered**:
- Day of week (0-6)
- Weekend flag
- Holiday flag
- Promotion active / discount percentage
- Rolling averages (7-day, 14-day, 30-day)
- Lag features (t-1, t-7)
- Month, quarter, year
- Weather conditions (if available)

**Output**: Daily unit predictions with confidence intervals per menu item.

### 4.2 Neural Predictor (LSTM)

| Attribute | Value |
|-----------|-------|
| **Library** | PyTorch 2.1+ |
| **Architecture** | LSTM (Long Short-Term Memory) |
| **Training** | Per-session, configurable epochs |
| **Epochs** | 30 (default) |
| **Batch Size** | 32 |

**Purpose**: Sequence-based demand forecasting when sufficient historical data is available. Captures temporal dependencies that XGBoost may miss.

### 4.3 Neural Predictor (Transformer)

| Attribute | Value |
|-----------|-------|
| **Library** | PyTorch 2.1+ |
| **Architecture** | Attention-based Transformer |
| **Purpose** | Alternative to LSTM for longer sequences |

**Purpose**: Attention-based time-series prediction for complex seasonal patterns.

### 4.4 BCG Classifier

| Attribute | Value |
|-----------|-------|
| **Type** | Hybrid (statistical + AI) |
| **Classification** | Star, Cash Cow, Question Mark, Dog |
| **Thresholds** | 75th percentile for high share/growth (configurable) |

**Method**: Combines statistical analysis of sales data (market share, growth rate, contribution margin) with Gemini AI reasoning for strategic context and recommendations.

---

## 5. Intended Use

### Primary Use Case
AI-powered competitive intelligence and menu optimization for small and medium restaurants.

### Intended Users
- Restaurant owners and managers
- Food & beverage consultants
- Restaurant chains (multi-location analysis)

### Out-of-Scope Uses
- This system is NOT designed for:
  - Financial trading or investment decisions
  - Medical or health-related food safety analysis
  - Legal compliance verification
  - Real-time pricing automation without human oversight

---

## 6. Training Data

### Gemini 3 Models
- Pre-trained by Google DeepMind on diverse internet data
- No fine-tuning performed by RestoPilotAI
- All task-specific behavior is via prompting (zero-shot and few-shot)

### XGBoost / Neural Models
- Trained per-session on user-uploaded sales data
- No pre-trained weights shipped with the application
- Models are ephemeral (created per analysis, not persisted across sessions)

---

## 7. Evaluation & Performance

### Gemini 3 Quality Assurance
- **Vibe Engineering** quality threshold: 0.85 (configurable)
- **Self-verification** loop detects inconsistencies and hallucinations
- **Multi-agent debate** for contested analytical conclusions
- **Grounding verification** cross-references claims against Google Search

### Sales Prediction Metrics
- **MAE** (Mean Absolute Error) — reported per prediction
- **MAPE** (Mean Absolute Percentage Error) — reported per prediction
- **R²** (Coefficient of Determination) — reported per prediction
- Actual metrics depend on data quality and volume

### BCG Classification
- Validated against menu engineering literature thresholds
- AI reasoning provides confidence score (0-1) per classification
- Thought signatures document all assumptions

---

## 8. Limitations & Biases

### Known Limitations

1. **Language Bias** — Gemini 3 performs best in English; Spanish and other languages may have reduced accuracy for nuanced restaurant terminology
2. **Geographic Bias** — Google Maps data availability varies by region; rural areas may have sparse competitor data
3. **Temporal Bias** — Predictions are based on historical patterns and may not account for unprecedented events
4. **Image Generation** — Campaign images may not perfectly represent specific dishes or restaurant aesthetics
5. **Review Bias** — Sentiment analysis is limited to publicly available Google Maps reviews, which may not represent all customers

### Mitigation Strategies

- **Thought Signatures** make all assumptions explicit and auditable
- **Confidence Scores** allow users to assess reliability
- **Google Search Grounding** reduces hallucination in competitive analysis
- **Self-Verification** catches internally inconsistent conclusions
- **Human-in-the-loop** — all recommendations require human review before action

---

## 9. Ethical Considerations

- **Transparency** — All AI reasoning is exposed via thought signatures
- **No PII Collection** — System analyzes publicly available business data only
- **Competitor Data** — Only publicly accessible information (Google Maps, web search) is used
- **No Automated Decisions** — All outputs are recommendations requiring human approval
- **Cost Control** — Budget limits prevent runaway API costs ($50/day default cap)

---

## 10. Cost & Resource Usage

### Gemini API Costs (approximate)
| Resource | Cost |
|----------|------|
| Input tokens | $0.01 per 1M tokens |
| Output tokens | $0.03 per 1M tokens |
| Image generation | Included in API usage |
| Google Search grounding | Included in API usage |

### Typical Analysis Cost
- Full pipeline (17 stages): ~$0.50 - $2.00
- Single BCG analysis: ~$0.10 - $0.30
- Campaign generation with images: ~$0.20 - $0.50
- Daily budget cap: $50.00 (configurable)

### Resource Requirements
- **Backend**: 2GB RAM minimum, 4GB recommended
- **GPU**: Not required (PyTorch runs on CPU for small datasets)
- **Storage**: ~500MB for application + variable for uploads/cache

---

## 11. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-06 | Initial release with Gemini 3 Pro (all models upgraded from Flash to Pro) |

---

## 12. Contact

For questions about model behavior, performance, or ethical concerns:
- **Repository**: [RestoPilotAI on GitHub](https://github.com/RestoPilotAI/RestoPilotAI)
- **License**: MIT
