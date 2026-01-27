#!/usr/bin/env python3
"""
Seed demo data for MenuPilot testing.
Creates a pre-loaded session with sample menu items and sales data.
"""

import json
import sys
sys.path.insert(0, 'backend')

from datetime import datetime, timedelta
import random

# Demo restaurant data
DEMO_SESSION_ID = "demo-session-001"

DEMO_MENU_ITEMS = [
    # Stars - High growth, high share
    {"name": "Tacos al Pastor", "price": 12.99, "category": "Tacos", "description": "Marinated pork with pineapple, cilantro, and onion"},
    {"name": "Guacamole Premium", "price": 8.99, "category": "Appetizers", "description": "Fresh avocado with lime, cilantro, and jalapeño"},
    
    # Cash Cows - Low growth, high share  
    {"name": "Quesadilla de Queso", "price": 7.99, "category": "Quesadillas", "description": "Melted cheese in flour tortilla"},
    {"name": "Arroz con Pollo", "price": 14.99, "category": "Main Courses", "description": "Chicken with Mexican rice and beans"},
    {"name": "Nachos Supreme", "price": 11.99, "category": "Appetizers", "description": "Tortilla chips with cheese, beans, and jalapeños"},
    
    # Question Marks - High growth, low share
    {"name": "Birria Tacos", "price": 15.99, "category": "Tacos", "description": "Slow-braised beef tacos with consommé"},
    {"name": "Elote Callejero", "price": 5.99, "category": "Sides", "description": "Street corn with mayo, cotija, and chili"},
    
    # Dogs - Low growth, low share
    {"name": "Ensalada Verde", "price": 6.99, "category": "Salads", "description": "Mixed greens with lime vinaigrette"},
    {"name": "Sopa de Tortilla", "price": 5.99, "category": "Soups", "description": "Tomato broth with crispy tortilla strips"},
    {"name": "Flan", "price": 4.99, "category": "Desserts", "description": "Traditional caramel custard"},
]

# BCG classification for demo
BCG_CLASSIFICATION = {
    "Tacos al Pastor": {"category": "STAR", "growth": 0.85, "share": 0.75, "revenue": 15000},
    "Guacamole Premium": {"category": "STAR", "growth": 0.72, "share": 0.68, "revenue": 8500},
    "Quesadilla de Queso": {"category": "CASH_COW", "growth": 0.15, "share": 0.82, "revenue": 12000},
    "Arroz con Pollo": {"category": "CASH_COW", "growth": 0.20, "share": 0.70, "revenue": 18000},
    "Nachos Supreme": {"category": "CASH_COW", "growth": 0.18, "share": 0.65, "revenue": 9500},
    "Birria Tacos": {"category": "QUESTION_MARK", "growth": 0.90, "share": 0.25, "revenue": 4500},
    "Elote Callejero": {"category": "QUESTION_MARK", "growth": 0.78, "share": 0.30, "revenue": 2800},
    "Ensalada Verde": {"category": "DOG", "growth": 0.08, "share": 0.20, "revenue": 1200},
    "Sopa de Tortilla": {"category": "DOG", "growth": 0.12, "share": 0.22, "revenue": 1500},
    "Flan": {"category": "DOG", "growth": 0.10, "share": 0.18, "revenue": 900},
}

BCG_INSIGHTS = {
    "STAR": "Your Stars (Tacos al Pastor, Guacamole) are driving growth! Invest in marketing and consider premium variations.",
    "CASH_COW": "Cash Cows (Quesadilla, Arroz con Pollo, Nachos) generate steady revenue. Maintain quality and optimize costs.",
    "QUESTION_MARK": "Question Marks (Birria Tacos, Elote) show potential. Consider promotional campaigns to increase market share.",
    "DOG": "Dogs (Ensalada, Sopa, Flan) have low performance. Evaluate if they should be repositioned or removed.",
}

