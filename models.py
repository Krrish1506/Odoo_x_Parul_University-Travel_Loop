"""
models.py — SQLAlchemy ORM models for Traveloop.
Designed for MySQL/PostgreSQL compatibility. Works with SQLite for prototyping.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

# ── CITY & ACTIVITY DATA (static JSON for rapid prototyping) ──────────
# In production, these would be database tables populated via admin panel.

CITIES = {
    "Paris":      {"country":"France","lat":48.8566,"lng":2.3522,"daily_budget":150,"hotel_avg":120,"transport_avg":15,"food_avg":45,
                   "img":"https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=600&q=80","pop":"Iconic","cost_index":"$$$","desc":"The City of Light. Art, fashion, gastronomy.","theme":"northern"},
    "Tokyo":      {"country":"Japan","lat":35.6762,"lng":139.6503,"daily_budget":130,"hotel_avg":100,"transport_avg":12,"food_avg":35,
                   "img":"https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=600&q=80","pop":"Trending","cost_index":"$$$","desc":"Ultra-modern meets traditional Japanese culture.","theme":"northern"},
    "Bali":       {"country":"Indonesia","lat":-8.3405,"lng":115.092,"daily_budget":50,"hotel_avg":30,"transport_avg":8,"food_avg":12,
                   "img":"https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=600&q=80","pop":"Top Rated","cost_index":"$","desc":"Tropical paradise with temples and rice terraces.","theme":"tropical"},
    "New York":   {"country":"USA","lat":40.7128,"lng":-74.006,"daily_budget":200,"hotel_avg":180,"transport_avg":20,"food_avg":50,
                   "img":"https://images.unsplash.com/photo-1534430480872-3498386e7856?w=600&q=80","pop":"Always Buzzing","cost_index":"$$$$","desc":"The city that never sleeps. Broadway, food, culture.","theme":"northern"},
    "Santorini":  {"country":"Greece","lat":36.3932,"lng":25.4615,"daily_budget":140,"hotel_avg":110,"transport_avg":10,"food_avg":40,
                   "img":"https://images.unsplash.com/photo-1613395877344-13d4a8e0d49e?w=600&q=80","pop":"Romantic","cost_index":"$$$","desc":"White-washed cliffs, sunsets, and Aegean Sea views.","theme":"tropical"},
    "Kyoto":      {"country":"Japan","lat":35.0116,"lng":135.7681,"daily_budget":110,"hotel_avg":80,"transport_avg":10,"food_avg":30,
                   "img":"https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=600&q=80","pop":"Cultural","cost_index":"$$","desc":"Ancient temples, bamboo groves, and geisha culture.","theme":"northern"},
    "Cape Town":  {"country":"South Africa","lat":-33.9249,"lng":18.4241,"daily_budget":70,"hotel_avg":50,"transport_avg":10,"food_avg":20,
                   "img":"https://images.unsplash.com/photo-1580060839134-75a5edca2e99?w=600&q=80","pop":"Hidden Gem","cost_index":"$$","desc":"Table Mountain, penguins, and incredible wine country.","theme":"tropical"},
    "Marrakech":  {"country":"Morocco","lat":31.6295,"lng":-7.9811,"daily_budget":45,"hotel_avg":25,"transport_avg":5,"food_avg":10,
                   "img":"https://images.unsplash.com/photo-1597212618440-806262de4f6b?w=600&q=80","pop":"Exotic","cost_index":"$","desc":"Vibrant souks, spices, and desert adventures.","theme":"desert"},
    "London":     {"country":"UK","lat":51.5074,"lng":-0.1278,"daily_budget":180,"hotel_avg":150,"transport_avg":18,"food_avg":45,
                   "img":"https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=600&q=80","pop":"Classic","cost_index":"$$$$","desc":"Royal palaces, world-class museums, and theatre.","theme":"northern"},
    "Dubai":      {"country":"UAE","lat":25.2048,"lng":55.2708,"daily_budget":160,"hotel_avg":130,"transport_avg":15,"food_avg":40,
                   "img":"https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=600&q=80","pop":"Luxury","cost_index":"$$$$","desc":"Futuristic skyline, desert safaris, and luxury shopping.","theme":"desert"},
    "Bangkok":    {"country":"Thailand","lat":13.7563,"lng":100.5018,"daily_budget":40,"hotel_avg":20,"transport_avg":5,"food_avg":10,
                   "img":"https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=600&q=80","pop":"Budget Friendly","cost_index":"$","desc":"Street food capital, golden temples, and nightlife.","theme":"tropical"},
    "Rome":       {"country":"Italy","lat":41.9028,"lng":12.4964,"daily_budget":130,"hotel_avg":100,"transport_avg":12,"food_avg":35,
                   "img":"https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=600&q=80","pop":"Historic","cost_index":"$$$","desc":"Eternal City. Colosseum, Vatican, and pasta.","theme":"desert"},
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

def get_city_activities(city_name):
    """Return activity list for a city, empty list if unknown."""
    return CITY_ACTIVITIES.get(city_name, [])


# ── ORM MODELS ────────────────────────────────────────────────────────

class User(db.Model):
    """User account with authentication and preferences."""
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    language      = db.Column(db.String(30), default='English')
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    trips = db.relationship('Trip', backref='owner', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.name}>'


class Trip(db.Model):
    """A travel plan with metadata and sharing capability."""
    __tablename__ = 'trips'

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name        = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    start_date  = db.Column(db.String(20))
    end_date    = db.Column(db.String(20))
    cover_photo = db.Column(db.String(500), default='')
    is_public   = db.Column(db.Boolean, default=False)
    share_id    = db.Column(db.String(10), unique=True, index=True)
    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    stops     = db.relationship('Stop', backref='trip', lazy=True, cascade='all, delete-orphan',
                                order_by='Stop.stop_order')
    notes     = db.relationship('Note', backref='trip', lazy=True, cascade='all, delete-orphan',
                                order_by='Note.date_added.desc()')
    checklist = db.relationship('ChecklistItem', backref='trip', lazy=True, cascade='all, delete-orphan',
                                order_by='ChecklistItem.category')

    @property
    def total_budget(self):
        """Calculate total estimated budget across all stops and selected activities."""
        total = 0.0
        for stop in self.stops:
            total += (stop.hotel_cost or 0) * (stop.num_days or 0)
            total += (stop.food_cost or 0) * (stop.num_days or 0)
            total += (stop.transport_cost or 0)
            for act in stop.activities:
                if act.is_selected:
                    total += act.cost or 0
        return total


class Stop(db.Model):
    """A city/destination within a trip with auto-calculated daily costs."""
    __tablename__ = 'stops'

    id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trip_id        = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False, index=True)
    city_name      = db.Column(db.String(100), nullable=False)
    num_days       = db.Column(db.Integer, default=2)
    stop_order     = db.Column(db.Integer, default=1)
    hotel_cost     = db.Column(db.Float, default=0)
    transport_cost = db.Column(db.Float, default=0)
    food_cost      = db.Column(db.Float, default=0)

    # Relationships
    activities = db.relationship('Activity', backref='stop', lazy=True, cascade='all, delete-orphan')


class Activity(db.Model):
    """An activity within a stop — can be auto-suggested or manually added."""
    __tablename__ = 'activities'

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stop_id     = db.Column(db.Integer, db.ForeignKey('stops.id'), nullable=False, index=True)
    name        = db.Column(db.String(200), nullable=False)
    type        = db.Column(db.String(50), default='General')
    cost        = db.Column(db.Float, default=0)
    duration    = db.Column(db.String(20), default='')
    time        = db.Column(db.String(10), default='')
    is_selected = db.Column(db.Boolean, default=True)


class Note(db.Model):
    """A journal note attached to a trip."""
    __tablename__ = 'notes'

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trip_id    = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False, index=True)
    content    = db.Column(db.Text, nullable=False)
    date_added = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class ChecklistItem(db.Model):
    """A packing checklist item, categorized."""
    __tablename__ = 'checklist'

    id        = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trip_id   = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False, index=True)
    item_name = db.Column(db.String(200), nullable=False)
    category  = db.Column(db.String(50), default='General')
    is_packed = db.Column(db.Boolean, default=False)


class SavedPlace(db.Model):
    """A wishlisted/saved destination."""
    __tablename__ = 'saved_places'

    id        = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    city_name = db.Column(db.String(100), nullable=False)
    saved_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint('user_id', 'city_name'),)
