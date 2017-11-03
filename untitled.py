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

    #cur.execute("INSERT INTO \"USER\" (lastname, firstname, nickname, gender, age, mail, login_username, password, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
    #            ("Louis", "Chaumier", "Chaumichau", 1, 22, "louischaumier@yahoo.fr", "lolilol", "ezpz", 0))
    #conn.commit()
    if request.method == 'POST':
        SQL = "SELECT * from \"USER\" WHERE login_username = %s;"
        if cur.execute("SELECT * from \"USER\" WHERE login_username = %s;", (request.form['username'])) == None:
            error = 'Invalid username'
        elif cur.execute("SELECT * from \"USER\" WHERE password = %s;", (request.form['password'])) == None:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('Successfully login')
            return redirect('feed')
    cur.close()
    conn.close()
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Successfully logged out')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()