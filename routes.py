import os
import psycopg2
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='123456',
    USERNAME='postgres',
    PASSWORD='postgre'
))
app.config.from_envvar('FLASKR_SETTTINGS', silent=True)

conn = psycopg2.connect("dbname=BJTUTwitter user=postgres password=postgre host=localhost port=5434")
cur = conn.cursor()

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        SQL = "SELECT * from \"USER\" WHERE login_username = %s AND password = %s;"
        cur.execute(SQL, (request.form['username'], request.form['password']))
        if cur.fetchone() == None:
            error = 'Invalid username and/or password'
        else:
            session['logged_in'] = True
            flash('Successfully login')
            return redirect('feed')

    return render_template('login.html', error=error)

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    error = None
    gender = -1
    if request.method == 'POST':
        if request.form['gender'] == 'Male':
            gender = 1
        elif request.form['gender'] == 'Female':
            gender = 0
        else:
            error = 'PLease specify a gender'
            return render_template('registration.html')
        SQL = "INSERT INTO \"USER\" (lastname, firstname, gender, mail, login_username, password) VALUES (%s, %s, %s, %s, %s, %s)"
        cur.execute(SQL, (request.form['lastname'], request.form['firstname'], gender, request.form['mail'], request.form['login'], request.form['password']))
        conn.commit()
    return render_template('registration.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Successfully logged out')
    cur.close()
    conn.close()
    return redirect(url_for('login'))

@app.route('account', methods=['GET', 'POST'])
def account():

    return render_template('account.html')
if __name__ == '__main__':
    app.run()