"""
chatbot.py — Rule-based AI Travel Assistant for Traveloop.
No third-party APIs required. Uses NLP-style keyword matching
against the built-in city/activity knowledge base.
"""
from models import CITIES, CITY_ACTIVITIES
import re

# ── Intent patterns (compiled for performance) ───────────────────────
INTENTS = {
    'greeting':    re.compile(r'\b(hi|hello|hey|howdy|greetings|sup)\b', re.I),
    'budget':      re.compile(r'\b(budget|cost|cheap|expensive|afford|price|money|spend)\b', re.I),
    'recommend':   re.compile(r'\b(recommend|suggest|where|should i go|best|top|popular)\b', re.I),
    'activity':    re.compile(r'\b(activity|activities|things to do|what to do|see|visit|explore|sightseeing)\b', re.I),
    'food':        re.compile(r'\b(food|eat|restaurant|cuisine|cooking|dining|meal)\b', re.I),
    'packing':     re.compile(r'\b(pack|packing|bring|carry|checklist|essentials|luggage)\b', re.I),
    'weather':     re.compile(r'\b(weather|climate|temperature|rain|season|when to go)\b', re.I),
    'safety':      re.compile(r'\b(safe|safety|danger|scam|precaution|tips)\b', re.I),
    'compare':     re.compile(r'\b(compare|vs|versus|difference|better)\b', re.I),
    'help':        re.compile(r'\b(help|can you|what can|how do)\b', re.I),
}

# ── City detection ───────────────────────────────────────────────────
CITY_NAMES = {name.lower(): name for name in CITIES.keys()}

def detect_city(text: str) -> str | None:
    """Extract a city name from user input."""
    text_lower = text.lower()
    for key, name in CITY_NAMES.items():
        if key in text_lower:
            return name
    return None

def detect_intent(text: str) -> str:
    """Determine user's intent from their message."""
    for intent, pattern in INTENTS.items():
        if pattern.search(text):
            return intent
    return 'unknown'


