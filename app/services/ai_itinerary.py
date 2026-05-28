import os
import json
import google.generativeai as genai
from typing import List, Dict
from app.core.config import get_settings

settings = get_settings()

if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

def generate_ai_itinerary(destination: str, days: int, trip_style: str, budget: float) -> List[Dict]:
    """
    Generates a structured travel itinerary using Google Gemini.
    """
    if not settings.gemini_api_key:
        # Fallback to sample data if no API key is provided
        return _get_fallback_itinerary(destination, days, budget)

    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""
    Create a highly specific, realistic {days}-day travel itinerary for {destination}.
    USER CONSTRAINTS:
    - Trip Style: {trip_style}
    - TOTAL BUDGET: ${budget} for the entire {days} days. THIS BUDGET MUST COVER LODGING, MEALS, AND ALL ACTIVITIES.
    
    CRITICAL REQUIREMENTS:
    1. BUDGET ALLOCATION: Split the total budget of ${budget} dynamically between:
       - Accommodation (approx. 40-50% of the total budget)
       - Food & Dining (approx. 25-30% of the total budget)
       - Sightseeing & Activities (approx. 20-25% of the total budget)
       The daily sum of (accommodation_cost + food_cost + other_cost) multiplied by {days} days must be less than or equal to ${budget}.
    2. REAL-WORLD DATA: Use ONLY real-world, currently existing hotels/accommodations, restaurants, and landmarks in {destination}.
    3. VARIETY: For each day, provide exactly 3 distinct activities (Morning, Afternoon, Evening).
       - Morning and Evening should focus on experiences or attractions.
       - Afternoon must recommend a specific, real restaurant for lunch.
    4. DETAILED VALUES: Every day must contain:
       - A real hotel recommended for "accommodation".
       - Precise numeric cost estimates for accommodation_cost, food_cost, other_cost, and total_day_cost.
    
    Return the result ONLY as a JSON array of objects with this structure (no markdown fences, no conversational text):
    [
      {{
        "day": 1,
        "activities": [
          "Morning: Visit [Real Landmark] - [Description] (Est. cost: [Price])",
          "Afternoon: Lunch at [Real Restaurant Name] - Known for [Dish] (Est. cost: [Price])",
          "Evening: Explore [Real Area] for [Activity] (Est. cost: [Price])"
        ],
        "accommodation": "[Real Hotel Name] - [Brief desc, e.g., Boutique hotel in city center]",
        "accommodation_cost": [Estimated hotel cost per night as float, e.g. 75.0],
        "food_cost": [Estimated daily food cost as float, e.g. 40.0],
        "other_cost": [Estimated daily activities/transit cost as float, e.g. 20.0],
        "total_day_cost": [Sum of accommodation_cost + food_cost + other_cost as float, e.g. 135.0]
      }},
      ...
    ]
    """

    try:
        response = model.generate_content(prompt)
        if not response or not response.text:
            print("AI returned an empty response")
            return _get_fallback_itinerary(destination, days, budget)
            
        # Extract JSON from the response text
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        itinerary_data = json.loads(text)
        return itinerary_data
    except Exception as e:
        print(f"AI Generation Error ({type(e).__name__}): {e}")
        return _get_fallback_itinerary(destination, days, budget)

def _get_fallback_itinerary(destination: str, days: int, budget: float = 1000.0) -> List[Dict]:
    """Sample data if AI generation fails or is unavailable."""
    itinerary = []
    daily_budget = budget / max(days, 1)
    for i in range(1, days + 1):
        itinerary.append({
            "day": i,
            "activities": [
                f"Morning: Explore the historic center of {destination} (Est. cost: Free)",
                f"Afternoon: Lunch at a highly-rated local bistro in {destination} (Est. cost: ${round(daily_budget * 0.25, 2)})",
                f"Evening: Visit a top-rated local attraction (Est. cost: ${round(daily_budget * 0.2, 2)})"
            ],
            "accommodation": f"Charming local hotel in {destination}",
            "accommodation_cost": round(daily_budget * 0.45, 2),
            "food_cost": round(daily_budget * 0.25, 2),
            "other_cost": round(daily_budget * 0.2, 2),
            "total_day_cost": round(daily_budget * 0.9, 2)
        })
    return itinerary
