# 📁 MenuPilot Data Directory

This directory contains data files used by MenuPilot.

## Directory Structure

```
data/
├── demo/           # Pre-loaded demo session data
│   ├── menu.json       # Demo menu items (10 items)
│   ├── bcg.json        # BCG classification results
│   ├── campaigns.json  # Generated marketing campaigns
│   ├── sales.json      # 90 days of synthetic sales data
│   └── session.json    # Complete session snapshot
│
├── sample/         # Sample files for testing
│   └── sales_sample.csv  # Sample sales CSV format
│
├── uploads/        # User-uploaded files (gitignored)
├── outputs/        # Generated outputs (gitignored)
└── models/         # Trained ML models (gitignored)
```

## Demo Data

The `demo/` folder contains a complete pre-loaded session for the **Mexican Restaurant** demo:

| File | Description | Records |
|------|-------------|---------|
| `menu.json` | Extracted menu items | 10 items |
| `bcg.json` | BCG Matrix classification | 10 items |
| `campaigns.json` | AI-generated campaigns | 3 campaigns |
| `sales.json` | Historical sales data | ~900 records |
| `session.json` | Full session state | 1 session |

### Regenerating Demo Data

```bash
python scripts/seed_demo_data.py
```

## Sample Files

### sales_sample.csv Format

```csv
date,item_name,quantity,revenue,cost
2024-01-15,Tacos al Pastor,45,584.55,233.82
2024-01-15,Guacamole Premium,32,287.68,86.30
```

**Required columns:**
- `date` - Sale date (YYYY-MM-DD)
- `item_name` - Menu item name (must match menu extraction)
- `quantity` - Units sold
- `revenue` - Total revenue

**Optional columns:**
- `cost` - Total cost (for margin calculation)
- `category` - Item category

## Data Privacy

- **uploads/**: Contains user-uploaded menu images and sales files
- **outputs/**: Contains generated reports and exports
- **models/**: Contains trained ML model checkpoints

All runtime data directories are gitignored for privacy.
