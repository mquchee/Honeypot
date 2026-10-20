import sqlite3
from flask import Flask, render_template, request, redirect, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'meow'

@app.route('/')
def start():
    return render_template('start_page.html')

def init_db():
    conn = sqlite3.connect('honeypot.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS posts (username TEXT, message TEXT, date_time TEXT)')
    conn.commit()
    conn.close()

@app.route('/main_page', methods=['GET','POST'])
def main():
    if 'username' not in session:
        return redirect('/login')

    conn = sqlite3.connect('honeypot.db')

    if request.method == 'POST':
        message = request.form["message"]

        now = datetime.now().strftime('%d-%m-%Y %H:%M')
        conn.execute( 'INSERT INTO posts VALUES ( ?, ?, ? )',
                      (session['username'], message, now))
        conn.commit()

    posts = conn.execute('SELECT * FROM posts ORDER BY rowid DESC').fetchall()
    conn.close()

    return render_template('main_page.html', posts = posts, username = session['username'])

@app.route('/login_page', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('honeypot.db')
        query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password +"'"
        print(query)
        user = conn.execute(query).fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect('/main_page')
        else:
            return render_template('login_page.html', oops_2 ='Wrong username or password, try again!')
    return render_template('login_page.html')

@app.route('/signup_page', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("honeypot.db")
        try:
            conn.execute("INSERT INTO users VALUES (?, ?)", (username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('signup_page.html', oops ='That username is already taken!')
        conn.close()

        return redirect('/login_page')

    return render_template('signup_page.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login_page')

if __name__ == '__main__':
    init_db()
    app.run(port=5001, debug=True)
