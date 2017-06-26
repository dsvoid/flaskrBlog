# flaskrBlog
My custom additions to the Flaskr tutorial for Python's Flask web framework.

## Overview

[Flask](http://flask.pocoo.org/) is a neat and minimal web framework for Python. Like every web framework, the first thing you should do with it is make a [blog](https://ds0.xyz/opening-ceremony). I followed the [Flaskr](http://flask.pocoo.org/docs/0.12/tutorial/introduction/) tutorial to make mine, with a few modifications here and there, mostly inspired by [Charles Leiffer](http://charlesleifer.com/blog/how-to-make-a-flask-blog-in-one-hour-or-less/), minus a few things here and there.

I'll be real with you: it isn't very pretty. There are no tests. I foolishly set up the Python virtualenv to occupy the same folder as the blog itself. There are practically zero features right now. Nevertheless, I'm publicly releasing this repo as a little encouragement for myself to keep developing it.

## Setup

First, you'll need a working install of virtualenv for Python. I recommend using Python 3.x, so replace the `pip` command with `pip3` depending on your setup.

```
pip install virtualenv
```

Next, you'll need to clone the repository and place a virtual environment within it.
```
git clone https://github.com/dsvoid/flaskrBlog.git
virtualenv flaskrBlog
```

Now you are going to set up the blog and its necessary packages from within the virtual environment.
```
cd flaskrBlog
source bin/activate
pip install -r requirements.txt
pip install --editable .
```

It's time to set up some security. We start by creating a [hashed and salted password](http://flask.pocoo.org/snippets/54/) for the blog: this is done with Werkzeug. Run python in the virtualenv and follow these commands:
```
python
>>> from werkzeug.security import generate_password_hash
>>> print(generate_password_hash('PUT_THE_PASSSWORD_YOU_WANT_HERE'))
```

Copy down the hash that gets ouput and remember your password. Now make a `keys.py` file in the current directory, and fill it in like so (you can generate a key at [this handy website](https://randomkeygen.com/)):
```
keys =  dict(
    DATABASE=('flaskr.db'),
    SECRET_KEY='DEVELOPMENT_KEY_GOES_HERE',
    USERNAME='PICK_A_USERNAME_HERE',
    PASSWORD='THE_HASH_YOU_GENERATED_EARLIER_GOES_HERE')
```

We're almost there. It's time to point to flaskr as the main application, initialize the database, and run the application.
```
export FLASK_APP=flaskr
export FLASK_DEBUG=true
flask initdb
flask run
```

Now the application should host the website at `http://127.0.0.1:5000/`

## Usage

First you'll need to log in using the credentials you set up earlier by going to `/login`. Once you've done that, you have some options:

- `/add` to make a new post. Check "Publish post" for it to appear publicly.
- `/admin` to view all your posts whether published or not, and edit them.
- `/logout` to end your session.
- `/archive` to view an archive of your posts.
