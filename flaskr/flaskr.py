import os
import sys
import sqlite3
import markdown
import tomd
from keys import keys
from datetime import datetime
from slugify import slugify
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, Markup

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(keys)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def format_slug(slug):
    db = get_db()
    slug_extra = 1
    duplicate_slugs = db.execute('select slug from posts where slug == ?', [slug]).fetchall()
    if len(duplicate_slugs) != 0:
        while len(duplicate_slugs) != 0:
            slug_extra += 1
            duplicate_slugs = db.execute('select slug from posts where slug == ?', [slug + '-' + str(slug_extra)]).fetchall()
        return slug + '-' + str(slug_extra)
    return slug

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def show_posts():
    db = get_db()
    cur = db.execute('''select title, slug, text, publish_date from posts
                        where published == 1
                        order by publish_date desc''')
    posts = cur.fetchall()
    return render_template('show_posts.html', posts=posts)

@app.route('/archive')
def archive():
    db = get_db()
    posts = db.execute('''select title, slug, publish_date from posts
                          where published == 1
                          order by publish_date desc''').fetchall()
    return render_template('archive.html', posts=posts, title="archive")

@app.route('/post/<slug>')
def show_post(slug):
    db = get_db()
    cur = db.execute('''select title, slug, text, publish_date from posts
                        where published == 1 and slug == ?''', [slug])
    posts = cur.fetchall()
    if len(posts) > 0:
        post = posts[0]
        return render_template('show_post.html', post=post, title=post[0])
    abort(404)

@app.route('/add', methods=['GET', 'POST'])
def add_post():
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'POST':
        if request.form['title'] is '' or request.form['title'].isspace():
            flash('Title cannot be empty')
            return redirect(url_for('add_post'))
        if request.form['text'] is '' or request.form['text'].isspace():
            flash('Text cannot be empty')
            return redirect(url_for('add_post'))

        db = get_db()

        # render markdown to html
        text = Markup(markdown.markdown(request.form['text']))

        # create slug given title
        title = request.form['title']
        slug = format_slug(slugify(title))

        # set publish status
        published = True if 'published' in request.form else False
        publish_date = str(datetime.now()) if published else "unpublished"

        db.execute('''insert into posts
                      (title, slug, text, published, publish_date)
                      values (?, ?, ?, ?, ?)''',
                   [title, slug, text, published, publish_date])
        db.commit()
        return redirect(url_for('show_posts'))
    return render_template('add.html')

@app.route('/edit/<slug>', methods=['GET', 'POST'])
def edit_post(slug):
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'POST':
        if request.form['title'] is '' or request.form['title'].isspace():
            flash('Title cannot be empty')
            return redirect(url_for('edit_post', slug=slug))
        if request.form['text'] is '' or request.form['text'].isspace():
            flash('Text cannot be empty')
            return redirect(url_for('edit_post', slug=slug))

        db = get_db()
        post = db.execute('select * from posts where slug == ?', [slug]).fetchall()[0]
        title = request.form['title']
        new_slug = slug
        if title != post['title']:
            new_slug = format_slug(slugify(title))
        text = Markup(markdown.markdown(request.form['text'])) 
        # set publish status
        published = True if 'published' in request.form else False
        publish_date = str(datetime.now()) if published else "unpublished" 
        db.execute('''update posts set title = ?, slug = ?, text = ?,
                      published = ?, publish_date = ?
                      where slug == ?''',
                      [title, new_slug, text, published, publish_date, slug])
        db.commit()
        return redirect(url_for('show_posts'))

    db = get_db()
    post = db.execute('select * from posts where slug == ?', [slug]).fetchall()[0]
    # get post from slug
    text = tomd.Tomd(post['text']).markdown
    return render_template('edit.html', post=post, text=text, slug=slug)

@app.route('/delete', methods=['POST'])
def delete():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('delete from posts where id == ?', [request.form['id']])
    db.commit()
    return redirect(url_for('admin'))

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    posts = db.execute('select * from posts order by id desc').fetchall()
    return render_template('admin_menu.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif check_password_hash(app.config['PASSWORD'], request.form['password']) is not True:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            return redirect(url_for('show_posts'))
    if session.get('logged_in'):
        return redirect(url_for('admin'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('show_posts'))

if __name__ == "__main__":
    app.run(host='0.0.0.0')
