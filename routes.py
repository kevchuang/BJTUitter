import os
import psycopg2
import time
import static
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

dbName='BJTUTwitter'
dbHost='localhost'
dbPort='5434'

app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='123456',
    USERNAME='postgres',
    PASSWORD='postgre'
))
app.config.from_envvar('FLASKR_SETTTINGS', silent=True)

conn = psycopg2.connect("dbname="+dbName+" user=postgres password=postgre host="+dbHost+" port="+dbPort)
cur = conn.cursor()

@app.route('/list_followers/<user_id>', methods=['GET', 'POST'])
def list_followers(user_id):
    friends = []
    SQL = "SELECT * FROM \"FRIENDS\" WHERE id_followed = %s"
    cur.execute(SQL, (user_id,))
    following = cur.fetchall()
    for follow in following:
        SQL = "SELECT * FROM \"USER\" WHERE user_id = %s"
        cur.execute(SQL, (follow[0],))
        friends.append(cur.fetchone())

    return render_template("list_following.html", friends=friends)

@app.route('/list_following/<user_id>', methods=['GET', 'POST'])
def list_following(user_id):
    friends = []
    SQL = "SELECT * FROM \"FRIENDS\" WHERE user_id = %s"
    cur.execute(SQL, (user_id,))
    following = cur.fetchall()
    for follow in following:
        SQL = "SELECT * FROM \"USER\" WHERE user_id = %s"
        cur.execute(SQL, (follow[1],))
        friends.append(cur.fetchone())

    return render_template("list_following.html", friends=friends)

@app.route('/follow/<id_followed>', methods=['GET', 'POST'])
def follow(id_followed):
    SQL = "SELECT * FROM \"FRIENDS\" WHERE user_id = %s AND id_followed = %s;"
    cur.execute(SQL, (str(session['user_id']), id_followed))
    ret = cur.fetchone()

    if ret == None:
        SQL = "INSERT INTO \"FRIENDS\" (user_id, id_followed) VALUES (%s, %s)"
        cur.execute(SQL, (str(session['user_id']), id_followed))
        SQL = "UPDATE \"USER\" SET nb_follow = nb_follow + 1 WHERE user_id = %s;"
        cur.execute(SQL, (str(session['user_id']),))
    else:
        SQL = "DELETE FROM \"FRIENDS\" WHERE user_id = %s AND id_followed = %s"
        cur.execute(SQL, (str(session['user_id']), id_followed))
        SQL = "UPDATE \"USER\" SET nb_follow = nb_follow - 1 WHERE user_id = %s;"
        cur.execute(SQL, (str(session['user_id']),))
    conn.commit()
    return redirect('profile/' + id_followed)

@app.route('/profile/<user_id>', methods=['GET', 'POST'])
def profile(user_id):
    follow = None

    SQL = "SELECT * from \"USER\" WHERE user_id = %s"
    cur.execute(SQL, (user_id,))
    user = cur.fetchone()
    SQL = "SELECT * FROM \"POSTS\" WHERE user_id = %s"
    cur.execute(SQL, (user_id,))
    posts = cur.fetchall()
    SQL = "SELECT * FROM \"FRIENDS\" WHERE user_id = %s AND id_followed = %s"
    cur.execute(SQL, (str(session['user_id']), user_id))
    ret = cur.fetchone()
    if ret == None:
        follow = "Follow"
    else:
        follow = "Unfollow"

    if str(session['user_id']) == user_id:
        follow = ""

    return render_template('profile.html', user=user, posts=posts, follow=follow, user_id=session['user_id'])

@app.route('/search', methods=['GET', 'POST'])
def search():
    SQL = "SELECT * from \"USER\" WHERE login_username = %s OR mail = %s"
    cur.execute(SQL, (request.form['search-content'].lower().strip(), request.form['search-content'].lower().strip()))
    ret = cur.fetchone()
    if ret != None:
        return redirect('profile/' + str(ret[8]))
    return redirect('feed')

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

    return render_template('login.html', error=error), 403

@app.route('/feed', methods=['GET'])
def feed():
    error = None
    entries = None
    user_id = str(session['user_id'])

    SQL = "SELECT * FROM \"POSTS\" WHERE user_id = %s AND ans_to_post IS NULL"
    cur.execute(SQL, (str(session['user_id']),))
    entries = cur.fetchall()
    SQL = "SELECT * FROM \"FRIENDS\" WHERE user_id = %s"
    cur.execute(SQL, (str(session['user_id']),))
    friends = cur.fetchall()
    for friend in friends:
        SQL = "SELECT * FROM \"POSTS\" WHERE user_id = %s"
        cur.execute(SQL, (friend[1],))
        entries.extend(cur.fetchall())
    return render_template('feed.html', entries=entries, user_id = user_id)


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

    SQL = "SELECT * from \"LIKES\" WHERE user_id = %s AND post_id = %s;"
    cur.execute(SQL, (str(session['user_id']), post_id))
    ret = cur.fetchone()

    if ret == None:
        SQL = "INSERT INTO \"LIKES\" (user_id, post_id) VALUES(%s, %s);"
        cur.execute(SQL,(str(session['user_id']), post_id))
        SQL = "UPDATE \"POSTS\" SET nb_of_likes = nb_of_likes + 1 WHERE post_id = %s;"
        cur.execute(SQL, (post_id,))
    else:
        SQL = "DELETE FROM \"LIKES\" WHERE user_id = %s AND post_id = %s;"
        cur.execute(SQL, (str(session['user_id']), post_id))
        SQL = "UPDATE \"POSTS\" SET nb_of_likes = nb_of_likes - 1 WHERE post_id = %s;"
        cur.execute(SQL, (post_id,))
    conn.commit()
    return redirect('post/' + post_page)

@app.route('/like/<post_id>', methods=['GET', 'POST'])
def like(post_id):
    error = None
    SQL = "SELECT * from \"LIKES\" WHERE user_id = %s AND post_id = %s;"
    cur.execute(SQL, (str(session['user_id']), post_id))
    ret = cur.fetchone()

    if ret == None:
        SQL = "INSERT INTO \"LIKES\" (user_id, post_id) VALUES(%s, %s)"
        cur.execute(SQL, (str(session['user_id']), post_id))
        SQL = "UPDATE \"POSTS\" SET nb_of_likes = nb_of_likes + 1 WHERE post_id = %s;"
        cur.execute(SQL, (post_id,))
    else:
        SQL = "DELETE FROM \"LIKES\" WHERE user_id = %s AND post_id = %s;"
        cur.execute(SQL, (str(session['user_id']), post_id))
        SQL = "UPDATE \"POSTS\" SET nb_of_likes = nb_of_likes - 1 WHERE post_id = %s;"
        cur.execute(SQL, (post_id,))
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
    cur.execute(SQL, (str(session['user_id']),))
    entries = cur.fetchone()
    if request.method == 'POST':
        SQL = "UPDATE \"USER\" SET lastname = %s, firstname = %s, nickname = %s, mail = %s WHERE user_id = %s;"
        cur.execute(SQL, (request.form['lastname'], request.form['firstname'], request.form['nickname'], request.form['mail'].lower().strip(), str(session['user_id'])))
        if request.form['password'] != "":
            cur.execute("UPDATE \"USER\" SET password = crypt(%s, gen_salt('bf', 8)) WHERE user_id = %s;", (request.form['password'], str(session['user_id'])))
        conn.commit()
    return render_template('account.html', entries=entries)

def main():
    app.run()
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()