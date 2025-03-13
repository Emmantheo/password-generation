import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import random
import string
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = "CHANGE_ME_IN_PRODUCTION"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'  # Store sessions on the file system

db = SQLAlchemy(app)

# ----------------------------------------------------
# DATABASE MODEL
# ----------------------------------------------------
class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Integer, default=0)

# Ensure the counter exists in the DB
def get_password_counter():
    counter = Counter.query.filter_by(name='password_count').first()
    if counter is None:
        counter = Counter(name='password_count', value=0)
        db.session.add(counter)
        db.session.commit()
    return counter

# ----------------------------------------------------
# LOGGING SETUP
# ----------------------------------------------------
if not os.path.exists('logs'):
    os.mkdir('logs')

file_handler = RotatingFileHandler('logs/app.log', maxBytes=1000000, backupCount=3)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# ----------------------------------------------------
# ROUTES
# ----------------------------------------------------

@app.route('/')
def home():
    return render_template('index.html'), 200

@app.route('/create_password', methods=['POST'])
def create_password():
    """
    Generates a password based on user-selected options, stores count in DB,
    and saves the password temporarily in session for strength evaluation.
    """
    # Safely parse user input for length
    try:
        length = int(request.form.get('length', 8))
    except ValueError:
        length = 8

    # Build the character set based on checkboxes
    selected_chars = ""
    if request.form.get('use_upper'):
        selected_chars += string.ascii_uppercase  # A-Z
    if request.form.get('use_lower'):
        selected_chars += string.ascii_lowercase  # a-z
    if request.form.get('use_digits'):
        selected_chars += string.digits           # 0-9
    if request.form.get('use_punct'):
        selected_chars += string.punctuation      # !"#$%&'()

    if not selected_chars:
        selected_chars = string.ascii_letters + string.digits

    # Generate the password
    password_list = random.choices(selected_chars, k=length)
    password = ''.join(password_list)

    # Save password in session for strength evaluation
    session['last_generated_password'] = password

    # Increment the counter in the database
    counter = get_password_counter()
    counter.value += 1
    db.session.commit()

    # Log metadata
    app.logger.info(
        "Password created. Length: %d, Char set: %d, Count so far: %d",
        length, len(selected_chars), counter.value
    )

    return jsonify({
        "generated_password": password
    })

@app.route('/suggest_password_strength', methods=['GET'])
def suggest_password_strength():
    """
    Evaluates the strength of the most recently generated password.
    """
    password = session.get('last_generated_password')

    if not password:
        return jsonify({"error": "No recently generated password found."}), 400

    # Strength criteria
    length = len(password)
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_special = any(char in string.punctuation for char in password)

    # Determine strength level
    strength = "Weak"
    if length >= 8 and has_upper and has_lower and has_digit:
        strength = "Moderate"
    if length >= 12 and has_upper and has_lower and has_digit and has_special:
        strength = "Strong"

    return jsonify({
        "generated_password": password,
        "strength": strength
    })

# ----------------------------------------------------
#  DB INIT UTILITY (Optional)
# ----------------------------------------------------
@app.cli.command("init-db")
def init_db():
    """
    Command to initialize (or reset) the database tables.
    Usage: flask init-db
    """
    db.drop_all()
    db.create_all()
    print("Database initialized.")

# ----------------------------------------------------
# LAUNCH
# ----------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.logger.info("Starting Password Generator App (with Strength Suggestion)...")
    app.run(debug=True, host="0.0.0.0", port=5000)
