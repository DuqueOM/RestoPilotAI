import csv
import json
import sys
import os
import random
from pathlib import Path
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "backend")

# Configuration
DEMO_SESSION_ID = "margarita-pinta-demo-001"
# Ensure we point to backend/data/demo regardless of where script is run
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "backend" / "data" / "demo"
CSV_PATH = DATA_DIR / "menu_completo.csv"

RESTAURANT_INFO = {
    "name": "Margarita Pinta",
    "location": "Cl 20 #40A-10, Pasto, Nariño, Colombia",
    "cuisine_type": "Gastrobar / Coctelería",
    "social_media": {
        "instagram": "https://www.instagram.com/margaritapintapasto/",
        "facebook": "https://www.facebook.com/MargaritaPintaRestauranteBar"
    }
}

def load_menu_from_csv():
    """Load menu items from the CSV file."""
    if not CSV_PATH.exists():
        print(f"Error: Menu CSV not found at {CSV_PATH}")
        sys.exit(1)
        
    items = []
    print(f"Loading menu from {CSV_PATH}...")
    
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                price = float(row['price'])
                cost = float(row['estimated_cost_cop'])
                
                # Skip invalid entries
                if price <= 0: continue
                
                name = row['product'].strip()
                unit = row['unit'].strip()
                
                # Append unit to name if it's a specific measure (trago, bot, med) to distinguish variants
                if unit.lower() not in ['unit', 'unidad', 'und', '']:
                    name = f"{name} ({unit})"
                
                items.append({
                    "name": name,
                    "category": row['category'].strip(),
                    "price": price,
                    "cost": cost,
                    "description": row['description'].strip(),
                    "unit": unit
                })
            except (ValueError, KeyError) as e:
                print(f"Skipping row due to error: {row} - {e}")
                continue
                
    return items

