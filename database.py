import sqlite3, os, json

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'traveloop.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ── Rich city & activity data for auto-planning ──
CITIES = {
    "Paris": {"country":"France","daily_budget":150,"hotel_avg":120,"transport_avg":15,"food_avg":45,
              "img":"https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=600&q=80","pop":"Iconic","cost_index":"$$$"},
    "Tokyo": {"country":"Japan","daily_budget":130,"hotel_avg":100,"transport_avg":12,"food_avg":35,
              "img":"https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=600&q=80","pop":"Trending","cost_index":"$$$"},
    "Bali":  {"country":"Indonesia","daily_budget":50,"hotel_avg":30,"transport_avg":8,"food_avg":12,
              "img":"https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=600&q=80","pop":"Top Rated","cost_index":"$"},
    "New York":{"country":"USA","daily_budget":200,"hotel_avg":180,"transport_avg":20,"food_avg":50,
               "img":"https://images.unsplash.com/photo-1534430480872-3498386e7856?w=600&q=80","pop":"Always Buzzing","cost_index":"$$$$"},
    "Santorini":{"country":"Greece","daily_budget":140,"hotel_avg":110,"transport_avg":10,"food_avg":40,
                 "img":"https://images.unsplash.com/photo-1613395877344-13d4a8e0d49e?w=600&q=80","pop":"Romantic","cost_index":"$$$"},
    "Kyoto": {"country":"Japan","daily_budget":110,"hotel_avg":80,"transport_avg":10,"food_avg":30,
              "img":"https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=600&q=80","pop":"Cultural","cost_index":"$$"},
    "Cape Town":{"country":"South Africa","daily_budget":70,"hotel_avg":50,"transport_avg":10,"food_avg":20,
                 "img":"https://images.unsplash.com/photo-1580060839134-75a5edca2e99?w=600&q=80","pop":"Hidden Gem","cost_index":"$$"},
    "Marrakech":{"country":"Morocco","daily_budget":45,"hotel_avg":25,"transport_avg":5,"food_avg":10,
                 "img":"https://images.unsplash.com/photo-1597212618440-806262de4f6b?w=600&q=80","pop":"Exotic","cost_index":"$"},
    "London": {"country":"UK","daily_budget":180,"hotel_avg":150,"transport_avg":18,"food_avg":45,
               "img":"https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=600&q=80","pop":"Classic","cost_index":"$$$$"},
    "Dubai":  {"country":"UAE","daily_budget":160,"hotel_avg":130,"transport_avg":15,"food_avg":40,
               "img":"https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=600&q=80","pop":"Luxury","cost_index":"$$$$"},
    "Bangkok":{"country":"Thailand","daily_budget":40,"hotel_avg":20,"transport_avg":5,"food_avg":10,
               "img":"https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=600&q=80","pop":"Budget Friendly","cost_index":"$"},
    "Rome":   {"country":"Italy","daily_budget":130,"hotel_avg":100,"transport_avg":12,"food_avg":35,
               "img":"https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=600&q=80","pop":"Historic","cost_index":"$$$"},
}

