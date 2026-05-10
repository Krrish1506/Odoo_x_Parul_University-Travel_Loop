"""
app.py — Traveloop Trip Planner Application
Architecture: Flask + SQLAlchemy ORM + Modular Validation + AI Chatbot
Database: MySQL/PostgreSQL ready (SQLite for prototyping)
"""
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, Trip, Stop, Activity, Note, ChecklistItem, SavedPlace, CITIES, CITY_ACTIVITIES, get_city_activities
from validators import (validate_email, validate_password, validate_name,
                         validate_trip_name, validate_date_range,
                         validate_positive_number, validate_num_days, sanitize_string)
from chatbot import get_response as chatbot_response
import uuid

# ── App Factory ───────────────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

# ── Error Handlers ────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, msg="Page not found."), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, msg="Internal server error."), 500

# ── Auth Routes ───────────────────────────────────────────────────────
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = sanitize_string(request.form.get('email', ''))
    password = request.form.get('password', '')

    # Validate inputs
    ok, msg = validate_email(email)
    if not ok:
        flash(msg, 'error'); return redirect(url_for('index'))
    if not password:
        flash('Password is required.', 'error'); return redirect(url_for('index'))

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        session['user_name'] = user.name
        return redirect(url_for('dashboard'))

    flash('Invalid email or password.', 'error')
    return redirect(url_for('index'))

@app.route('/signup', methods=['POST'])
def signup():
    name     = sanitize_string(request.form.get('name', ''))
    email    = sanitize_string(request.form.get('email', ''))
    password = request.form.get('password', '')

    # Validate all fields
    ok, msg = validate_name(name)
    if not ok: flash(msg, 'error'); return redirect(url_for('index'))
    ok, msg = validate_email(email)
    if not ok: flash(msg, 'error'); return redirect(url_for('index'))
    ok, msg = validate_password(password)
    if not ok: flash(msg, 'error'); return redirect(url_for('index'))

    # Check uniqueness
    if User.query.filter_by(email=email).first():
        flash('An account with this email already exists.', 'error')
        return redirect(url_for('index'))

    user = User(name=name, email=email, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    flash('Account created! Please login.', 'success')
    return redirect(url_for('index'))

@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    email = sanitize_string(request.form.get('email', ''))
    ok, msg = validate_email(email)
    if not ok: flash(msg, 'error'); return redirect(url_for('index'))
    flash('If this email is registered, a reset link has been sent.', 'success')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ── Dashboard ─────────────────────────────────────────────────────────
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('index'))
    trips = Trip.query.filter_by(user_id=session['user_id']).order_by(Trip.id.desc()).all()
    trip_budgets = {t.id: t.total_budget for t in trips}
    return render_template('dashboard.html', user_name=session['user_name'],
                           trips=trips, cities=CITIES, trip_budgets=trip_budgets)

# ── Profile ───────────────────────────────────────────────────────────
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session: return redirect(url_for('index'))
    user = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        if request.form.get('action') == 'delete':
            db.session.delete(user)  # cascade deletes everything
            db.session.commit()
            session.clear()
            return redirect(url_for('index'))

        name = sanitize_string(request.form.get('name', ''))
        ok, msg = validate_name(name)
        if not ok: flash(msg, 'error'); return redirect(url_for('profile'))

        user.name = name
        user.language = request.form.get('language', 'English')
        db.session.commit()
        session['user_name'] = name
        flash('Profile updated!', 'success')
        return redirect(url_for('profile'))

    trips_count = Trip.query.filter_by(user_id=user.id).count()
    return render_template('profile.html', user=user, trips_count=trips_count)

