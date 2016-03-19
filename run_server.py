import datetime
from functools import wraps
from hashlib import md5

from flask import Flask
from flask import redirect, request, session, g
from flask import url_for, abort, render_template, flash

from models import db, User, Goal, Section, Subsection
from table import table_page
from forms import RegistrationForm, LoginForm

DEBUG = True
SECRET_KEY = '*@H#(PJ#PJF#Fpt^#@vrqjld!^2ci@g*b'
# todo: parse from config file

app = Flask(__name__)
app.config.from_object(__name__)
app.register_blueprint(table_page)

FLASH_ERROR = 'error'
FLASH_INFO = 'info'


@app.before_request
def before_request():
    g.db = db
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('logged_in'):
            return f(*args, **kwargs)
        else:
            flash('You must sign in', FLASH_ERROR)
            return redirect(url_for('login'))
    return wrapper


@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            user = User.get(
                username=request.form['username'],
                password=md5((request.form['password']).encode(
                    'utf-8')).hexdigest()
            )
            auth_user(user)
            return redirect(url_for('homepage'))
        except User.DoesNotExist:
            flash('Username or password is incorrect', FLASH_ERROR)
    return render_template('login.html', form=form)


def auth_user(user):
    session['logged_in'] = True
    session['user_id'] = user.id
    session['username'] = user.username
    flash('You are logged in as %s' % user.username, FLASH_INFO)


@app.route('/signUp/', methods=['GET', 'POST'])
def sign_up():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        with db.transaction():
            try:
                user = User.create(
                    username=request.form['username'],
                    password=md5((request.form['password']).encode(
                        'utf-8')).hexdigest(),
                    email=request.form['email']
                )
                auth_user(user)
                return redirect(url_for('homepage'))

            except IntegrityError:
                flash('Such username has already taken', FLASH_ERROR)

    return render_template('signup.html', form=form)


@app.route('/logout/')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out', FLASH_INFO)
    return redirect(url_for('homepage'))


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
