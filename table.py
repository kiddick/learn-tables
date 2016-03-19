import datetime
from functools import wraps

from flask import Flask, Blueprint
from flask import redirect, request, session, g
from flask import url_for, abort, render_template, flash

from models import db, User, Goal, Section, Subsection

FLASH_ERROR = 'error'
FLASH_INFO = 'info'
# todo: DRY - constants

table_page = Blueprint(
    'table', __name__, template_folder='templates', static_folder='static')


# todo: DRY
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('logged_in'):
            return f(*args, **kwargs)
        else:
            flash('You must log in to view tables', FLASH_ERROR)
            return redirect(url_for('login'))
    return wrapper


@table_page.before_request
def before_request():
    g.db = db
    g.db.connect()


@table_page.after_request
def after_request(response):
    g.db.close()
    return response


# Read

@table_page.route('/table/<username>', methods=['GET'])
@login_required
def show_table(username):
    # if session['username'] == username:
    sections = Section.select().where(Section.user == session['user_id'])
    sections = list(sections)[::-1]  # stub
    subsections = []
    for section in sections:
        subsections += list(Subsection.select().where(Subsection.section == section.id))
    goals = Goal.select().where(Goal.user == session['user_id'])

    return render_template(
        'usertable.html',
        sections=sections,
        subsections=subsections,
        goals=goals
    )


# Create

@table_page.route('/modify_table/create_goal', methods=['POST'])
@login_required
def create_goal():
    Goal.create(
        title=request.form['goal_title'],
        user=session['user_id'],
        note='',
        subsection=int(request.form['subsection_id']),
        progress=0
    )
    Subsection.update(
        goals_num=Subsection.goals_num + 1
    ).where(
        Subsection.id == int(request.form['subsection_id'])).execute()

    return redirect(url_for('table.show_table', username=session['username']))


@table_page.route('/modify_table/create_section', methods=['POST'])
@login_required
def create_section():
    with db.transaction():
        s = Section.create(
            title=request.form['section_title'],
            user=session['user_id']
        )
        Subsection.create(
            title='default',
            user=session['user_id'],
            section=s.id
        )
    return redirect(url_for('table.show_table', username=session['username']))


@table_page.route('/modify_table/create_subsection', methods=['POST'])
@login_required
def create_subsection():
    Subsection.create(
        title=request.form['subsection_title'],
        user=session['user_id'],
        section=request.form['section_id']
    )
    return redirect(url_for('table.show_table', username=session['username']))


# Update

@table_page.route('/modify_table/update_section', methods=['POST'])
@login_required
def update_section():
    try:
        Section.update(
            title=request.form['new_title']
        ).where(
            Section.id == int(request.form['section_id'])).execute()

    except Exception as e:
        print str(e)
    return redirect(url_for('table.show_table', username=session['username']))


@table_page.route('/modify_table/update_subsection', methods=['POST'])
@login_required
def update_subsection():
    try:
        Subsection.update(
            title=request.form['new_title']
        ).where(
            Subsection.id == int(request.form['subsection_id'])).execute()

    except Exception as e:
        print str(e)
    return redirect(url_for('table.show_table', username=session['username']))


@table_page.route('/update_note/', methods=['POST'])
@login_required
def update_note():
    try:
        Goal.update(
            note=request.form['new_note']
        ).where(
            Goal.id == int(request.form['goal_id'])).execute()

    except Exception as e:
        print str(e)

    return redirect(url_for('table.show_table', username=session['username']))


# Delete

@table_page.route('/modify_table/delete_goal', methods=['POST'])
@login_required
def delete_goal():
    goal = Goal.get(Goal.id == int(request.form['goal_id']))

    Subsection.update(
        goals_num=Subsection.goals_num - 1
    ).where(
        Subsection.id == goal.subsection).execute()

    Goal.delete().where(Goal.id == goal.id).execute()

    return redirect(url_for('table.show_table', username=session['username']))


@table_page.route('/modify_table/delete_subsection', methods=['POST'])
@login_required
def delete_subsection():
    Subsection.delete().where(
        Subsection.id == int(request.form['subsection_id'])).execute()

    return redirect(url_for('table.show_table', username=session['username']))


@table_page.route('/modify_table/delete_section', methods=['POST'])
@login_required
def delete_section():
    if request.form['has_goals']:
        flash('Cant delete section which has goals', FLASH_ERROR)
        return redirect(url_for('table.show_table', username=session['username']))

    Subsection.delete().where(
        Subsection.section.id == int(request.form['section_id'])).execute()
    Section.delete().where(
        Section.id == int(request.form['section_id'])).execute()

    return redirect(url_for('table.show_table', username=session['username']))
