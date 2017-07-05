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

def clean_tags():
    db = get_db()
    tagrows = db.execute('''select id from tags
                         where id not in(select tag_id from tagmap)''').fetchall()
    tag_ids = []
    for tagrow in tagrows:
        tag_ids += [tagrow[0]]
    for tag_id in tag_ids:
        db.execute('''delete from tags where id == ?''', [tag_id])
    db.commit()

@app.route('/')
def show_posts():
    db = get_db()
    posts = db.execute('''select id, title, slug, text, publish_date from posts
                          where published == 1
                          order by publish_date desc''').fetchall()
    tagdict = dict()
    for post in posts:
        tags = db.execute('''select label from tags
                             where id in(
                                select tag_id from tagmap
                                where post_id == ?)''', [post[0]]).fetchall()
        tagdict[post[0]] = []
        for tag in tags:
            tagdict[post[0]] += [tag[0]]
    return render_template('show_posts.html', posts=posts, tagdict=tagdict)

@app.route('/about')
def about():
    return render_template('about.html', title='about')

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
    cur = db.execute('''select id, title, slug, text, publish_date from posts
                        where published == 1 and slug == ?''', [slug])
    posts = cur.fetchall()
    if len(posts) > 0:
        post = posts[0]
        tagrows = db.execute('''select label from tags
                             where id in(
                                select tag_id from tagmap
                                where post_id ==?)''', [post[0]]).fetchall()
        tags = []
        for tagrow in tagrows:
            tags += [tagrow['label']]
        return render_template('show_post.html', post=post, tags=tags, title=post['title'])
    abort(404)

@app.route('/tags')
def tags():
    db = get_db()
    tags = db.execute('''select * from tags order by label asc''').fetchall()
    return render_template('tags.html', tags=tags, title='tags')

@app.route('/tagged/<label>')
def tagged(label):
    db = get_db()
    tag_id = None
    cur = db.execute('''select id from tags where label == ?''', [label]).fetchone()
    if cur:
        tag_id = cur[0]
    if tag_id:
        posts = db.execute('''select * from posts where published == 1
                            and id in(
                                select post_id from tagmap where tag_id == ?)
                            order by publish_date desc''',[tag_id]).fetchall()
        tagdict = dict()
        for post in posts:
            tags = db.execute('''select label from tags
                                where id in(
                                    select tag_id from tagmap
                                    where post_id == ?)''', [post[0]]).fetchall()
            tagdict[post[0]] = []
            for tag in tags:
                tagdict[post[0]] += [tag[0]]
        return render_template('show_posts.html', posts=posts, tagdict=tagdict, tagged=label, title=label)
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

        tags = []
        for key in request.form:
            if key[:4] == "tag_":
                print(True)
                tags += [request.form[key]]

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

        post_id = db.execute('''select id from posts
                                where slug == ?''', [slug]).fetchone()[0]
        for tag in tags:
            db.execute('''insert or ignore into tags (label) values (?)''', [tag])
            db.commit()
            tag_id = db.execute('''select id from tags
                                   where label == ?''', [tag]).fetchone()[0]
            db.execute('''insert or ignore into tagmap
                          (post_id, tag_id)
                          values (?, ?)''', [post_id, tag_id])
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
        
        tags = []
        for key in request.form:
            if key[:4] == "tag_":
                tags += [request.form[key]]

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
        
        db.execute('''delete from tagmap where post_id == ?''', [post[0]])
        db.commit()
        for tag in tags:
            db.execute('''insert or ignore into tags (label) values (?)''', [tag])
            db.commit()
            tag_id = db.execute('''select id from tags
                                   where label == ?''', [tag]).fetchone()[0]
            db.execute('''insert or ignore into tagmap
                          (post_id, tag_id)
                          values (?, ?)''', [post[0], tag_id])
            db.commit()

        clean_tags()
        return redirect(url_for('show_posts'))

    db = get_db()
    post = db.execute('select * from posts where slug == ?', [slug]).fetchall()[0]
    # get post from slug
    text = tomd.Tomd(post['text']).markdown
    tags = db.execute('''select id, label from tags
                            where id in(
                            select tag_id from tagmap
                            where post_id == ?)''', [post[0]]).fetchall()
    return render_template('edit.html', post=post, text=text, slug=slug, tags=tags)

@app.route('/delete', methods=['POST'])
def delete():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('delete from posts where id == ?', [request.form['id']])
    db.execute('''delete from tagmap where post_id == ?''', [request.form['id']])
    db.commit()
    clean_tags()
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