def get_response(user_message: str) -> str:
    """Generate a response based on user message. Core chatbot logic."""
    if not user_message or not user_message.strip():
        return "👋 Hi! I'm your Traveloop travel assistant. Ask me about destinations, budgets, activities, or packing tips!"

    intent = detect_intent(user_message)
    city = detect_city(user_message)

    # ── Greeting ──
    if intent == 'greeting':
        return ("👋 Hello! I'm your Traveloop AI assistant. I can help with:\n"
                "• 🌍 Destination recommendations\n"
                "• 💰 Budget estimates for any city\n"
                "• 🎯 Activity suggestions\n"
                "• 🧳 Packing checklists\n"
                "• 🍽️ Food recommendations\n\n"
                "Just ask! e.g. \"What's the budget for Paris?\"")

    # ── Budget query ──
    if intent == 'budget':
        if city:
            c = CITIES[city]
            return (f"💰 **{city} Budget Breakdown:**\n"
                    f"• 🏨 Hotels: ~${c['hotel_avg']}/night\n"
                    f"• 🍽️ Food: ~${c['food_avg']}/day\n"
                    f"• 🚌 Transport: ~${c['transport_avg']}/day\n"
                    f"• 📊 Daily total: ~${c['daily_budget']}/day\n\n"
                    f"For a 5-day trip: ~${c['daily_budget'] * 5} total.\n"
                    f"Cost level: {c['cost_index']}")
        # No city specified — show cheapest/most expensive
        sorted_cities = sorted(CITIES.items(), key=lambda x: x[1]['daily_budget'])
        cheapest = sorted_cities[:3]
        return ("💰 **Budget-friendly destinations:**\n" +
                "\n".join(f"• {n}: ~${d['daily_budget']}/day ({d['cost_index']})" for n, d in cheapest) +
                "\n\n💎 **Premium destinations:**\n" +
                "\n".join(f"• {n}: ~${d['daily_budget']}/day ({d['cost_index']})" for n, d in sorted_cities[-3:]) +
                "\n\nAsk about a specific city for a full breakdown!")

    # ── Recommendations ──
    if intent == 'recommend':
        if 'cheap' in user_message.lower() or 'budget' in user_message.lower():
            picks = sorted(CITIES.items(), key=lambda x: x[1]['daily_budget'])[:4]
            return ("🌴 **Best budget destinations:**\n" +
                    "\n".join(f"• {n} ({d['country']}) — ${d['daily_budget']}/day — {d['pop']}" for n, d in picks))
        return ("🌍 **Top recommended destinations:**\n" +
                "\n".join(f"• {n} ({d['country']}) — {d['pop']} — {d['cost_index']}"
                          for n, d in list(CITIES.items())[:6]) +
                "\n\nTell me your budget or interests and I'll narrow it down!")

    # ── Activities ──
    if intent == 'activity':
        if city:
            acts = CITY_ACTIVITIES.get(city, [])
            if acts:
                return (f"🎯 **Top activities in {city}:**\n" +
                        "\n".join(f"• {a['name']} ({a['type']}) — ${a['cost']} · {a['duration']}" for a in acts))
            return f"I don't have activity data for {city} yet. Try Paris, Tokyo, or Bali!"
        return "🎯 Which city? Ask me \"activities in Tokyo\" or \"things to do in Paris\"!"

    # ── Food ──
    if intent == 'food':
        if city:
            acts = [a for a in CITY_ACTIVITIES.get(city, []) if a['type'] == 'Food']
            c = CITIES[city]
            resp = f"🍽️ **Food in {city}:**\n• Average daily food cost: ${c['food_avg']}\n"
            if acts:
                resp += "\n**Food experiences:**\n" + "\n".join(f"• {a['name']} — ${a['cost']} · {a['duration']}" for a in acts)
            return resp
        return "🍽️ Which city's food scene are you curious about? Try \"food in Tokyo\"!"

    # ── Packing ──
    if intent == 'packing':
        return ("🧳 **Universal packing checklist:**\n"
                "📄 **Documents:** Passport, visa, travel insurance, hotel bookings\n"
                "👕 **Clothing:** Weather-appropriate layers, comfortable shoes\n"
                "💊 **Health:** Medications, sunscreen, first-aid kit\n"
                "📱 **Electronics:** Phone charger, adapter, power bank\n"
                "🧴 **Toiletries:** Travel-size essentials\n"
                "💰 **Money:** Local currency, backup card\n\n"
                "Pro tip: Roll clothes to save space! 🎒")

    # ── Weather ──
    if intent == 'weather':
        if city:
            tips = {
                "Paris": "🌤️ Best: Apr-Jun & Sep-Oct. Mild 15-25°C. Pack layers!",
                "Tokyo": "🌸 Best: Mar-May (cherry blossoms) & Oct-Nov. Humid summers.",
                "Bali": "☀️ Dry season: Apr-Oct. Tropical 27-30°C year-round.",
                "New York": "🍂 Best: Apr-Jun & Sep-Nov. Cold winters, hot summers.",
                "Santorini": "☀️ Best: Jun-Sep. Mediterranean climate, very sunny.",
            }
            return tips.get(city, f"🌡️ I'd recommend checking a weather forecast closer to your travel date for {city}!")
        return "🌡️ Which city? Ask \"weather in Bali\" for seasonal tips!"

    # ── Safety ──
    if intent == 'safety':
        return ("🛡️ **General travel safety tips:**\n"
                "• Keep copies of important documents\n"
                "• Use hotel safes for valuables\n"
                "• Be cautious of common tourist scams\n"
                "• Register with your embassy\n"
                "• Get travel insurance\n"
                "• Share your itinerary with someone back home")

    # ── Compare ──
    if intent == 'compare':
        cities_found = []
        for key, name in CITY_NAMES.items():
            if key in user_message.lower():
                cities_found.append(name)
        if len(cities_found) >= 2:
            c1, c2 = CITIES[cities_found[0]], CITIES[cities_found[1]]
            return (f"⚖️ **{cities_found[0]} vs {cities_found[1]}:**\n"
                    f"{'Category':<12} | {cities_found[0]:<12} | {cities_found[1]:<12}\n"
                    f"{'Daily cost':<12} | ${c1['daily_budget']:<11} | ${c2['daily_budget']}\n"
                    f"{'Hotel/night':<12} | ${c1['hotel_avg']:<11} | ${c2['hotel_avg']}\n"
                    f"{'Food/day':<12} | ${c1['food_avg']:<11} | ${c2['food_avg']}\n"
                    f"{'Cost level':<12} | {c1['cost_index']:<12} | {c2['cost_index']}")
        return "⚖️ Name two cities to compare! e.g. \"compare Paris vs Bali\""

    # ── Help ──
    if intent == 'help':
        return ("🤖 **I can help with:**\n"
                "• \"Budget for Tokyo\" — cost breakdown\n"
                "• \"Activities in Paris\" — top things to do\n"
                "• \"Compare Bali vs Bangkok\" — side-by-side\n"
                "• \"Recommend cheap destinations\" — budget picks\n"
                "• \"Food in Rome\" — cuisine tips\n"
                "• \"Packing tips\" — universal checklist\n"
                "• \"Weather in Santorini\" — best time to visit")

    # ── Fallback: try city info ──
    if city:
        c = CITIES[city]
        acts = CITY_ACTIVITIES.get(city, [])
        resp = (f"🌍 **{city}, {c['country']}**\n"
                f"• Daily budget: ~${c['daily_budget']} ({c['cost_index']})\n"
                f"• {c['pop']}\n")
        if acts:
            resp += f"• {len(acts)} activities available\n"
        resp += "\nAsk about budget, activities, or food for more details!"
        return resp

    return ("🤔 I'm not sure what you mean. Try asking:\n"
            "• \"Budget for Paris\"\n"
            "• \"Activities in Tokyo\"\n"
            "• \"Recommend destinations\"\n"
            "• \"Packing tips\"\n"
            "• Type **help** for all commands")
