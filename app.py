from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Rule, Attribute, WeatherSummary, WeatherAlert
from sqlalchemy import desc
from rule_engine import create_rule, combine_rules, evaluate_rule, modify_rule
from weather_monitor import WeatherMonitor
import logging
import os

app = Flask(__name__, static_folder=os.path.abspath('static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rule_engine.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

logging.basicConfig(level=logging.DEBUG)

@app.before_first_request
def create_tables():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/create_rule', methods=['POST'])
@login_required
def create_rule_route():
    rule_name = request.form['rule_name']
    rule_string = request.form['rule_string']
    rule = create_rule(rule_name, rule_string)
    if rule:
        flash(f'Rule "{rule_name}" created successfully!')
    else:
        flash(f'Failed to create rule "{rule_name}".')
    return redirect(url_for('home'))

@app.route('/combine_rules', methods=['POST'])
@login_required
def combine_rules_route():
    rule_names = request.form.getlist('rule_names')
    combined_rule_name = request.form['combined_rule_name']
    combined_rule = combine_rules(combined_rule_name, rule_names)
    if combined_rule:
        flash(f'Combined rule "{combined_rule_name}" created successfully!')
    else:
        flash(f'Failed to create combined rule "{combined_rule_name}".')
    return redirect(url_for('home'))

@app.route('/evaluate_rule', methods=['POST'])
@login_required
def evaluate_rule_route():
    rule_name = request.form['rule_name']
    attributes = request.form.to_dict(flat=True)
    result = evaluate_rule(rule_name, attributes)
    return jsonify({"result": result})

@app.route('/modify_rule', methods=['POST'])
@login_required
def modify_rule_route():
    rule_name = request.form['rule_name']
    new_rule_string = request.form['new_rule_string']
    modify_rule(rule_name, new_rule_string)
    flash(f'Rule "{rule_name}" modified successfully!')
    return redirect(url_for('home'))

@app.route('/weather_alerts')
@login_required
def weather_alerts():
    alerts = WeatherAlert.query.order_by(desc(WeatherAlert.timestamp)).all()
    return render_template('weather_alerts.html', alerts=alerts)

@app.route('/weather_summary/<city>')
@login_required
def weather_summary(city):
    days = request.args.get('days', default=7, type=int)
    monitor = WeatherMonitor(api_key=os.getenv('WEATHER_API_KEY'), cities=[city])
    image_base64 = monitor.generate_temperature_chart(city, days)
    return render_template('weather_summary.html', city=city, image_base64=image_base64)

# Initialize the weather monitor and start it in a separate thread
if __name__ == '__main__':
    monitor = WeatherMonitor(api_key=os.getenv('WEATHER_API_KEY'), cities=["New York", "London", "Paris"])
    # You can set different thresholds for alerts as needed
    thresholds = [
        {"type": "temperature", "value": 35},  # Alert if temperature exceeds 35°C
        {"type": "condition", "value": "Rain"}  # Alert if the weather condition is Rain
    ]
    import threading
    monitor_thread = threading.Thread(target=monitor.run, args=(thresholds,))
    monitor_thread.daemon = True  # Daemonize thread to exit when the main program exits
    monitor_thread.start()

    app.run(debug=True)
