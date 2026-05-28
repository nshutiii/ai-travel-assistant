from typing import List, Dict

# This acts as our "Local Intelligence" - real data for top destinations
TRAVEL_DATA = {
    "paris": {
        "hotels": [
            {"name": "Generator Hostel Paris", "desc": "Trendy, design-forward hostel with a gorgeous rooftop terrace in the 10th arrondissement.", "cost": 45, "style": ["Budget", "Adventure"]},
            {"name": "Hotel Caron de Beaumarchais", "desc": "Historic 18th-century themed boutique hotel located in the historic Marais district.", "cost": 150, "style": ["Leisure", "Business"]},
            {"name": "The Ritz Paris", "desc": "World-famous legendary luxury hotel on Place Vendôme with standard-setting service.", "cost": 650, "style": ["Luxury"]}
        ],
        "landmarks": [
            {"name": "Eiffel Tower", "desc": "Iconic iron lattice tower on the Champ de Mars.", "cost": 28, "style": ["Leisure", "Luxury"]},
            {"name": "Louvre Museum", "desc": "World's largest art museum and a historic monument.", "cost": 22, "style": ["Leisure", "Business"]},
            {"name": "Montmartre", "desc": "Large hill in Paris's 18th arrondissement.", "cost": 0, "style": ["Adventure", "Leisure"]},
            {"name": "Arc de Triomphe", "desc": "One of the most famous monuments in Paris.", "cost": 13, "style": ["Leisure"]},
            {"name": "Seine River Cruise", "desc": "Relaxing boat tour through the heart of the city.", "cost": 15, "style": ["Leisure", "Luxury"]}
        ],
        "restaurants": [
            {"name": "Le Comptoir de la Gastronomie", "dish": "Famous Foie Gras and Duck Confit", "cost": 45, "style": ["Luxury"]},
            {"name": "L'As du Fallafel", "dish": "Best Falafel in the Marais", "cost": 12, "style": ["Budget", "Adventure"]},
            {"name": "Angelina Paris", "dish": "Old-school tea house known for hot chocolate", "cost": 25, "style": ["Luxury", "Leisure"]},
            {"name": "Bouillon Chartier", "dish": "Traditional French brasserie experience", "cost": 20, "style": ["Budget", "Leisure"]}
        ]
    },
    "tokyo": {
        "hotels": [
            {"name": "Nine Hours Capsule Hotel Shinjuku", "desc": "Modern, sleek capsule lodging designed for high-efficiency and comfort.", "cost": 38, "style": ["Budget", "Adventure"]},
            {"name": "Hotel Gracery Shinjuku", "desc": "Famous 'Godzilla' landmark hotel offering chic rooms in the vibrant Kabukicho district.", "cost": 140, "style": ["Leisure", "Business"]},
            {"name": "Park Hyatt Tokyo", "desc": "Iconic high-end luxury hotel featuring breathtaking panoramic views of Mount Fuji.", "cost": 500, "style": ["Luxury"]}
        ],
        "landmarks": [
            {"name": "Senso-ji Temple", "desc": "Tokyo's oldest and most significant Buddhist temple.", "cost": 0, "style": ["Leisure", "Adventure"]},
            {"name": "Shibuya Crossing", "desc": "The world's busiest pedestrian intersection.", "cost": 0, "style": ["Adventure", "Leisure"]},
            {"name": "Tokyo Skytree", "desc": "Observation tower with panoramic city views.", "cost": 25, "style": ["Leisure", "Luxury"]},
            {"name": "Meiji Jingu Shrine", "desc": "Shinto shrine dedicated to Emperor Meiji.", "cost": 0, "style": ["Leisure", "Business"]},
            {"name": "Akihabara Electric Town", "desc": "District famous for electronic shops and anime culture.", "cost": 0, "style": ["Adventure"]}
        ],
        "restaurants": [
            {"name": "Ichiran Ramen", "dish": "Classic Tonkotsu Ramen in private booths", "cost": 15, "style": ["Budget", "Leisure"]},
            {"name": "Sukiyabashi Jiro", "dish": "World-famous high-end sushi", "cost": 300, "style": ["Luxury"]},
            {"name": "Fuunji", "dish": "Famous Tsukemen (dipping noodles)", "cost": 12, "style": ["Budget", "Adventure"]},
            {"name": "Gonpachi Nishi-Azabu", "dish": "The 'Kill Bill' inspired Izakaya", "cost": 50, "style": ["Luxury", "Leisure"]}
        ]
    },
    "rome": {
        "hotels": [
            {"name": "The Beehive Hostel", "desc": "Cozy, green-conscious organic hostel and garden located near Termini Station.", "cost": 35, "style": ["Budget", "Adventure"]},
            {"name": "Hotel Santa Maria", "desc": "Charming boutique hotel located in a quiet former convent in Trastevere.", "cost": 160, "style": ["Leisure", "Business"]},
            {"name": "Hotel Hassler Roma", "desc": "Legendary ultra-luxury hotel situated at the absolute top of the Spanish Steps.", "cost": 600, "style": ["Luxury"]}
        ],
        "landmarks": [
            {"name": "Colosseum", "desc": "Ancient amphitheater in the center of the city.", "cost": 18, "style": ["Leisure", "Adventure"]},
            {"name": "Vatican Museums", "desc": "Christian and art museums located within Vatican City.", "cost": 25, "style": ["Leisure", "Luxury"]},
            {"name": "Trevi Fountain", "desc": "Stunning Baroque fountain where you toss a coin.", "cost": 0, "style": ["Leisure"]},
            {"name": "Pantheon", "desc": "Former Roman temple, now a Catholic church.", "cost": 5, "style": ["Leisure", "Business"]},
            {"name": "Trastevere District", "desc": "Charming medieval neighborhood with narrow streets.", "cost": 0, "style": ["Adventure", "Leisure"]}
        ],
        "restaurants": [
            {"name": "Roscioli", "dish": "The most famous Carbonara in Rome", "cost": 35, "style": ["Luxury", "Leisure"]},
            {"name": "Pizzeria Da Remo", "dish": "Authentic Roman thin-crust pizza", "cost": 15, "style": ["Budget", "Adventure"]},
            {"name": "Bonci Pizzarium", "dish": "World-class pizza al taglio", "cost": 12, "style": ["Budget", "Leisure"]},
            {"name": "La Pergola", "dish": "Michelin-starred dining with a view", "cost": 250, "style": ["Luxury"]}
        ]
    }
}