DEMO_CAMPAIGNS = [
    {
        "title": "Taco Tuesday Fiesta",
        "objective": "Increase Star product sales by 25%",
        "target_category": "STAR",
        "target_audience": "Young professionals aged 25-40 who love authentic Mexican food",
        "copy": {
            "social_media": "🌮 TACO TUESDAY IS HERE! 🌮\n\nOur legendary Tacos al Pastor are calling your name! Marinated pork, fresh pineapple, cilantro perfection.\n\n🔥 $2 OFF all tacos today!\n📍 [Location]\n\n#TacoTuesday #TacosAlPastor #AuthenticMexican",
            "email_subject": "🌮 Your Taco Tuesday Deal is Ready!",
            "email_body": "Hey foodie!\n\nWe know you've been craving our famous Tacos al Pastor. Today's the day!\n\nGet $2 OFF all tacos this Tuesday. Our slow-marinated pork with fresh pineapple is waiting for you.\n\nSee you soon!\n- The MenuPilot Demo Restaurant Team"
        },
        "timing": "Every Tuesday, 11am-9pm",
        "expected_impact": "15-25% increase in taco sales, 10% increase in overall Tuesday traffic",
        "rationale": "Tacos al Pastor is our top Star product. A dedicated promotion day builds habit and drives consistent traffic."
    },
    {
        "title": "Birria Buzz Campaign",
        "objective": "Convert Question Mark to Star by increasing market share",
        "target_category": "QUESTION_MARK",
        "target_audience": "Food trend followers and social media influencers",
        "copy": {
            "social_media": "🔥 THE BIRRIA EXPERIENCE 🔥\n\nDip. Bite. Repeat.\n\nOur Birria Tacos come with rich consommé that'll change your life. Slow-braised beef, melted cheese, pure magic.\n\n📸 Tag us for a chance to win FREE birria for a month!\n\n#BirriaTacos #FoodTrend #MustTry",
            "email_subject": "Have You Tried Our Viral Birria Tacos? 🔥",
            "email_body": "The internet is obsessed with Birria Tacos, and ours are the real deal.\n\nSlow-braised beef, gooey cheese, and that iconic consommé for dipping. It's not just a meal – it's an experience.\n\nCome see what the hype is about!\n\nFirst-timers get 15% off with code: BIRRIA15"
        },
        "timing": "Weekend lunch rush, Friday-Sunday 11am-3pm",
        "expected_impact": "40% increase in Birria Taco orders, strong social media engagement",
        "rationale": "Birria is trending nationally. Capitalizing on this trend can convert this Question Mark into a Star."
    },
    {
        "title": "Family Feast Bundle",
        "objective": "Maximize Cash Cow revenue through bundling",
        "target_category": "CASH_COW",
        "target_audience": "Families with children, groups of 4+",
        "copy": {
            "social_media": "👨‍👩‍👧‍👦 FAMILY FEAST DEAL 👨‍👩‍👧‍👦\n\nFeed the whole crew without breaking the bank!\n\n🍽️ 4 Quesadillas\n🍽️ 2 Arroz con Pollo\n🍽️ 1 Nachos Supreme\n🥤 4 Drinks\n\nALL FOR $49.99 (Save $15!)\n\n#FamilyDinner #MexicanFood #ValueDeal",
            "email_subject": "Feed Your Family for Less! 👨‍👩‍👧‍👦",
            "email_body": "Family dinner just got easier AND cheaper!\n\nOur Family Feast Bundle includes:\n• 4 Quesadillas de Queso\n• 2 Arroz con Pollo plates\n• 1 Nachos Supreme to share\n• 4 Drinks\n\nAll for just $49.99 (normally $65)!\n\nPerfect for busy weeknights. Order online for pickup or delivery."
        },
        "timing": "Weekday evenings 5pm-8pm, all day weekends",
        "expected_impact": "20% increase in family-sized orders, higher average ticket",
        "rationale": "Bundling Cash Cows increases average order value while giving customers perceived savings."
    }
]