# ── Trip CRUD ─────────────────────────────────────────────────────────
@app.route('/create_trip', methods=['GET', 'POST'])
def create_trip():
    if 'user_id' not in session: return redirect(url_for('index'))
    if request.method == 'POST':
        name = sanitize_string(request.form.get('name', ''))
        ok, msg = validate_trip_name(name)
        if not ok: flash(msg, 'error'); return redirect(url_for('create_trip'))

        start = request.form.get('start_date', '')
        end   = request.form.get('end_date', '')
        ok, msg = validate_date_range(start, end)
        if not ok: flash(msg, 'error'); return redirect(url_for('create_trip'))

        cover = sanitize_string(request.form.get('cover_photo', ''), 500) or \
                "https://images.unsplash.com/photo-1488646953014-c8bfbc14a7a0?w=800&q=80"

        trip = Trip(user_id=session['user_id'], name=name,
                    description=sanitize_string(request.form.get('description', ''), 500),
                    start_date=start, end_date=end, cover_photo=cover,
                    share_id=str(uuid.uuid4())[:8])
        db.session.add(trip)
        db.session.commit()
        return redirect(url_for('planner', trip_id=trip.id))
    return render_template('create_trip.html', cities=CITIES)

@app.route('/delete_trip/<int:trip_id>', methods=['POST'])
def delete_trip(trip_id):
    if 'user_id' not in session: return redirect(url_for('index'))
    trip = Trip.query.filter_by(id=trip_id, user_id=session['user_id']).first_or_404()
    db.session.delete(trip)  # cascade
    db.session.commit()
    return redirect(url_for('dashboard'))

# ── Planner (main hub) ───────────────────────────────────────────────
@app.route('/planner/<int:trip_id>')
def planner(trip_id):
    if 'user_id' not in session: return redirect(url_for('index'))
    trip = Trip.query.filter_by(id=trip_id, user_id=session['user_id']).first_or_404()
    activities = Activity.query.filter(
        Activity.stop_id.in_([s.id for s in trip.stops])
    ).all() if trip.stops else []
    
    theme = "holographic"
    for s in trip.stops:
        t = CITIES.get(s.city_name, {}).get("theme")
        if t:
            theme = t
            break

    return render_template('planner.html', trip=trip, stops=trip.stops,
                           activities=activities, notes=trip.notes,
                           checklist=trip.checklist, cities=CITIES, theme=theme)

