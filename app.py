import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_cors import CORS
import uuid 
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from llama_client import get_ai_response  # Make sure you have the llama_client module set up
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

if supabase:
    logger.info("Supabase client initialized successfully")
else:
    logger.warning("Supabase client not initialized")

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv("SESSION_SECRET")  # This should be a strong secret key
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
CORS(app)

# In-memory chat sessions
chat_sessions = {}

# Routes
@app.route('/')
def index():
    if 'email' in session:
        return redirect(url_for('chat'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please provide both email and password.', 'error')
            return render_template('login.html')

        result = supabase.table("users").select("*").eq("email", email).single().execute()
        user = result.data if result.data else None

        if user and check_password_hash(user['password'], password):
            session['email'] = user['email']
            session['username'] = user['name']
            flash('Login successful!', 'success')
            return redirect(url_for('chat'))
        else:
            flash('Invalid credentials. Please try again.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not name or not email or not password:
            flash('Please provide name, email, and password.', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        existing_user = supabase.table("users").select("*").eq("email", email).execute()
        if existing_user.data:
            flash('Email already exists. Please use another email or log in.', 'error')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)
        response = supabase.table("users").insert({
            "name": name,
            "email": email,
            "password": hashed_password
        }).execute()

        if response.data:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed. Try again later.', 'error')

    return render_template('register.html')

@app.route('/chat')
def chat():
    if 'email' not in session:
        flash('Please log in to access the chat.', 'error')
        return redirect(url_for('login'))

    if 'active_chat_id' not in session:
        session['active_chat_id'] = str(uuid.uuid4())

    if session['active_chat_id'] not in chat_sessions:
        chat_sessions[session['active_chat_id']] = []

    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    if 'email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    if 'active_chat_id' not in session:
        session['active_chat_id'] = str(uuid.uuid4())

    chat_id = session['active_chat_id']

    if chat_id not in chat_sessions:
        chat_sessions[chat_id] = []

    data = request.json or {}
    message = data.get('message', '')

    message_id = str(uuid.uuid4())
    user_message = {
        'id': message_id,
        'content': message,
        'is_user': True,
        'timestamp': None
    }

    chat_sessions[chat_id].append(user_message)

    formatted_history = [
        {"role": "user" if m["is_user"] else "assistant", "content": m["content"]}
        for m in chat_sessions[chat_id]
    ]

    ai_response = get_ai_response(formatted_history)

    ai_message_id = str(uuid.uuid4())
    ai_message = {
        'id': ai_message_id,
        'content': ai_response,
        'is_user': False,
        'timestamp': None
    }

    chat_sessions[chat_id].append(ai_message)

    return jsonify({
        'response': ai_response,
        'message_id': ai_message_id
    })

@app.route('/api/chat_history', methods=['GET'])
def get_chat_history():
    if 'email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    chat_id = session.get('active_chat_id', '')
    return jsonify(chat_sessions.get(chat_id, []))

@app.route('/api/new_chat', methods=['POST'])
def new_chat():
    if 'email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    new_chat_id = str(uuid.uuid4())
    session['active_chat_id'] = new_chat_id
    chat_sessions[new_chat_id] = []

    return jsonify({'success': True, 'session_id': new_chat_id})

if __name__ == '__main__':
    # Ensure the app runs with Gunicorn if deployed (recommended for production)
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)), debug=True)