def generate_sales_data(days=90):
    """Generate realistic sales data for the past N days."""
    sales = []
    base_date = datetime.now() - timedelta(days=days)
    
    for i in range(days):
        date = base_date + timedelta(days=i)
        day_of_week = date.weekday()
        
        # Weekend boost
        weekend_multiplier = 1.3 if day_of_week in [4, 5, 6] else 1.0
        
        for item in DEMO_MENU_ITEMS:
            bcg = BCG_CLASSIFICATION.get(item["name"], {})
            base_sales = bcg.get("revenue", 1000) / 30  # Daily average
            
            # Add some randomness
            daily_sales = base_sales * weekend_multiplier * random.uniform(0.7, 1.3)
            quantity = int(daily_sales / item["price"])
            
            sales.append({
                "date": date.strftime("%Y-%m-%d"),
                "item_name": item["name"],
                "quantity": quantity,
                "revenue": round(quantity * item["price"], 2),
                "category": item["category"]
            })
    
    return sales

def create_demo_json():
    """Create demo data JSON files."""
    
    # Menu data
    menu_data = {
        "session_id": DEMO_SESSION_ID,
        "items": DEMO_MENU_ITEMS,
        "categories": list(set(item["category"] for item in DEMO_MENU_ITEMS)),
        "extraction_confidence": 0.95
    }
    
    # BCG data
    bcg_items = []
    for item in DEMO_MENU_ITEMS:
        bcg = BCG_CLASSIFICATION.get(item["name"], {})
        bcg_items.append({
            "name": item["name"],
            "price": item["price"],
            "category": bcg.get("category", "UNKNOWN"),
            "growth": bcg.get("growth", 0.5),
            "share": bcg.get("share", 0.5),
            "revenue": bcg.get("revenue", 0)
        })
    
    bcg_data = {
        "session_id": DEMO_SESSION_ID,
        "items": bcg_items,
        "insights": BCG_INSIGHTS,
        "summary": "Your menu shows a healthy mix with strong Stars driving growth and reliable Cash Cows generating steady revenue. Focus marketing on Stars, optimize Cash Cow costs, evaluate Question Marks for investment, and consider refreshing Dogs."
    }
    
    # Campaign data
    campaign_data = {
        "session_id": DEMO_SESSION_ID,
        "campaigns": DEMO_CAMPAIGNS,
        "thought_process": "Analyzed BCG matrix to create targeted campaigns. Stars get awareness campaigns, Question Marks get conversion campaigns, and Cash Cows get bundling strategies."
    }
    
    # Full session
    session_data = {
        "session_id": DEMO_SESSION_ID,
        "status": "completed",
        "created_at": datetime.now().isoformat(),
        "menu": menu_data,
        "bcg": bcg_data,
        "campaigns": campaign_data
    }
    
    # Save files
    import os
    os.makedirs("data/demo", exist_ok=True)
    
    with open("data/demo/menu.json", "w") as f:
        json.dump(menu_data, f, indent=2)
    
    with open("data/demo/bcg.json", "w") as f:
        json.dump(bcg_data, f, indent=2)
    
    with open("data/demo/campaigns.json", "w") as f:
        json.dump(campaign_data, f, indent=2)
    
    with open("data/demo/session.json", "w") as f:
        json.dump(session_data, f, indent=2)
    
    # Generate and save sales data
    sales_data = generate_sales_data(90)
    with open("data/demo/sales.json", "w") as f:
        json.dump(sales_data, f, indent=2)
    
    print("✅ Demo data created successfully!")
    print(f"   - Menu: {len(DEMO_MENU_ITEMS)} items")
    print(f"   - BCG: {len(bcg_items)} classified items")
    print(f"   - Campaigns: {len(DEMO_CAMPAIGNS)} campaigns")
    print(f"   - Sales: {len(sales_data)} records")
    print(f"\nFiles saved to data/demo/")

if __name__ == "__main__":
    create_demo_json()
