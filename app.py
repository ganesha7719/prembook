import os
import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')

# Get the directory where the app is running
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'users.db')

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS userlogin 
                      (name TEXT, userid TEXT PRIMARY KEY, pin TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['nm']
    userid = request.form['uid']
    pin = request.form['upin']

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO userlogin VALUES (?, ?, ?)", (name, userid, pin))
        conn.commit()
        cursor.close()
        conn.close()
        return "Sign Up यशस्वी झाले! <a href='/login'>Login करा</a>"

    except Exception as e:
        return f"UserID already exists! Error: {str(e)}"

@app.route('/login', methods=['POST'])
def login():
    userid = request.form['uid']
    pin = request.form['upin']

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM userlogin WHERE userid = ? AND pin = ?", (userid, pin))
    result = cursor.fetchone()
    conn.close()

    if result:
        session['user'] = result[0]
        return render_template('main.html', name=result[0])
    else:
        return "Invalid UserID or PIN! <a href='/login'>Try Again</a>"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return "Logout successful! <a href='/login'>Login again</a>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
