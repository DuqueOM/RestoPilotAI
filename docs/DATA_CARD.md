# Data Card — RestoPilotAI

> Documentation of all data flows, schemas, sources, storage, and privacy considerations in the RestoPilotAI platform.

**Version**: 1.0.0  
**Last Updated**: 2026-02-06

---

## 1. Data Overview

RestoPilotAI processes **six categories of data**:

| Category | Input Format | Source | Persistence |
|----------|-------------|--------|-------------|
| **Menu Data** | Images (JPG/PNG/WebP), PDF | User upload | Database + file storage |
| **Sales Data** | CSV, XLSX | User upload | Database |
| **Dish Photos** | Images (JPG/PNG/WebP) | User upload | File storage |
| **Audio Context** | MP3, WAV, M4A, OGG, WebM, FLAC, AAC | User upload | File storage |
| **Video Content** | MP4, WebM | User upload | File storage (temporary) |
| **Location Data** | Google Maps API | External API | Database (session-scoped) |

---

## 2. Data Flow Architecture

```
┌─────────────────────┐
│   User Uploads       │
│  (menu, sales, etc.) │
└─────────┬───────────┘
          ↓
┌─────────────────────┐     ┌─────────────────────┐
│   Data Ingestion     │────→│   File Storage       │
│   (validation +      │     │   data/uploads/      │
│    preprocessing)    │     └─────────────────────┘
└─────────┬───────────┘
          ↓
┌─────────────────────┐     ┌─────────────────────┐
│   AI Processing      │←───→│   External APIs      │
│   (Gemini 3 Pro)     │     │   • Gemini API       │
│                      │     │   • Google Maps      │
│   • Menu extraction  │     │   • Google Search    │
│   • Sentiment        │     └─────────────────────┘
│   • BCG analysis     │
│   • Campaigns        │
└─────────┬───────────┘
          ↓
┌─────────────────────┐     ┌─────────────────────┐
│   Results Storage    │────→│   SQLite / PostgreSQL│
│   (structured JSON)  │     │   data/RestoPilotAI.db│
└─────────┬───────────┘     └─────────────────────┘
          ↓
┌─────────────────────┐
│   Frontend Display   │
│   (Dashboard + API)  │
└─────────────────────┘
```

---

## 3. Input Data Schemas

### 3.1 Menu Data

**Accepted Formats**: JPG, JPEG, PNG, WebP, PDF  
**Max File Size**: 10 MB per file  
**Processing**: Gemini 3 Pro multimodal OCR + structured extraction

**Extracted Schema** (`MenuExtractionResponse`):
```json
{
  "session_id": "string (UUID)",
  "status": "success | partial | failed",
  "items_extracted": 42,
  "categories_found": ["Appetizers", "Main Courses", "Desserts"],
  "items": [
    {
      "name": "Filete Mignon",
      "description": "8oz prime beef with truffle sauce",
      "price": 38.50,
      "category": "Main Courses",
      "confidence": 0.95,
      "dietary_tags": ["gluten_free"]
    }
  ],
  "extraction_confidence": 0.92,
  "thought_process": "AI reasoning trace...",
  "warnings": []
}
```

### 3.2 Sales Data

**Accepted Formats**: CSV, XLSX  
**Max File Size**: 10 MB  

**Expected CSV Columns** (flexible — AI adapts to variations):

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `item_name` / `producto` / `dish` | string | Yes | Menu item name |
| `sale_date` / `fecha` / `date` | date | Yes | Date of sale |
| `units_sold` / `cantidad` / `quantity` | integer | Yes | Units sold |
| `revenue` / `ingreso` / `total` | float | No | Revenue amount |
| `price` / `precio` | float | No | Unit price |
| `cost` / `costo` | float | No | Unit cost |
| `category` / `categoria` | string | No | Item category |
| `promotion` / `promocion` | boolean | No | Promotion active |
| `discount` / `descuento` | float | No | Discount percentage |

**Stored Schema** (`SalesRecord` ORM model):
```python
class SalesRecord:
    id: int                          # Auto-incremented PK
    session_id: str                  # Session UUID
    item_name: str                   # Menu item name
    sale_date: date                  # Sale date
    units_sold: int                  # Quantity sold
    revenue: float | None            # Total revenue
    day_of_week: int                 # 0=Monday, 6=Sunday
    is_weekend: bool                 # Derived from day_of_week
    is_holiday: bool                 # Holiday flag
    had_promotion: bool              # Promotion active
    promotion_discount: float | None # Discount %
    weather_condition: str | None    # Weather (if available)
    temperature: float | None        # Temperature (if available)
```

