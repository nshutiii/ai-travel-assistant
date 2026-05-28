import json
from typing import List, Dict
from duckduckgo_search import DDGS

def generate_duck_itinerary(destination: str, days: int, trip_style: str, budget: float) -> List[Dict]:
    """
    Generates a structured travel itinerary using DuckDuckGo's free AI (GPT-4o-mini).
    No API key required, highly reliable.
    """
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
        with DDGS() as ddgs:
            # Using gpt-4o-mini via DuckDuckGo AI
            results = ddgs.chat(prompt, model='gpt-4o-mini')
            
            # Clean up response text in case it includes markdown
            text = results.strip()
            if text.startswith("```json"):
                text = text.split("```json")[1].split("```")[0].strip()
            elif text.startswith("```"):
                text = text.split("```")[1].split("```")[0].strip()
            
            # Find the first '[' and last ']' to extract JSON array
            start = text.find('[')
            end = text.rfind(']') + 1
            if start != -1 and end > start:
                text = text[start:end]
                
            itinerary_data = json.loads(text)
            return itinerary_data
    except Exception as e:
        print(f"Duck AI Generation failed: {e}")
        # Return empty list to trigger the next fallback in the router
        return []