# ── TravelLoop Wrapped ───────────────────────────────────────────────
@app.route('/wrapped/<int:trip_id>')
def wrapped(trip_id):
    if 'user_id' not in session: return redirect(url_for('index'))
    trip = Trip.query.filter_by(id=trip_id, user_id=session['user_id']).first_or_404()
    activities = Activity.query.filter(
        Activity.stop_id.in_([s.id for s in trip.stops])
    ).all() if trip.stops else []
    
    theme = "holographic"
    for s in trip.stops:
        t = CITIES.get(s.city_name, {}).get("theme")
        if t:
            theme = t
            break
            
    try:
        from datetime import datetime
        start_dt = datetime.strptime(trip.start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(trip.end_date, '%Y-%m-%d')
        total_days = (end_dt - start_dt).days + 1
    except:
        total_days = sum(s.num_days for s in trip.stops) or 1

    return render_template('wrapped.html', trip=trip, stops=trip.stops,
                           activities=activities, theme=theme, total_days=total_days)

# ── Auto-add city with costs + activities ─────────────────────────────
@app.route('/api/add_city', methods=['POST'])
def add_city():
    trip_id   = request.form.get('trip_id', type=int)
    city_name = sanitize_string(request.form.get('city_name', ''))
    num_days  = request.form.get('num_days', 2, type=int)

    if not city_name:
        flash('City name is required.', 'error')
        return redirect(url_for('planner', trip_id=trip_id))

    ok, msg = validate_num_days(num_days)
    if not ok: flash(msg, 'error'); return redirect(url_for('planner', trip_id=trip_id))

    city_data = CITIES.get(city_name, {})
    max_order = db.session.query(db.func.max(Stop.stop_order)).filter_by(trip_id=trip_id).scalar() or 0

    stop = Stop(trip_id=trip_id, city_name=city_name, num_days=num_days,
                stop_order=max_order + 1,
                hotel_cost=city_data.get('hotel_avg', 50),
                transport_cost=city_data.get('transport_avg', 10),
                food_cost=city_data.get('food_avg', 20))
    db.session.add(stop)
    db.session.flush()  # get stop.id

    for act_data in get_city_activities(city_name):
        db.session.add(Activity(stop_id=stop.id, name=act_data['name'],
                                type=act_data['type'], cost=act_data['cost'],
                                duration=act_data['duration'], time=act_data['time']))
    db.session.commit()
    return redirect(url_for('planner', trip_id=trip_id))

@app.route('/api/add_manual_activity', methods=['POST'])
def add_manual_activity():
    name = sanitize_string(request.form.get('name', ''))
    if not name:
        flash('Activity name is required.', 'error')
        return redirect(url_for('planner', trip_id=request.form.get('trip_id')))

    cost = request.form.get('cost', 0)
    ok, msg = validate_positive_number(cost, 'Cost')
    if not ok: flash(msg, 'error'); return redirect(url_for('planner', trip_id=request.form.get('trip_id')))

    db.session.add(Activity(
        stop_id=request.form.get('stop_id', type=int), name=name,
        type=request.form.get('type', 'Custom'), cost=float(cost or 0),
        duration=sanitize_string(request.form.get('duration', '')),
        time=request.form.get('time', '')))
    db.session.commit()
    return redirect(url_for('planner', trip_id=request.form.get('trip_id')))

@app.route('/api/toggle_activity/<int:act_id>', methods=['POST'])
def toggle_activity(act_id):
    act = Activity.query.get_or_404(act_id)
    act.is_selected = not act.is_selected
    db.session.commit()
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/api/update_days/<int:stop_id>', methods=['POST'])
def update_days(stop_id):
    days = request.form.get('num_days', 2)
    ok, msg = validate_num_days(days)
    if not ok: flash(msg, 'error')
    else:
        stop = Stop.query.get_or_404(stop_id)
        stop.num_days = int(days)
        db.session.commit()
    return redirect(url_for('planner', trip_id=request.form.get('trip_id')))

@app.route('/api/remove_stop/<int:stop_id>/<int:trip_id>', methods=['POST'])
def remove_stop(stop_id, trip_id):
    stop = Stop.query.get_or_404(stop_id)
    db.session.delete(stop)  # cascade deletes activities
    db.session.commit()
    return redirect(url_for('planner', trip_id=trip_id))

# ── Notes ─────────────────────────────────────────────────────────────
@app.route('/api/add_note', methods=['POST'])
def add_note():
    content = sanitize_string(request.form.get('content', ''), 2000)
    if not content:
        flash('Note content cannot be empty.', 'error')
        return redirect(url_for('planner', trip_id=request.form.get('trip_id')))
    db.session.add(Note(trip_id=request.form.get('trip_id', type=int), content=content))
    db.session.commit()
    return redirect(url_for('planner', trip_id=request.form.get('trip_id')))

@app.route('/api/delete_note/<int:nid>/<int:tid>', methods=['POST'])
def delete_note(nid, tid):
    db.session.delete(Note.query.get_or_404(nid))
    db.session.commit()
    return redirect(url_for('planner', trip_id=tid))

# ── Checklist ─────────────────────────────────────────────────────────
@app.route('/api/add_checklist', methods=['POST'])
def add_checklist():
    item = sanitize_string(request.form.get('item_name', ''))
    if not item:
        flash('Item name is required.', 'error')
        return redirect(url_for('planner', trip_id=request.form.get('trip_id')))
    db.session.add(ChecklistItem(
        trip_id=request.form.get('trip_id', type=int), item_name=item,
        category=request.form.get('category', 'General')))
    db.session.commit()
    return redirect(url_for('planner', trip_id=request.form.get('trip_id')))

@app.route('/api/toggle_checklist/<int:item_id>', methods=['POST'])
def toggle_checklist(item_id):
    item = ChecklistItem.query.get_or_404(item_id)
    item.is_packed = not item.is_packed
    db.session.commit()
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/api/reset_checklist/<int:tid>', methods=['POST'])
def reset_checklist(tid):
    ChecklistItem.query.filter_by(trip_id=tid).update({'is_packed': False})
    db.session.commit()
    return redirect(url_for('planner', trip_id=tid))

@app.route('/api/delete_checklist/<int:iid>/<int:tid>', methods=['POST'])
def delete_checklist(iid, tid):
    db.session.delete(ChecklistItem.query.get_or_404(iid))
    db.session.commit()
    return redirect(url_for('planner', trip_id=tid))

@app.route('/api/toggle_public/<int:tid>', methods=['POST'])
def toggle_public(tid):
    trip = Trip.query.filter_by(id=tid, user_id=session['user_id']).first_or_404()
    trip.is_public = not trip.is_public
    db.session.commit()
    return redirect(url_for('planner', trip_id=tid))

# ── Shared Itinerary ──────────────────────────────────────────────────
@app.route('/shared/<share_id>')
def shared_itinerary(share_id):
    trip = Trip.query.filter_by(share_id=share_id, is_public=True).first_or_404()
    activities = Activity.query.filter(
        Activity.stop_id.in_([s.id for s in trip.stops]), Activity.is_selected == True
    ).all()
    return render_template('shared_trip.html', trip=trip, stops=trip.stops,
                           activities=activities, cities=CITIES)

# ── AI Chatbot API ────────────────────────────────────────────────────
@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chatbot messages. Returns JSON response."""
    data = request.get_json(silent=True) or {}
    user_msg = sanitize_string(data.get('message', ''), 500)
    response = chatbot_response(user_msg)
    return jsonify({'reply': response})

# ── Explore / City Search + Globe (Phase 13) ─────────────────────────
@app.route('/explore')
def explore():
    if 'user_id' not in session: return redirect(url_for('index'))
    saved = [s.city_name for s in SavedPlace.query.filter_by(user_id=session['user_id']).all()]
    trips = Trip.query.filter_by(user_id=session['user_id']).order_by(Trip.id.desc()).all()
    return render_template('explore.html', cities=CITIES, activities=CITY_ACTIVITIES,
                           saved=saved, trips=trips)

@app.route('/api/destinations')
def search_destinations():
    q = (request.args.get('q', '') or '').strip().lower()
    cat = request.args.get('category', '')
    budget = request.args.get('budget', '')
    results = []
    for name, d in CITIES.items():
        if q and q not in name.lower() and q not in d['country'].lower():
            continue
        if cat and cat != d.get('pop', '').lower():
            continue
        if budget == 'low' and d['daily_budget'] > 70: continue
        if budget == 'mid' and (d['daily_budget'] < 70 or d['daily_budget'] > 150): continue
        if budget == 'high' and d['daily_budget'] < 150: continue
        results.append({**d, 'name': name, 'activities': len(CITY_ACTIVITIES.get(name, []))})
    return jsonify(results)

@app.route('/api/save_place', methods=['POST'])
def save_place():
    if 'user_id' not in session: return jsonify({'error': 'Login required'}), 401
    data = request.get_json(silent=True) or {}
    city = data.get('city', '')
    if not city or city not in CITIES:
        return jsonify({'error': 'Invalid city'}), 400
    existing = SavedPlace.query.filter_by(user_id=session['user_id'], city_name=city).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'saved': False, 'msg': f'{city} removed from wishlist'})
    db.session.add(SavedPlace(user_id=session['user_id'], city_name=city))
    db.session.commit()
    return jsonify({'saved': True, 'msg': f'{city} added to wishlist ❤️'})

@app.route('/admin')
def admin():
    if 'user_id' not in session: return redirect(url_for('index'))
    users = User.query.all()
    trips = Trip.query.order_by(Trip.id.desc()).limit(20).all()
    top_cities = db.session.query(Stop.city_name, db.func.count(Stop.id).label('cnt'))\
        .group_by(Stop.city_name).order_by(db.text('cnt DESC')).limit(6).all()
    return render_template('admin.html',
                           total_users=User.query.count(),
                           total_trips=Trip.query.count(),
                           total_acts=Activity.query.filter_by(is_selected=True).count(),
                           users=users, trips=trips, top_cities=top_cities)

# ── Run ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, port=5000)
