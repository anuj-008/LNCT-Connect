from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Function to connect to the database
def get_db_connection():
    db_url = os.environ.get("DATABASE_URL")  # Get the database URL from environment variables
    conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    return conn

# Function to create database tables
def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(50) PRIMARY KEY,
            password TEXT NOT NULL,
            email TEXT,
            name TEXT,
            interests TEXT
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def homepage():
    if 'username' in session:
        return render_template('homepage.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()

        # Check user credentials
        cur.execute('SELECT * FROM users WHERE username = %s AND password = %s;', (username, password))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            session['username'] = username
            return redirect(url_for('homepage'))
        return "Invalid credentials! Please try again.", 401

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if the username already exists
        cur.execute('SELECT * FROM users WHERE username = %s;', (username,))
        existing_user = cur.fetchone()

        if existing_user:
            cur.close()
            conn.close()
            return "Username already exists!", 409

        # Insert the new user
        cur.execute('''
            INSERT INTO users (username, password, email, name, interests)
            VALUES (%s, %s, '', '', '');
        ''', (username, password))
        conn.commit()

        cur.close()
        conn.close()

        session['username'] = username
        return redirect(url_for('homepage'))

    return render_template('signup.html')

@app.route('/profile', methods=['POST'])
def save_profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    email = request.form['email']
    name = request.form['name']
    interests = request.form['interests']

    conn = get_db_connection()
    cur = conn.cursor()

    # Update profile details
    cur.execute('''
        UPDATE users
        SET email = %s, name = %s, interests = %s
        WHERE username = %s;
    ''', (email, name, interests, username))
    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for('homepage'))

@app.route('/search', methods=['GET'])
def search_users():
    if 'username' not in session:
        return redirect(url_for('login'))

    query = request.args.get('query', '').lower()
    conn = get_db_connection()
    cur = conn.cursor()

    # Perform a search for users based on username, name, or interests
    cur.execute('''
        SELECT username, name, email, interests
        FROM users
        WHERE LOWER(username) LIKE %s
           OR LOWER(name) LIKE %s
           OR LOWER(interests) LIKE %s;
    ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
    results = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(results)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Create tables if they don't exist
    create_tables()

    # Run the Flask app
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