### 3.3 Dish Photos

**Accepted Formats**: JPG, JPEG, PNG, WebP  
**Max File Size**: 10 MB per image  
**Processing**: Gemini 3 Pro vision analysis

**Analysis Output**:
- Visual quality score (0-1)
- Presentation assessment
- Color harmony score
- Composition score
- Appeal score
- Portion perception

### 3.4 Audio Context

**Accepted Formats**: MP3, WAV, M4A, OGG, WebM, FLAC, AAC  
**Max File Size**: 10 MB  
**Processing**: Gemini 3 Pro native audio understanding

**Extracted Data**:
- Business context and story
- Target audience description
- Competitive positioning
- Brand values and tone

### 3.5 Video Content

**Accepted Formats**: MP4, WebM  
**Max File Size**: 10 MB  
**Processing**: Gemini 3 Pro native video analysis

**Analysis Output**:
- Content type classification
- Key moments with timestamps
- Visual/audio quality scores
- Platform-specific recommendations (TikTok, Instagram, YouTube)
- Environment assessment (restaurant, kitchen, service)

---

## 4. External Data Sources

### 4.1 Google Maps / Places API

**Data Retrieved**:
| Field | Description |
|-------|-------------|
| `place_id` | Google Maps unique identifier |
| `name` | Business name |
| `address` | Full formatted address |
| `latitude`, `longitude` | Geographic coordinates |
| `rating` | Average star rating (1-5) |
| `user_ratings_total` | Total review count |
| `price_level` | Price tier (1-4) |
| `reviews` | Up to 5 most recent reviews (text + rating) |
| `photos` | Photo references |
| `opening_hours` | Operating schedule |
| `website` | Business website URL |
| `phone_number` | Contact phone |
| `types` | Business type tags |

**API Used**: Legacy Places API (not "Places API (New)")  
**Required Permissions**: Places API, Geocoding API, Maps JavaScript API

### 4.2 Google Search (via Gemini Grounding)

**Data Retrieved**:
- Competitor web presence and descriptions
- Market pricing benchmarks
- Food industry trends
- Source URLs with titles and snippets
- Relevance scores

**Note**: Google Search grounding is performed by Gemini 3 internally — no direct Google Search API calls are made. Sources are auto-cited by the model.

---

## 5. Output Data Schemas

### 5.1 BCG Analysis (`BCGAnalysisResult`)

```json
{
  "session_id": "uuid",
  "status": "success",
  "methodology": "menu_engineering_v2",
  "period": "all_time",
  "total_records": 15420,
  "items_analyzed": 42,
  "thresholds": {
    "popularity_threshold": 2.38,
    "cm_threshold": 45.20,
    "n_items": 42,
    "total_units": 15420
  },
  "items": [
    {
      "name": "Filete Mignon",
      "category": "star",
      "units_sold": 1250,
      "price": 38.50,
      "cost": 15.40,
      "cm_unitario": 23.10,
      "popularity_pct": 8.11,
      "total_contribution": 28875.0,
      "category_label": "⭐ Star",
      "high_popularity": true,
      "high_cm": true,
      "strategy": {
        "action": "Maintain & Protect",
        "priority": "high",
        "recommendations": ["Keep quality consistent", "Feature prominently"],
        "pricing": "Premium pricing justified",
        "menu_position": "Top-right quadrant"
      }
    }
  ],
  "summary": {
    "total_items": 42,
    "total_revenue": 245000.0,
    "categories": [
      {"category": "star", "count": 8, "pct_revenue": 45.2},
      {"category": "cash_cow", "count": 12, "pct_revenue": 30.1},
      {"category": "question_mark", "count": 10, "pct_revenue": 15.5},
      {"category": "dog", "count": 12, "pct_revenue": 9.2}
    ]
  },
  "grounding_sources": [{"uri": "https://...", "title": "..."}],
  "grounded": true
}
```

### 5.2 Sentiment Analysis (`SentimentAnalysisResult`)

