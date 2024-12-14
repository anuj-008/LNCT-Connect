from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os


app = Flask(__name__)
app.secret_key = 'your_secret_key'
port = int(os.environ.get("PORT", 5000))  # Default to 5000 if PORT isn't set
app.run(host='0.0.0.0', port=port)
# Function to load user data
def load_users():
    if not os.path.exists('users.json'):
        with open('users.json', 'w') as file:
            json.dump({}, file)
    with open('users.json', 'r') as file:
        return json.load(file)

# Function to save user data
def save_users(users):
    with open('users.json', 'w') as file:
        json.dump(users, file, indent=4)

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
        users = load_users()

        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('homepage'))
        return "Invalid credentials! Please try again.", 401
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()

        if username in users:
            return "Username already exists!", 409

        users[username] = {
            'password': password,
            'email': '',
            'name': '',
            'interests': ''
        }
        save_users(users)
        session['username'] = username
        return redirect(url_for('homepage'))

    return render_template('signup.html')

@app.route('/profile', methods=['POST'])
def save_profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    users = load_users()

    if username in users:
        # Update profile fields
        users[username]['name'] = request.form['name']
        users[username]['email'] = request.form['email']
        users[username]['interests'] = request.form['interests']

        # Save updated data
        save_users(users)
        return redirect(url_for('homepage'))

    return "User not found!", 404

@app.route('/search', methods=['GET'])
def search_users():
    if 'username' not in session:
        return redirect(url_for('login'))

    query = request.args.get('query', '').lower()
    users = load_users()
    results = []

    for username, data in users.items():
        if query in username.lower() or query in data.get('name', '').lower() or query in data.get('interests', '').lower():
            results.append({
                'username': username,
                'name': data.get('name', ''),
                'email': data.get('email', ''),
                'interests': data.get('interests', '')
            })

    return jsonify(results)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