def load_sales_from_csv():
    """Load real sales data from the source CSV."""
    sales_path = DATA_DIR / "sales_source.csv"
    if not sales_path.exists():
        print(f"Warning: Sales source not found at {sales_path}. Falling back to generation.")
        return None

    sales = []
    print(f"Loading real sales data from {sales_path}...")
    
    try:
        with open(sales_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Map CSV columns to our schema
                # CSV: item_name, date, units_sold, price, categoria
                try:
                    # Parse date DD-MM-YY
                    date_str = row.get('date', row.get('fecha'))
                    try:
                        date_obj = datetime.strptime(date_str, "%d-%m-%y").replace(tzinfo=timezone.utc)
                    except ValueError:
                        # Fallback for other formats if needed
                        date_obj = datetime.now(timezone.utc)

                    sales.append({
                        "date": date_str,
                        # "date_obj": date_obj, # Removed to avoid JSON serialization error
                        "item_name": row['item_name'],
                        "quantity": int(row['units_sold']),
                        "revenue": float(row['price']) * int(row['units_sold']), # Fixed: Use item price * qty, NOT ticket subtotal
                        "category": row.get('categoria', row.get('category')),
                        "unit_price": float(row['price']),
                        "unit_cost": float(row['cost'])
                    })
                except (ValueError, KeyError) as e:
                    continue
    except Exception as e:
        print(f"Error reading sales CSV: {e}")
        return None
        
    return sales

def analyze_menu_portfolio_from_sales(items, sales_data):
    """
    Classify items into BCG matrix based on REAL sales data.
    Normalizes metrics to 30-day averages based on the actual date range.
    """
    analyzed_items = {}
    
    if not sales_data:
        return {}

    # Calculate date range
    dates = []
    for s in sales_data:
        try:
            d = datetime.strptime(s['date'], "%d-%m-%y").replace(tzinfo=timezone.utc)
            dates.append(d)
        except ValueError:
            continue
            
    if dates:
        min_date = min(dates)
        max_date = max(dates)
        total_days = (max_date - min_date).days + 1
    else:
        total_days = 1
        min_date = datetime.now(timezone.utc)
        max_date = min_date

    if total_days < 1: total_days = 1
    
    print(f"   - Analyzing sales over {total_days} days ({min_date.date()} to {max_date.date()})")
    
    # Aggregates
    item_stats = {}
    total_sold = 0
    
    # Initialize with menu items
    for item in items:
        item_stats[item['name']] = {
            "units": 0,
            "revenue": 0,
            "cost": item['cost'],
            "price": item['price']
        }

    # Process sales
    matched_count = 0
    unmatched_count = 0
    
    # Create a lookup for menu items by normalized name to handle variants
    # Key: normalized_name -> list of (price, item_name_with_unit)
    menu_variants = {}
    for item in items:
        # Extract base name if we added a suffix in load_menu_from_csv
        base_name = item['name']
        if "(" in base_name and base_name.endswith(")"):
            base_name = base_name.rsplit(" (", 1)[0]
        
        norm_name = base_name.lower().strip()
        if norm_name not in menu_variants:
            menu_variants[norm_name] = []
        
        menu_variants[norm_name].append((item['price'], item['name']))

    for sale in sales_data:
        name = sale['item_name'].lower().strip()
        price = float(sale['unit_price'])
        
        matched_name = None
        
        # 1. Try to find the name in our menu variants
        if name in menu_variants:
            variants = menu_variants[name]
            
            if len(variants) == 1:
                matched_name = variants[0][1]
            else:
                closest_variant = min(variants, key=lambda x: abs(x[0] - price))
                matched_name = closest_variant[1]
        
        if matched_name:
            if matched_name in item_stats:
                line_revenue = price * sale['quantity']
                
                item_stats[matched_name]["units"] += sale['quantity']
                item_stats[matched_name]["revenue"] += line_revenue
                total_sold += sale['quantity']
                matched_count += 1
        else:
            unmatched_count += 1

    print(f"   - Matched {matched_count} sales records to menu items.")
    print(f"   - Unmatched {unmatched_count} records (skipped).")

    # Calculate metrics
    margins = []
    
    for name, stats in item_stats.items():
        if stats["price"] > 0:
            margin = (stats["price"] - stats["cost"]) / stats["price"]
        else:
            margin = 0
        margins.append(margin)
        stats["margin"] = margin
        
        # Calculate monthly averages
        stats["monthly_units"] = (stats["units"] / total_days) * 30
        stats["monthly_revenue"] = (stats["revenue"] / total_days) * 30

    # Calculate total monthly volume for share
    total_monthly_units = sum(s["monthly_units"] for s in item_stats.values())
    
    # Calculate averages for classification
    avg_margin = sum(margins) / len(margins) if margins else 0
    avg_share = 1.0 / len(items) if items else 0

    # Classify
    for name, stats in item_stats.items():
        margin = stats["margin"]
        share = stats["monthly_units"] / total_monthly_units if total_monthly_units > 0 else 0
        stats["share"] = share
        
        # Weighted thresholds usually better, but simple average for now
        is_high_margin = margin >= avg_margin
        is_high_share = share >= (avg_share * 0.7) # Lower threshold slightly
        
        if is_high_share and is_high_margin:
            category = "star"
        elif is_high_share and not is_high_margin:
            category = "plowhorse"
        elif not is_high_share and is_high_margin:
            category = "puzzle"
        else:
            category = "dog"
            
        analyzed_items[name] = {
            "bcg_category": category,
            "margin": margin,
            "share": share,
            "growth": random.uniform(0.0, 0.5), # Simulated growth
            "revenue_30d": stats["monthly_revenue"], 
            "daily_vol_est": stats["monthly_units"] / 30
        }
        
    return analyzed_items

def get_strategy_for_category(category, name, margin):
    """Generate realistic strategy recommendations based on BCG category."""
    strategies = {
        "star": {
            "action": "Protect & Promote",
            "priority": "High",
            "pricing": "Maintain or Slight Increase",
            "menu_position": "High Visibility (Top/Right)",
            "recommendations": [
                "Maintain strict quality control to preserve reputation.",
                "Feature prominently in menu design (Golden Triangle).",
                f"Consider a slight price increase (e.g., 5%) to maximize profit given high demand." if margin < 0.6 else "Keep price stable to maintain volume dominance."
            ]
        },
        "plowhorse": {
            "action": "Maintain & Leverage",
            "priority": "Medium",
            "pricing": "Monitor Costs",
            "menu_position": "Standard Visibility",
            "recommendations": [
                "Ensure consistent stock availability (Never 86).",
                "Bundle with 'Puzzle' items to drive trial of new products.",
                "Streamline preparation to reduce labor costs further."
            ]
        },
        "puzzle": {
            "action": "Invest or Divest",
            "priority": "High",
            "pricing": "Review / Promotion",
            "menu_position": "Highlight to Test",
            "recommendations": [
                "Increase visibility through table talkers or staff recommendations.",
                "Run a limited-time 'Happy Hour' promotion to boost trial.",
                "Review recipe to ensure it appeals to the core demographic."
            ]
        },
        "dog": {
            "action": "Divest or Retool",
            "priority": "Low",
            "pricing": "Discount or Remove",
            "menu_position": "Low Visibility / Remove",
            "recommendations": [
                "Consider removing from the menu to simplify operations.",
                "Rebrand with a new name or photo to refresh interest.",
                "Increase price significantly to convert to 'Puzzle' (niche high margin)."
            ]
        }
    }
    return strategies.get(category, {
        "action": "Analyze",
        "priority": "Medium",
        "pricing": "Analyze",
        "menu_position": "Standard",
        "recommendations": ["Gather more data."]
    })

def create_demo_json():
    """Create demo data JSON files."""
    
    # 1. Load Data
    menu_items = load_menu_from_csv()
    if not menu_items:
        print("No items loaded!")
        return

    # 2. Load Sales Data
    sales_data = load_sales_from_csv()
    if not sales_data:
        print("No sales data loaded!")
        return

    # 3. Analyze (BCG) with Real Data
    bcg_analysis = analyze_menu_portfolio_from_sales(menu_items, sales_data)
    
    # 3. Structure Menu Data
    menu_data = {
        "session_id": DEMO_SESSION_ID,
        "items": menu_items,
        "categories": list(set(item["category"] for item in menu_items)),
        "extraction_confidence": 1.0, # It's from CSV
    }

    # 4. Structure BCG Data
    bcg_items = []
    for item in menu_items:
        stats = bcg_analysis.get(item['name'])
        if not stats: continue
        
        category = stats["bcg_category"]
        strategy = get_strategy_for_category(category, item['name'], stats['margin'])
        
        bcg_items.append({
            "name": item["name"],
            "price": item["price"],
            "cost": item["cost"],
            "category": category,
            "growth": stats["growth"],
            "share": stats["share"],
            "revenue": stats["revenue_30d"],
            "margin": stats["margin"],
            "popularity_pct": stats["share"] * 100 * 10, # Normalized for display
            "cm_unitario": item["price"] - item["cost"],
            "margin_pct": stats["margin"] * 100,
            "units_sold": int(stats["daily_vol_est"] * 30),
            "strategy": strategy
        })

    # Calculate detailed summary and thresholds
    total_items = len(bcg_items)
    total_revenue = sum(i['revenue'] for i in bcg_items)
    total_units = sum(i['units_sold'] for i in bcg_items)
    total_contribution = sum(i['cm_unitario'] * i['units_sold'] for i in bcg_items)
    weighted_avg_cm = total_contribution / total_units if total_units > 0 else 0
    
    # Thresholds used in analysis (approximate reconstruction)
    avg_share = 1.0 / total_items if total_items > 0 else 0
    popularity_threshold = avg_share * 0.7
    
    # Category aggregation
    cat_stats = {}
    for i in bcg_items:
        cat = i['category'].lower()
        if cat not in cat_stats:
            cat_stats[cat] = {"count": 0, "revenue": 0, "contribution": 0, "units": 0}
        cat_stats[cat]["count"] += 1
        cat_stats[cat]["revenue"] += i['revenue']
        cat_stats[cat]["contribution"] += i['cm_unitario'] * i['units_sold']
        cat_stats[cat]["units"] += i['units_sold']
        
    categories_summary = []
    for cat, s in cat_stats.items():
        categories_summary.append({
            "category": cat,
            "label": cat.replace("_", " ").title(),
            "count": s["count"],
            "pct_items": (s["count"] / total_items) * 100,
            "total_revenue": s["revenue"],
            "pct_revenue": (s["revenue"] / total_revenue) * 100 if total_revenue else 0,
            "total_contribution": s["contribution"],
            "pct_contribution": (s["contribution"] / total_contribution) * 100 if total_contribution else 0,
            "units_sold": s["units"],
            "pct_units": (s["units"] / total_units) * 100 if total_units else 0
        })

    # Top lists
    top_contribution = sorted(bcg_items, key=lambda x: x['cm_unitario'] * x['units_sold'], reverse=True)[:5]
    top_popularity = sorted(bcg_items, key=lambda x: x['popularity_pct'], reverse=True)[:5]
    dogs_list = [i['name'] for i in bcg_items if i['category'] == 'dog']

    bcg_data = {
        "session_id": DEMO_SESSION_ID,
        "items": bcg_items,
        "summary": {
            "total_items": total_items,
            "total_revenue": total_revenue,
            "total_contribution": total_contribution,
            "total_units": total_units,
            "avg_cm": weighted_avg_cm,
            "methodology": "BCG Matrix (Growth-Share)",
            "period": "30d",
            "categories": categories_summary,
            "top_by_contribution": [{"name": i['name'], "contribution": i['cm_unitario'] * i['units_sold']} for i in top_contribution],
            "top_by_popularity": [{"name": i['name'], "popularity_pct": i['popularity_pct']} for i in top_popularity],
            "attention_needed": len(dogs_list),
            "dogs_list": dogs_list
        },
        "thresholds": {
            "popularity_threshold": popularity_threshold * 100, # as %
            "cm_threshold": weighted_avg_cm, # Using weighted avg as proxy for display
            "cm_average_simple": sum(i['cm_unitario'] for i in bcg_items) / total_items if total_items else 0,
            "expected_popularity": avg_share * 100,
            "n_items": total_items,
            "total_units": total_units
        }
    }

    # Generate dynamic insights
    stars = [i for i in bcg_items if i['category'] == 'star']
    cows = [i for i in bcg_items if i['category'] == 'plowhorse']
    questions = [i for i in bcg_items if i['category'] == 'puzzle']
    dogs = [i for i in bcg_items if i['category'] == 'dog']
    
    stars.sort(key=lambda x: x['revenue'], reverse=True)
    cows.sort(key=lambda x: x['revenue'], reverse=True)
    
    top_star_names = ", ".join([i['name'] for i in stars[:2]]) if stars else "None"
    top_cow_names = ", ".join([i['name'] for i in cows[:2]]) if cows else "None"
    
    insights = {
        "STAR": f"Your top stars ({top_star_names}) are driving significant revenue. These align perfectly with your 'Margarita Pinta' brand identity.",
        "CASH_COW": f"Steady performers like {top_cow_names} provide consistent cash flow. Maintain quality and availability.",
        "QUESTION_MARK": f"You have {len(questions)} items (Puzzles) with high margin but low volume. Consider promotional campaigns to convert these into Stars.",
        "DOG": f"There are {len(dogs)} items underperforming. Review the 'Dogs' list for potential menu optimization or removal."
    }
    
    bcg_data["insights"] = insights

    # 5. Generate Campaigns (Contextual)
    # Identify top Stars and Dogs to create realistic campaigns
    stars = [i for i in bcg_items if i['category'] == 'star']
    dogs = [i for i in bcg_items if i['category'] == 'dog']
    
    stars.sort(key=lambda x: x['revenue'], reverse=True)
    cows.sort(key=lambda x: x['revenue'], reverse=True)
    
    top_star = stars[0] if stars else None
    
    campaigns = [
        {
            "title": f"Noches de {top_star['name'].split()[0] if top_star else 'Margarita'}",
            "objective": "Boost signature cocktail sales",
            "target_category": "STAR",
            "target_audience": "Social groups 25-45",
            "copy": {
                "social_media": f"🍹 {top_star['name'].upper() if top_star else 'MARGARITA'} NIGHTS! 🍹\n\nExperience the best of Pasto. 2x1 every Thursday.\n\n#MargaritaPinta #Pasto",
                "email_subject": "🌶️ Spice up your night!",
                "email_body": "Join us for our signature specials."
            },
            "timing": "Thursdays 6pm-11pm",
            "expected_impact": "30% increase in category revenue"
        },
        {
            "title": "Happy Hour Estudiantil",
            "objective": "Increase traffic during off-peak hours",
            "target_category": "CASH_COW",
            "target_audience": "University students",
            "copy": {
                "social_media": "📚 Study Break? 🍻\n\nShow your student ID for 15% off beers and nachos.\n\n#PastoStudents #HappyHour",
                "email_subject": "Study hard, relax hard",
                "email_body": "You deserve a break."
            },
            "timing": "Wed-Fri 3pm-6pm",
            "expected_impact": "Fill tables during afternoon slump"
        }
    ]

    # Add a 3rd campaign if Hervidos exist (Signature local drink)
    hervidos = [i for i in menu_items if "Hervido" in i['name']]
    if hervidos:
        campaigns.append({
            "title": "Hervido Experience",
            "objective": "Promote local fusion drinks",
            "target_category": "QUESTION_MARK", # Usually high margin, need volume
            "target_audience": "Locals and tourists",
            "copy": {
                "social_media": "🔥 HERVIDO COMO NUNCA ANTES 🔥\n\nTradición Nariñense + Licores Premium.\n\nVen a probar nuestro Hervido con Tequila. El calorcito que necesitas esta noche.\n\n#Pasto #Tradicion",
                "email_subject": "Tradition meets Innovation ☕",
                "email_body": "Discover our unique twist on the Nariño classic."
            },
            "timing": "Cold evenings / Weekends",
            "expected_impact": "Convert local curiosity into sales"
        })
    else:
        # Fallback 3rd campaign
        campaigns.append({
            "title": "After Office Chill",
            "objective": "Drive traffic early evening",
            "target_category": "CASH_COW",
            "target_audience": "Office workers",
            "copy": {
                "social_media": "🍻 AFTER OFFICE 🍻\n\nRough day? We've got you covered.\n\n#AfterOffice #Pasto",
                "email_subject": "You deserve a break",
                "email_body": "Work's done. Time to relax."
            },
            "timing": "Weekdays 5pm-8pm",
            "expected_impact": "Increase early evening occupancy"
        })
    
    campaign_data = {
        "session_id": DEMO_SESSION_ID,
        "campaigns": campaigns,
        "thought_process": "Analysis of 178 menu items reveals strong potential in Coctelería stars."
    }

    # 6. Sales Data (Already Loaded)
    # sales_data is already populated from load_sales_from_csv() at the start

    # 7. Generate Competitors Data
    competitor_data = {
        "competitors": [
            {
                "name": "Vudú Coctelería",
                "type": "Directo",
                "distance": "300m",
                "rating": 4.6,
                "priceRange": "$$$",
                "strengths": ["Coctelería de autor", "Ambiente moderno"],
                "weaknesses": ["Espacio reducido", "Pocas opciones de comida"],
                "marketShare": 18,
                "trend": "up"
            },
            {
                "name": "La Merced Gastrobar",
                "type": "Directo",
                "distance": "500m",
                "rating": 4.4,
                "priceRange": "$$$",
                "strengths": ["Ubicación histórica", "Música en vivo"],
                "weaknesses": ["Servicio lento", "Carta de vinos limitada"],
                "marketShare": 22,
                "trend": "stable"
            },
            {
                "name": "El Techo",
                "type": "Indirecto",
                "distance": "1.2km",
                "rating": 4.3,
                "priceRange": "$$$$",
                "strengths": ["Vista panorámica", "Eventos exclusivos"],
                "weaknesses": ["Precios altos", "Difícil acceso"],
                "marketShare": 15,
                "trend": "down"
            }
        ],
        "market_position": "Strong contender in the premium gastrobar segment."
    }

    # 8. Generate Sentiment Data
    sentiment_data = {
        "overall": {
            "score": 0.85,
            "label": "Muy Positivo",
            "trend": "improving"
        },
        "sources": [
            {"name": "Google Reviews", "count": 245, "avgRating": 4.6, "sentiment": 0.88},
            {"name": "TripAdvisor", "count": 120, "avgRating": 4.5, "sentiment": 0.82},
            {"name": "Instagram", "count": 560, "avgRating": None, "sentiment": 0.90}
        ],
        "topics": [
            {"topic": "Coctelería", "sentiment": 0.95, "mentions": 180, "trend": "up"},
            {"topic": "Ambiente", "sentiment": 0.92, "mentions": 150, "trend": "stable"},
            {"topic": "Comida", "sentiment": 0.80, "mentions": 90, "trend": "up"},
            {"topic": "Tiempo de espera", "sentiment": 0.60, "mentions": 45, "trend": "down"}
        ],
        "recentReviews": [
            {"text": "El Margarita Ardiente es espectacular, una experiencia única en Pasto.", "rating": 5, "source": "Google", "date": "hace 2 días"},
            {"text": "Muy buen ambiente, la música es genial. Las costillas recomendadísimas.", "rating": 5, "source": "TripAdvisor", "date": "hace 5 días"},
            {"text": "Un poco demorado el servicio el viernes, pero los cocteles valen la pena.", "rating": 4, "source": "Google", "date": "hace 1 semana"}
        ]
    }

    # 9. Generate Predictions Data (Based on historical patterns)
    # Calculate historical daily stats
    daily_revenues = {}
    for sale in sales_data:
        date = sale['date']
        daily_revenues[date] = daily_revenues.get(date, 0) + sale['revenue']
    
    total_rev = sum(daily_revenues.values())
    print(f"   - Sales Data Stats: Total Rev: ${total_rev:,.2f}, Days: {len(daily_revenues)}")
    
    if daily_revenues:
        avg_daily_rev = sum(daily_revenues.values()) / len(daily_revenues)
        print(f"   - Avg Daily Rev: ${avg_daily_rev:,.2f}")
        # Calculate roughly std dev for noise
        variance = sum((r - avg_daily_rev) ** 2 for r in daily_revenues.values()) / len(daily_revenues)
        std_dev = variance ** 0.5
    else:
        avg_daily_rev = 33000000 # Fallback based on known average
        std_dev = 5000000

    predictions = []
    base_date = datetime.now(timezone.utc)
    
    # Generate 30 days forecast
    for i in range(30):
        date = base_date + timedelta(days=i)
        day_of_week = date.weekday() # 0=Mon, 6=Sun
        
        # Simple seasonality: Weekends higher
        is_weekend = day_of_week >= 4 # Fri, Sat, Sun
        seasonality = 1.3 if is_weekend else 0.85
        
        # Base projection
        projected = avg_daily_rev * seasonality
        
        # Add random noise
        noise = random.normalvariate(0, std_dev * 0.5) 
        final_prediction = max(0, projected + noise)
        
        predictions.append({
            "date": date.strftime("%Y-%m-%d"),
            "predicted": final_prediction,
            "confidence_lower": final_prediction * 0.85,
            "confidence_upper": final_prediction * 1.15
        })

    predictions_data = {
        "session_id": DEMO_SESSION_ID,
        "predictions": predictions,
        "metrics": {
            "mape": 0.12, # Realistic error rate
            "rmse": std_dev * 0.8,
            "r2": 0.78
        },
        "insights": [
            f"Forecast based on historical daily average of ${avg_daily_rev:,.0f}.",
            "Projected revenue stability with expected weekend peaks.",
            "Inventory planning should account for 30% higher demand on Fridays and Saturdays."
        ]
    }

    # 10. Full Session Structure
    session_data = {
        "session_id": DEMO_SESSION_ID,
        "restaurant_info": RESTAURANT_INFO,
        "status": "completed",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "menu": menu_data,
        "bcg": bcg_data,
        "campaigns": campaign_data,
        "sales_data": sales_data[:100], # Preview
        "competitor_analysis": competitor_data,
        "sentiment_analysis": sentiment_data,
        "predictions": predictions_data
    }

    # 11. Save Files
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(DATA_DIR / "menu.json", "w") as f:
        json.dump(menu_data, f, indent=2)

    with open(DATA_DIR / "bcg.json", "w") as f:
        json.dump(bcg_data, f, indent=2)

    with open(DATA_DIR / "campaigns.json", "w") as f:
        json.dump(campaign_data, f, indent=2)

    with open(DATA_DIR / "session.json", "w") as f:
        json.dump(session_data, f, indent=2)
        
    with open(DATA_DIR / "restaurant_info.json", "w") as f:
        json.dump(RESTAURANT_INFO, f, indent=2)

    with open(DATA_DIR / "sales.json", "w") as f:
        json.dump(sales_data, f, indent=2)

    print(f"✅ Demo data created for {RESTAURANT_INFO['name']}!")
    print(f"   - Menu: {len(menu_items)} items")
    print(f"   - Sales Records: {len(sales_data)} generated")
    print(f"   - Output Dir: {DATA_DIR}")
    print(f"   - Added: Competitors, Sentiment, Predictions")

if __name__ == "__main__":
    create_demo_json()