```json
{
  "analysis_id": "uuid",
  "overall": {
    "sentiment_score": 0.78,
    "nps": 42,
    "sentiment_distribution": {
      "very_positive": 35, "positive": 28,
      "neutral": 20, "negative": 12, "very_negative": 5
    }
  },
  "category_sentiments": {
    "service": 0.82, "food_quality": 0.85,
    "ambiance": 0.71, "value": 0.68
  },
  "themes": {
    "praises": ["Excellent steak quality", "Friendly staff"],
    "complaints": ["Slow service on weekends", "Limited parking"]
  },
  "item_sentiments": [
    {
      "item_name": "Filete Mignon",
      "overall_sentiment": "very_positive",
      "text_sentiment": {"score": 0.92, "mention_count": 15},
      "actionable_insight": "Signature dish — protect quality",
      "priority": "high"
    }
  ],
  "recommendations": [
    {
      "priority": "high",
      "type": "service",
      "issue": "Weekend service delays",
      "action": "Add staff during peak Saturday hours",
      "expected_impact": "15-20% improvement in service scores"
    }
  ]
}
```

### 5.3 Competitor Analysis (`CompetitorAnalysisResult`)

```json
{
  "analysis_id": "uuid",
  "competitors_analyzed": ["Competitor A", "Competitor B"],
  "competitive_landscape": {
    "market_position": "Mid-premium segment leader",
    "competitive_intensity": "moderate",
    "key_differentiators": ["Unique fusion menu", "Strong social presence"],
    "competitive_gaps": ["No delivery service", "Limited vegetarian options"]
  },
  "price_analysis": {
    "price_positioning": "premium",
    "price_gaps": [
      {
        "item_category": "Steaks",
        "our_price": 38.50,
        "competitor_price": 35.00,
        "price_difference_percent": 10.0,
        "recommendation": "Justify premium with quality narrative"
      }
    ]
  },
  "strategic_recommendations": [
    {
      "priority": 1,
      "action": "Launch delivery service",
      "expected_impact": "15-20% revenue increase",
      "timeframe": "1-2 months"
    }
  ]
}
```

### 5.4 Campaign Package (`CampaignPackage`)

```json
{
  "campaign_id": "uuid",
  "dish_name": "Filete Mignon",
  "campaign_brief": "Premium steak promotion targeting food enthusiasts",
  "strategy": {
    "target_audience": "Food enthusiasts, ages 28-45",
    "key_message": "Experience perfection on a plate",
    "channels": ["instagram", "facebook", "in_store"]
  },
  "image_prompt": {
    "positive_prompt": "Professional food photography, filete mignon...",
    "negative_prompt": "low quality, blurry...",
    "aspect_ratio": "1:1",
    "num_images": 4
  },
  "generated_images": ["base64_encoded_image_1", "base64_encoded_image_2"],
  "copy": {
    "caption": "Every bite tells a story of perfection...",
    "hashtags": ["#FineDining", "#SteakLovers"],
    "call_to_action": "Reserve your table tonight",
    "target_audience": "Food enthusiasts",
    "tone": "Premium, aspirational"
  }
}
```

### 5.5 Thought Signature

Every analysis includes a `ThoughtSignature`:

```json
{
  "plan": ["Extract menu items", "Calculate margins", "Classify BCG"],
  "observations": ["42 items found", "High margin variance detected"],
  "reasoning": "Based on contribution margin analysis and popularity data...",
  "assumptions": ["Cost data is accurate", "Sales period is representative"],
  "confidence": 0.87,
  "verification_checks": [
    {"check": "price_consistency", "passed": true},
    {"check": "margin_range", "passed": true}
  ],
  "corrections_made": ["Removed 2 duplicate items"]
}
```

---

## 6. Database Schema

### Tables

| Table | Description | Key Fields |
|-------|-------------|-----------|
| `analysis_sessions` | Session tracking | id (UUID), name, status, timestamps |
| `menu_categories` | Menu categories | session_id, name, display_order |
| `menu_items` | Individual items | name, price, cost, dietary flags, image_score |
| `sales_records` | Sales transactions | item_name, sale_date, units_sold, revenue |
| `product_profiles` | BCG classifications | bcg_class, market_share, growth_rate |
| `competitors` | Competitor profiles | name, address, coordinates, distance |
| `competitor_menus` | Competitor menu data | competitor_id, items (JSON) |
| `price_comparisons` | Price gap data | our_price, competitor_price, recommendation |
| `marathon_checkpoints` | Pipeline recovery | stage, state_json, timestamp |

### Storage Locations

