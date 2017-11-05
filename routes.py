import os
import psycopg2
import time
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='123456',
    USERNAME='postgres',
    PASSWORD='postgre'
))
app.config.from_envvar('FLASKR_SETTTINGS', silent=True)

conn = psycopg2.connect("dbname=BJTUTwitter user=postgres password=postgre host=192.168.1.106 port=5434")
cur = conn.cursor()

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        SQL = "SELECT * from \"USER\" WHERE login_username = %s AND password = crypt(%s, password);"
        cur.execute(SQL, (request.form['username'].lower().strip(), request.form['password']))
        ret = cur.fetchone()
        if ret == None:
            error = 'Invalid username and/or password'
        else:
            session['logged_in'] = True
            session['user_id'] = ret[8]
            flash('Successfully login')
            return redirect('feed')

    return render_template('login.html', error=error)

@app.route('/feed', methods=['GET'])
def feed():
    error = None
    entries = None
    SQL = "SELECT * FROM \"POSTS\" WHERE user_id = %s"
    cur.execute(SQL, (session['user_id'],))
    entries = cur.fetchall()

    return render_template('feed.html', entries=entries)

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    error = None
    if request.method == 'POST':
        SQL = "INSERT INTO \"POSTS\" (content, date) VALUES(%s, %S);"
        cur.execute(SQL, (request.form['content'], time.strftime("%A %d %B %Y %H:%M:%S")))
        conn.commit()
    return render_template('add_post')

@app.route('/like', methods=['GET', 'POST'])
def likes():
    error = None
    if request.method == 'POST':
        SQL = "INSERT INTO \"LIKES\" (user_id, post_id) VALUES(%s, %s)"
        cur.execute(SQL, (session['user_id'], request.form['post_id']))
        conn.commit()
        SQL = "UPDATE \"POSTS\" "
    return redirect('feed')

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
            error = 'Please specify a gender'
        SQL = "INSERT INTO \"USER\" (lastname, firstname, nickname, gender, mail, login_username, password) VALUES (%s, %s, %s, %s, %s, %s, crypt(%s, gen_salt('bf', 8)))"
        cur.execute(SQL, (request.form['lastname'], request.form['firstname'], request.form['login'].lower().strip(), str(gender), request.form['mail'].lower().strip(), request.form['login'].lower().strip(), request.form['password']))
        conn.commit()
    return render_template('registration.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Successfully logged out')
    session['user_id'] = -1
    return redirect(url_for('login'))

@app.route('/account', methods=['GET', 'POST'])
def account():
    entries = None
    SQL = "SELECT * FROM \"USER\" WHERE user_id = %s;"
    cur.execute(SQL, (str(session['user_id'])))
    entries = cur.fetchone()
    if request.method == 'POST':
        SQL = "UPDATE \"USER\" SET lastname = %s, firstname = %s, nickname = %s, mail = %s WHERE user_id = %s;"
        cur.execute(SQL, (request.form['lastname'], request.form['firstname'], request.form['nickname'], request.form['mail'].lower().strip(), str(session['user_id'])))
        if request.form['password'] != "":
            cur.execute("UPDATE \"USER\" SET password = crypt(%s, gen_salt('bf', 8)) WHERE user_id = %s;", (request.form['password'], str(session['user_id'])))
        conn.commit()
    return render_template('account.html', entries=entries)


@app.route('/main', methods=['GET', 'POST'])
def main():
    return render_template('main.html')


if __name__ == '__main__':
    app.run()
    cur.close()
    conn.close()
