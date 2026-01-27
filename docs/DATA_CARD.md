# Data Card - MenuPilot

## Dataset Overview

MenuPilot processes three primary data types from restaurant businesses:

### 1. Menu Images

| Attribute | Description |
|-----------|-------------|
| **Type** | Image files (JPEG, PNG, WebP) |
| **Source** | User-uploaded restaurant menus |
| **Processing** | OCR + Gemini 3 multimodal extraction |
| **Output** | Structured JSON with items, prices, categories |

**Extracted Fields:**
- Item name
- Price (numeric)
- Description (optional)
- Category (appetizers, mains, desserts, drinks)
- Dietary tags (vegetarian, vegan, gluten-free, spicy)

### 2. Dish Photographs

| Attribute | Description |
|-----------|-------------|
| **Type** | Image files (JPEG, PNG, WebP) |
| **Source** | User-uploaded dish photos |
| **Processing** | Gemini 3 visual analysis |
| **Output** | Attractiveness scores (0-1), presentation quality |

**Analyzed Metrics:**
- Visual attractiveness score
- Presentation quality rating
- Color appeal assessment
- Portion perception
- Social media worthiness (Instagram-ability)

### 3. Sales Data

| Attribute | Description |
|-----------|-------------|
| **Type** | CSV or XLSX files |
| **Source** | User-uploaded POS/sales records |
| **Processing** | Pandas parsing + feature engineering |

**Required Columns:**
| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `date` | Date | Yes | Sale date (YYYY-MM-DD) |
| `item_name` | String | Yes | Menu item name |
| `units_sold` | Integer | Yes | Quantity sold |
| `revenue` | Float | No | Total revenue |
| `had_promotion` | Boolean | No | Promotion active |
| `promotion_discount` | Float | No | Discount percentage |

## Synthetic Data Generation

For demonstration purposes, MenuPilot can generate realistic synthetic sales data:

```python
# Synthetic data parameters
- Time period: 90 days historical
- Base demand: 5-30 units/day per item
- Weekend multiplier: 1.3x
- Price elasticity: Higher price → lower demand
- Promotion effect: 1.3x during promotions
- Random noise: ±30% daily variation
```

## Data Privacy & Compliance

### User Data Handling
- **Storage**: Local filesystem or user-controlled volumes
- **Retention**: Session-based (no persistent storage of user data)
- **Encryption**: Not stored encrypted (demo system)
- **PII**: No personal customer data required or processed

### Recommendations for Production
- Implement data encryption at rest
- Add user authentication
- Enable audit logging
- Comply with GDPR/CCPA for any customer data
- Anonymize any sales data before processing

## Data Quality Requirements

### Menu Images
- **Resolution**: Minimum 800x600 pixels recommended
- **Format**: JPEG, PNG, or WebP
- **Clarity**: Text should be legible
- **Orientation**: Upright preferred (auto-rotation supported)

### Sales Data
- **Completeness**: No missing values in required columns
- **Date Range**: Minimum 30 days for meaningful analysis
- **Item Matching**: Item names should match menu items
- **Encoding**: UTF-8

## BCG Classification Logic

Products are classified using percentile-based thresholds:

| Class | Market Share | Growth Rate | Strategy |
|-------|--------------|-------------|----------|
| **Star** | ≥75th percentile | ≥75th percentile | Invest |
| **Cash Cow** | ≥75th percentile | <75th percentile | Maintain |
| **Question Mark** | <75th percentile | ≥75th percentile | Analyze |
| **Dog** | <75th percentile | <75th percentile | Review |

**Metrics Calculation:**
- **Market Share**: `item_units / total_units`
- **Growth Rate**: `(recent_avg - early_avg) / early_avg`
- **Popularity Score**: `item_units / max_item_units`

## Data Limitations

1. **Historical Dependency**: Predictions require historical data; new items have limited predictive accuracy
2. **Seasonality**: Model may not capture annual seasonality with <1 year data
3. **External Factors**: Weather, events, economic conditions not modeled
4. **Menu Changes**: Price/item changes require model retraining

## Citation

If using MenuPilot or this data processing methodology:

```
@software{menupilot2026,
  title = {MenuPilot: AI-Powered Restaurant Menu Optimization},
  author = {MenuPilot Team},
  year = {2026},
  url = {https://github.com/menupilot/menupilot}
}
```
