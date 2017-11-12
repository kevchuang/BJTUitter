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

conn = psycopg2.connect("dbname=BJTUTwitter user=postgres password=postgre host=192.168.1.104 port=5434")
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

    SQL = "SELECT * FROM \"POSTS\" WHERE user_id = %s AND ans_to_post IS NULL" % str(session['user_id'])
    cur.execute(SQL)
    entries = cur.fetchall()

    return render_template('feed.html', entries=entries)


@app.route('/post/<post_id>', methods=['GET', 'POST'])
def post(post_id):
    error = None
    entries = None
    comments = None

    SQL = "SELECT * FROM \"POSTS\" WHERE post_id = %s" % post_id
    cur.execute(SQL)
    entries = cur.fetchall()
    SQL = "SELECT * FROM \"POSTS\" WHERE ans_to_post = %s" % post_id
    cur.execute(SQL)
    comments = cur.fetchall()
    return render_template('post.html', entries=entries, comments=comments)

# @app.route('/like', methods=['GET', 'POST'])
# def like():
#
#     SQL = "INSERT INTO \"LIKES\" (user_id, post_id) VALUES (%s, %s);"
#     return redirect(like)

@app.route('/delete/<post_id>', methods=['GET', 'POST'])
def delete(post_id):
    error = None
    post = None
    SQL = "SELECT * FROM \"POSTS\" WHERE user_id = %s AND post_id = %s AND ans_to_post IS NULL"
    cur.execute(SQL, (str(session['user_id']), post_id))
    post = cur.fetchone()

    SQL = "DELETE FROM \"POSTS\" WHERE user_id = %s AND post_id = %s" % (str(session['user_id']), post_id)
    cur.execute(SQL)
    if post != None:
        SQL = "SELECT * FROM \"POSTS\" WHERE ans_to_post = %s" % post_id
        cur.execute(SQL)
        comments = cur.fetchall()
        for comment in comments:
            SQL = "DELETE FROM \"POSTS\" WHERE post_id = %s" % str(comment[0])
            cur.execute(SQL)
    conn.commit()
    return redirect('feed')

@app.route('/edit?post_page=<post_page>&post_edit=<post_edit>', methods=['GET', 'POST'])
def edit(post_page, post_edit):
    error = None
    if request.method == 'POST':
        SQL = "UPDATE \"POSTS\" SET content = %s WHERE post_id = %s;"
        cur.execute(SQL, (request.form['editPostText'], post_edit))
        conn.commit()
    return redirect('post/' + post_page)

@app.route('/add_comment?post_id=<post_id>', methods=['GET', 'POST'])
def add_comment(post_id):
    error = None
    if request.method == 'POST':
        SQL = "INSERT INTO \"POSTS\" (content, date, ans_to_post, user_id) VALUES(%s, %s, %s, %s);"
        cur.execute(SQL, (request.form['comment'], time.strftime("%A %d %B %Y %H:%M:%S"), post_id, str(session['user_id'])))
        conn.commit()
    return redirect('post/' + post_id)

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    error = None
    if request.method == 'POST':
        SQL = "INSERT INTO \"POSTS\" (content, date, user_id) VALUES(%s, %s, %s);"
        cur.execute(SQL, (request.form['post-content'], time.strftime("%A %d %B %Y %H:%M:%S"), str(session['user_id'])))
        conn.commit()
    return redirect('feed')

@app.route('/like_post/<post_page>/<post_id>')
def like_post(post_page, post_id):
    error = None

    SQL = "SELECT * from \"LIKES\" WHERE user_id = %s AND post_id = %s;" % (str(session['user_id']), post_id)
    cur.execute(SQL)
    ret = cur.fetchone()

    if ret == None:
        SQL = "INSERT INTO \"LIKES\" (user_id, post_id) VALUES(%s, %s);" % (str(session['user_id']), post_id)
        cur.execute(SQL)
        SQL = "UPDATE \"POSTS\" SET nb_of_likes = nb_of_likes + 1 WHERE post_id = %s;" % post_id
        cur.execute(SQL)
    else:
        SQL = "DELETE FROM \"LIKES\" WHERE user_id = %s AND post_id = %s;" % (str(session['user_id']), post_id)
        cur.execute(SQL)
        SQL = "UPDATE \"POSTS\" SET nb_of_likes = nb_of_likes - 1 WHERE post_id = %s;" % post_id
        cur.execute(SQL)
    conn.commit()
    return redirect('post/' + post_page)

@app.route('/like/<post_id>', methods=['GET', 'POST'])
def like(post_id):
    error = None
    SQL = "SELECT * from \"LIKES\" WHERE user_id = %s AND post_id = %s;" % (str(session['user_id']), post_id)
    cur.execute(SQL)
    ret = cur.fetchone()

    if ret == None:
        SQL = "INSERT INTO \"LIKES\" (user_id, post_id) VALUES(%s, %s)" % (str(session['user_id']), post_id)
        cur.execute(SQL)
        SQL = "UPDATE \"POSTS\" SET nb_of_likes = nb_of_likes + 1 WHERE post_id = %s;" % post_id
        cur.execute(SQL)
    else:
        SQL = "DELETE FROM \"LIKES\" WHERE user_id = %s AND post_id = %s;" % (str(session['user_id']), post_id)
        cur.execute(SQL)
        SQL = "UPDATE \"POSTS\" SET nb_of_likes = nb_of_likes - 1 WHERE post_id = %s;" % post_id
        cur.execute(SQL)
    conn.commit()
    return redirect('feed')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    error = None
    gender = -1
    if request.method == 'POST':
        if request.form['gender'] == 'male':
            gender = 1
        elif request.form['gender'] == 'female':
            gender = 0
        else:
            error = 'Please specify a gender'
            return render_template('registration.html')
        SQL = "INSERT INTO \"USER\" (lastname, firstname, nickname, gender, mail, login_username, password) VALUES (%s, %s, %s, %s, %s, %s, crypt(%s, gen_salt('bf', 8)))"
        cur.execute(SQL, (request.form['lastname'], request.form['firstname'], request.form['login'].lower().strip(), str(gender), request.form['mail'].lower().strip(), request.form['login'].lower().strip(), request.form['password']))
        conn.commit()
        return redirect('login')
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