def generate_smart_itinerary(destination: str, days: int, trip_style: str, budget: float) -> List[Dict]:
    dest_key = destination.lower().strip()
    
    # If we have real data for this city, use it!
    if dest_key in TRAVEL_DATA:
        data = TRAVEL_DATA[dest_key]
        itinerary = []
        
        daily_budget = budget / max(days, 1)
        
        # Pick hotel based on budget and style
        style_match = trip_style.capitalize() if trip_style else "Leisure"
        selected_hotel = data["hotels"][0] # fallback
        for hotel in data["hotels"]:
            if style_match in hotel["style"] and hotel["cost"] <= daily_budget * 0.5:
                selected_hotel = hotel
                break
        else:
            # Pick the cheapest if none match the budget constraint perfectly
            selected_hotel = min(data["hotels"], key=lambda h: h["cost"])
            
        for d in range(1, days + 1):
            # Pick a landmark that fits within remaining budget
            rem_daily = daily_budget - selected_hotel["cost"]
            landmark = next((l for l in data["landmarks"] if style_match in l["style"] and l["cost"] < rem_daily * 0.4), data["landmarks"][0])
            
            # Pick a restaurant
            restaurant = next((r for r in data["restaurants"] if style_match in r["style"] and r["cost"] < rem_daily * 0.5), data["restaurants"][0])
            
            # Pick another landmark or activity
            extra = next((l for l in reversed(data["landmarks"]) if l != landmark), data["landmarks"][1])
            
            food_cost = restaurant["cost"] + 15.0 # Restaurant cost + buffer for other meals
            other_cost = landmark["cost"] + extra["cost"] + 5.0 # Sightseeing + local transit
            
            itinerary.append({
                "day": d,
                "activities": [
                    f"Morning: Visit {landmark['name']} - {landmark['desc']} (Est. cost: ${landmark['cost']})",
                    f"Afternoon: Lunch at {restaurant['name']} - Enjoy the {restaurant['dish']} (Est. cost: ${restaurant['cost']})",
                    f"Evening: Explore {extra['name']} - {extra['desc']} (Est. cost: ${extra['cost']})"
                ],
                "accommodation": f"{selected_hotel['name']} - {selected_hotel['desc']}",
                "accommodation_cost": float(selected_hotel["cost"]),
                "food_cost": float(food_cost),
                "other_cost": float(other_cost),
                "total_day_cost": float(selected_hotel["cost"] + food_cost + other_cost)
            })
        return itinerary

    # Fallback for other cities (Enhanced template)
    itinerary = []
    daily_budget = budget / max(days, 1)
    
    # Estimate a hotel based on budget
    est_hotel_cost = round(daily_budget * 0.45, 2)
    est_food_cost = round(daily_budget * 0.3, 2)
    est_other_cost = round(daily_budget * 0.2, 2)
    
    for i in range(1, days + 1):
        itinerary.append({
            "day": i,
            "activities": [
                f"Morning: Explore the historic center of {destination} (Est. cost: Free)",
                f"Afternoon: Lunch at a highly-rated local bistro in {destination} (Est. cost: ${round(est_food_cost * 0.6, 2)})",
                f"Evening: Visit a top-rated attraction based on your {trip_style} style (Est. cost: ${round(est_other_cost * 0.7, 2)})"
            ],
            "accommodation": f"Comfortable local hotel in {destination} matching {trip_style} style",
            "accommodation_cost": float(est_hotel_cost),
            "food_cost": float(est_food_cost),
            "other_cost": float(est_other_cost),
            "total_day_cost": float(est_hotel_cost + est_food_cost + est_other_cost)
        })
    return itinerary