CITY_ACTIVITIES = {
    "Paris": [
        {"name":"Eiffel Tower Visit","type":"Sightseeing","cost":26,"duration":"2h","time":"10:00"},
        {"name":"Louvre Museum","type":"Culture","cost":17,"duration":"3h","time":"13:00"},
        {"name":"Seine River Cruise","type":"Leisure","cost":15,"duration":"1h","time":"17:00"},
        {"name":"Montmartre Walking Tour","type":"Sightseeing","cost":0,"duration":"2h","time":"09:00"},
        {"name":"French Cooking Class","type":"Food","cost":80,"duration":"3h","time":"18:00"},
    ],
    "Tokyo": [
        {"name":"Shibuya Crossing & Harajuku","type":"Sightseeing","cost":0,"duration":"3h","time":"10:00"},
        {"name":"Tsukiji Outer Market Food Tour","type":"Food","cost":40,"duration":"2h","time":"07:00"},
        {"name":"Senso-ji Temple","type":"Culture","cost":0,"duration":"1.5h","time":"09:00"},
        {"name":"TeamLab Borderless","type":"Entertainment","cost":30,"duration":"2h","time":"14:00"},
        {"name":"Ramen Tasting Tour","type":"Food","cost":25,"duration":"2h","time":"19:00"},
    ],
    "Bali": [
        {"name":"Tegallalang Rice Terraces","type":"Sightseeing","cost":5,"duration":"2h","time":"08:00"},
        {"name":"Ubud Monkey Forest","type":"Adventure","cost":4,"duration":"2h","time":"10:00"},
        {"name":"Bali Spa & Massage","type":"Wellness","cost":30,"duration":"3h","time":"14:00"},
        {"name":"Uluwatu Temple Sunset","type":"Culture","cost":5,"duration":"2h","time":"16:00"},
        {"name":"Cooking Class with Local Family","type":"Food","cost":25,"duration":"4h","time":"09:00"},
    ],
    "New York": [
        {"name":"Statue of Liberty & Ellis Island","type":"Sightseeing","cost":24,"duration":"4h","time":"09:00"},
        {"name":"Central Park Walking Tour","type":"Leisure","cost":0,"duration":"2h","time":"07:00"},
        {"name":"Broadway Show","type":"Entertainment","cost":120,"duration":"3h","time":"19:00"},
        {"name":"MoMA Museum","type":"Culture","cost":25,"duration":"3h","time":"13:00"},
        {"name":"Brooklyn Food Tour","type":"Food","cost":65,"duration":"3h","time":"11:00"},
    ],
    "Santorini": [
        {"name":"Oia Sunset Viewpoint","type":"Sightseeing","cost":0,"duration":"2h","time":"17:00"},
        {"name":"Catamaran Sailing Cruise","type":"Adventure","cost":120,"duration":"5h","time":"10:00"},
        {"name":"Wine Tasting Tour","type":"Food","cost":45,"duration":"3h","time":"14:00"},
        {"name":"Akrotiri Archaeological Site","type":"Culture","cost":12,"duration":"2h","time":"09:00"},
    ],
    "Kyoto": [
        {"name":"Fushimi Inari Shrine","type":"Culture","cost":0,"duration":"2h","time":"07:00"},
        {"name":"Bamboo Grove Walk","type":"Sightseeing","cost":0,"duration":"1.5h","time":"09:30"},
        {"name":"Geisha District Tour","type":"Culture","cost":15,"duration":"2h","time":"16:00"},
        {"name":"Traditional Tea Ceremony","type":"Culture","cost":30,"duration":"1h","time":"14:00"},
        {"name":"Nishiki Market Food Tour","type":"Food","cost":35,"duration":"2h","time":"11:00"},
    ],
    "Cape Town": [
        {"name":"Table Mountain Hike","type":"Adventure","cost":15,"duration":"4h","time":"08:00"},
        {"name":"Cape Point Drive","type":"Sightseeing","cost":10,"duration":"6h","time":"09:00"},
        {"name":"V&A Waterfront","type":"Leisure","cost":0,"duration":"3h","time":"15:00"},
        {"name":"Winelands Day Trip","type":"Food","cost":50,"duration":"8h","time":"09:00"},
    ],
    "Marrakech": [
        {"name":"Medina Souk Tour","type":"Culture","cost":0,"duration":"3h","time":"10:00"},
        {"name":"Jardin Majorelle","type":"Sightseeing","cost":10,"duration":"1.5h","time":"14:00"},
        {"name":"Hammam Spa Experience","type":"Wellness","cost":20,"duration":"2h","time":"16:00"},
        {"name":"Moroccan Cooking Class","type":"Food","cost":30,"duration":"3h","time":"18:00"},
    ],
    "London": [
        {"name":"British Museum","type":"Culture","cost":0,"duration":"3h","time":"10:00"},
        {"name":"Tower of London","type":"Sightseeing","cost":30,"duration":"3h","time":"09:00"},
        {"name":"West End Theatre Show","type":"Entertainment","cost":70,"duration":"3h","time":"19:00"},
        {"name":"Borough Market Food Walk","type":"Food","cost":20,"duration":"2h","time":"12:00"},
        {"name":"Thames River Cruise","type":"Leisure","cost":18,"duration":"1h","time":"15:00"},
    ],
    "Dubai": [
        {"name":"Burj Khalifa Observation","type":"Sightseeing","cost":40,"duration":"2h","time":"17:00"},
        {"name":"Desert Safari with BBQ","type":"Adventure","cost":60,"duration":"6h","time":"14:00"},
        {"name":"Dubai Mall & Aquarium","type":"Leisure","cost":35,"duration":"3h","time":"10:00"},
        {"name":"Gold Souk & Old Dubai Tour","type":"Culture","cost":0,"duration":"2h","time":"09:00"},
    ],
    "Bangkok": [
        {"name":"Grand Palace & Wat Phra Kaew","type":"Culture","cost":15,"duration":"3h","time":"08:00"},
        {"name":"Chatuchak Weekend Market","type":"Leisure","cost":0,"duration":"4h","time":"10:00"},
        {"name":"Street Food Tour by Tuk-Tuk","type":"Food","cost":20,"duration":"3h","time":"18:00"},
        {"name":"Thai Massage Session","type":"Wellness","cost":10,"duration":"2h","time":"14:00"},
    ],
    "Rome": [
        {"name":"Colosseum & Roman Forum","type":"Sightseeing","cost":18,"duration":"3h","time":"09:00"},
        {"name":"Vatican Museums & Sistine Chapel","type":"Culture","cost":17,"duration":"4h","time":"08:00"},
        {"name":"Trastevere Food Tour","type":"Food","cost":55,"duration":"3h","time":"18:00"},
        {"name":"Trevi Fountain & Spanish Steps","type":"Sightseeing","cost":0,"duration":"2h","time":"14:00"},
    ],
}