| Data Type | Location |
|-----------|---------|
| Database | `data/RestoPilotAI.db` (SQLite) or PostgreSQL container |
| File uploads | `data/uploads/` |
| Generated outputs | `data/outputs/` |
| ML model artifacts | `data/models/` |
| Cache | Redis or in-memory LRU |

---

## 7. Data Retention & Lifecycle

| Data Type | Retention | Deletion |
|-----------|----------|---------|
| Session data | Persistent until DB reset | Manual or DB wipe |
| Uploaded files | Persistent in `data/uploads/` | Manual deletion |
| Generated images | Session-scoped | With session cleanup |
| Cache (Redis) | TTL-based (7 days default) | Automatic expiry |
| Cache (in-memory) | Application lifetime | On restart |
| ML models | Session-scoped (ephemeral) | Not persisted |

---

## 8. Privacy & Security Considerations

### Data Handled
- **Business Data**: Restaurant names, addresses, menu items, pricing, sales figures
- **Competitor Data**: Publicly available Google Maps information only
- **Customer Reviews**: Publicly posted Google Maps reviews only
- **No PII**: System does not collect or store personally identifiable information about restaurant customers

### Data Transmission
- **Frontend ↔ Backend**: HTTP/WebSocket over localhost (dev) or HTTPS (prod)
- **Backend → Gemini API**: HTTPS to Google API endpoints
- **Backend → Google Maps**: HTTPS to Google Maps API endpoints
- **No third-party analytics or tracking**

### Security Measures
- API keys stored in environment variables (never in code)
- CORS configured for specific origins only
- Security headers: X-Frame-Options, X-Content-Type-Options, Referrer-Policy
- File upload size limits (10 MB)
- File type validation (extension whitelist)
- Rate limiting on API endpoints
- Budget caps on AI API usage ($50/day default)

### Data Processing by External Services
- **Google Gemini API**: Menu images, sales data, and business context are sent to Google's Gemini API for processing. Subject to [Google's AI Terms of Service](https://ai.google.dev/terms).
- **Google Maps/Places API**: Location queries and place IDs are sent to Google Maps. Subject to [Google Maps Platform Terms](https://cloud.google.com/maps-platform/terms).
- **No data is sold or shared** with any other third party.

---

## 9. Data Quality

### Input Validation
- File format validation (extension + MIME type)
- File size limits (10 MB per file)
- CSV schema detection with flexible column mapping
- Date parsing with multiple format support
- Numeric validation for prices and quantities

### AI Quality Assurance
- Extraction confidence scores (0-1) on every AI output
- Self-verification loop catches inconsistencies
- Vibe Engineering quality threshold (0.85 default)
- Grounding verification cross-references web sources
- Thought signatures document all assumptions

### Known Data Quality Issues
- **OCR Accuracy**: Handwritten or low-quality menu images may produce lower extraction confidence
- **Sales Data Gaps**: Missing dates or items are handled gracefully but reduce prediction accuracy
- **Review Bias**: Google Maps reviews skew toward extreme opinions (very positive or very negative)
- **Competitor Coverage**: Rural or newly opened restaurants may have limited Google Maps data

---

## 10. Synthetic Demo Data

The project includes synthetic demo data for testing:

| File | Description | Size |
|------|-------------|------|
| `docs/menu_completo.csv` | Complete menu catalog | 13.8 KB |
| `docs/ventas_sinteticas.csv` | Synthetic sales records (full) | 11.2 MB |
| `docs/ventas_sinteticas_short.csv` | Synthetic sales records (short) | 2.1 MB |
| `docs/sales_sample.csv` | Sales sample data | 11.2 MB |
| `docs/ventas_sinteticas_descripción.md` | Description of synthetic data | 12.3 KB |
| `docs/Platos Fuertes.pdf` | Sample menu PDF | 48.7 MB |
| `docs/Licores y cocteles.pdf` | Sample drinks menu PDF | 21.8 MB |
| `docs/Audiovisual/` | Audio/video test files | Variable |

The synthetic data was generated to simulate realistic restaurant operations with seasonal patterns, promotions, and multi-category menus.

---

## 11. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-06 | Initial data card documenting all data flows, schemas, and privacy |

---

## 12. Contact

For questions about data handling, privacy, or schema specifications:
- **Repository**: [RestoPilotAI on GitHub](https://github.com/RestoPilotAI/RestoPilotAI)
- **License**: MIT
