import os
import logging
import uuid
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from llama_client import get_ai_response
from supabase import create_client

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

if supabase:
    logger.info("Supabase client initialized successfully")
else:
    logger.warning("Supabase client not initialized, missing SUPABASE_URL or SUPABASE_KEY")

# Create database base class
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the Base class
db = SQLAlchemy(model_class=Base)

# Create Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database with Supabase PostgreSQL connection
database_url = os.environ.get("DATABASE_URL", "postgresql://postgres:lokesh7345@db.qjlveevoebvgxfzmsbzj.supabase.co:5432/postgres")

# Handle any bracket characters in the URL (if provided as template)
if "[" in database_url and "]" in database_url:
    database_url = database_url.replace("[", "").replace("]", "")

# Handle potential "postgres://" vs "postgresql://" prefix issue
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
logger.info("Using PostgreSQL database")

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize app with SQLAlchemy
db.init_app(app)
CORS(app)

# Store chat history in memory - no longer persisting chats to database
chat_sessions = {}

# Import models after db initialization
with app.app_context():
    from models import User
    db.create_all()

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
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
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.name  # Store user's name instead of user_id
            flash('Login successful!', 'success')
            return redirect(url_for('chat'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('active_chat_id', None)
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
            flash('Please provide name, email and password.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
            
        existing_email = User.query.filter_by(email=email).first()
        
        if existing_email:
            flash('Email already exists. Please use another email or log in.', 'error')
        else:
            hashed_password = generate_password_hash(password)
            new_user = User()
            new_user.name = name
            new_user.email = email
            new_user.password = hashed_password
            db.session.add(new_user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/chat')
def chat():
    if 'user_id' not in session:
        flash('Please log in to access the chat.', 'error')
        return redirect(url_for('login'))
    
    # If user doesn't have an active chat session, create one
    if 'active_chat_id' not in session:
        session['active_chat_id'] = str(uuid.uuid4())
    
    # Initialize chat session if it doesn't exist
    if session['active_chat_id'] not in chat_sessions:
        chat_sessions[session['active_chat_id']] = []
    
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get active chat ID or create a new one
    if 'active_chat_id' not in session:
        session['active_chat_id'] = str(uuid.uuid4())
    
    chat_id = session['active_chat_id']
    
    # Get current chat session or create new one
    if chat_id not in chat_sessions:
        chat_sessions[chat_id] = []
    
    # Get message from request
    data = request.json or {}
    message = data.get('message', '')
    
    # Add user message to session
    message_id = str(uuid.uuid4())
    user_message = {
        'id': message_id,
        'content': message,
        'is_user': True,
        'timestamp': None  # Will be added by the client
    }
    
    chat_sessions[chat_id].append(user_message)
    
    # Format history for the AI
    formatted_history = []
    for msg in chat_sessions[chat_id]:
        role = "user" if msg.get("is_user", True) else "assistant"
        formatted_history.append({"role": role, "content": msg["content"]})
    
    # Get AI response
    ai_response = get_ai_response(formatted_history)
    
    # Add AI response to session
    ai_message_id = str(uuid.uuid4())
    ai_message = {
        'id': ai_message_id,
        'content': ai_response,
        'is_user': False,
        'timestamp': None  # Will be added by the client
    }
    
    chat_sessions[chat_id].append(ai_message)
    
    return jsonify({
        'response': ai_response,
        'message_id': ai_message_id
    })

@app.route('/api/chat_history', methods=['GET'])
def get_chat_history():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # If user doesn't have an active chat session, return empty list
    if 'active_chat_id' not in session:
        return jsonify([])
    
    chat_id = session['active_chat_id']
    
    # If chat session doesn't exist, return empty list
    if chat_id not in chat_sessions:
        return jsonify([])
    
    return jsonify(chat_sessions[chat_id])

@app.route('/api/new_chat', methods=['POST'])
def new_chat():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Create new chat ID
    new_chat_id = str(uuid.uuid4())
    session['active_chat_id'] = new_chat_id
    
    # Initialize new chat session
    chat_sessions[new_chat_id] = []
    
    return jsonify({'success': True, 'session_id': new_chat_id})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