def get_city_data(): return CITIES
def get_city_activities(city_name):
    return CITY_ACTIVITIES.get(city_name, [])

def init_db():
    if os.path.exists(DATABASE_PATH): os.remove(DATABASE_PATH)
    conn = get_db_connection()
    conn.executescript('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
            photo TEXT, language TEXT DEFAULT 'English'
        );
        CREATE TABLE trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            name TEXT NOT NULL, description TEXT, start_date TEXT, end_date TEXT,
            cover_photo TEXT, is_public BOOLEAN DEFAULT 0, share_id TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE stops (
            id INTEGER PRIMARY KEY AUTOINCREMENT, trip_id INTEGER NOT NULL,
            city_name TEXT NOT NULL, arrival_date TEXT, departure_date TEXT,
            num_days INTEGER DEFAULT 2, stop_order INTEGER, hotel_cost REAL DEFAULT 0,
            transport_cost REAL DEFAULT 0, food_cost REAL DEFAULT 0,
            FOREIGN KEY(trip_id) REFERENCES trips(id)
        );
        CREATE TABLE activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT, stop_id INTEGER NOT NULL,
            name TEXT NOT NULL, type TEXT, cost REAL DEFAULT 0,
            duration TEXT, time TEXT, is_selected BOOLEAN DEFAULT 1,
            FOREIGN KEY(stop_id) REFERENCES stops(id)
        );
        CREATE TABLE notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, trip_id INTEGER NOT NULL,
            content TEXT NOT NULL, date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(trip_id) REFERENCES trips(id)
        );
        CREATE TABLE checklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT, trip_id INTEGER NOT NULL,
            item_name TEXT NOT NULL, category TEXT, is_packed BOOLEAN DEFAULT 0,
            FOREIGN KEY(trip_id) REFERENCES trips(id)
        );
    ''')
    conn.commit(); conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized.")
