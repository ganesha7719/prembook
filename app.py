import os
import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for

try:
    import psycopg2
except ImportError:
    psycopg2 = None

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')

# Get the directory where the app is running
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'users.db')
DATABASE_URL = os.environ.get('DATABASE_URL')


def use_postgres():
    return DATABASE_URL is not None and psycopg2 is not None


def get_connection():
    if use_postgres():
        db_url = DATABASE_URL
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        return psycopg2.connect(db_url, sslmode='require')
    return sqlite3.connect(DB_PATH)


# Initialize database

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS userlogin 
                      (name TEXT, userid TEXT PRIMARY KEY, pin TEXT)''')
    conn.commit()
    cursor.close()
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
        conn = get_connection()
        cursor = conn.cursor()
        if use_postgres():
            cursor.execute("INSERT INTO userlogin VALUES (%s, %s, %s)", (name, userid, pin))
        else:
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

    conn = get_connection()
    cursor = conn.cursor()
    if use_postgres():
        cursor.execute("SELECT name FROM userlogin WHERE userid = %s AND pin = %s", (userid, pin))
    else:
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

@app.route('/admin')
def admin():
    if 'admin' in session:
        return redirect(url_for('admin_users'))
    return render_template('admin.html')

@app.route('/admin', methods=['POST'])
def admin_login():
    username = request.form['username']
    password = request.form['password']
    if username == 'ganesh' and password == 'jaihind':
        session['admin'] = True
        return redirect(url_for('admin_users'))
    else:
        return "Invalid credentials! <a href='/admin'>Try Again</a>"

@app.route('/admin/users')
def admin_users():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, userid, pin FROM userlogin")
    users = cursor.fetchall()
    conn.close()
    return render_template('admin_users.html', users=users)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return "Admin Logout successful! <a href='/admin'>Login again</a>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
