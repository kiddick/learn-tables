from functools import wraps

from flask import Blueprint
from flask import redirect, request, session, g
from flask import url_for, render_template, flash

import models


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
    g.db = models.db
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
    sections = models.Section.select().where(
        models.Section.user == session['user_id'])
    sections = list(sections)[::-1]  # stub
    subsections = []
    for section in sections:
        subsections += list(
            models.Subsection.select().where(models.Subsection.section == section.id))
    goals = models.Goal.select().where(models.Goal.user == session['user_id'])

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
    models.Goal.create(
        title=request.form['goal_title'],
        user=session['user_id'],
        note='',
        subsection=int(request.form['subsection_id']),
        progress=0
    )
    models.Subsection.update(
        goals_num=models.Subsection.goals_num + 1
    ).where(
        models.Subsection.id == int(request.form['subsection_id'])).execute()

    return redirect(url_for('table.show_table', username=session['username']))


@table_page.route('/modify_table/create_section', methods=['POST'])
@login_required
def create_section():
    with models.db.transaction():
        s = models.Section.create(
            title=request.form['section_title'],
            user=session['user_id']
        )
        models.Subsection.create(
            title='default',
            user=session['user_id'],
            section=s.id
        )
    return redirect(url_for('table.show_table', username=session['username']))


@table_page.route('/modify_table/create_subsection', methods=['POST'])
@login_required
def create_subsection():
    models.Subsection.create(
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
        models.Section.update(
            title=request.form['new_title']
        ).where(
            models.Section.id == int(request.form['section_id'])).execute()

    except Exception as e:
        print str(e)
    return redirect(url_for('table.show_table', username=session['username']))


@table_page.route('/modify_table/update_subsection', methods=['POST'])
@login_required
def update_subsection():
    try:
        models.Subsection.update(
            title=request.form['new_title']
        ).where(
            models.Subsection.id == int(request.form['subsection_id'])).execute()

    except Exception as e:
        print str(e)
    return redirect(url_for('table.show_table', username=session['username']))


@table_page.route('/update_note/', methods=['POST'])
@login_required
def update_note():
    try:
        models.Goal.update(
            note=request.form['new_note']
        ).where(
            models.Goal.id == int(request.form['goal_id'])).execute()

    except Exception as e:
        print str(e)

    return redirect(url_for('table.show_table', username=session['username']))


# Delete

@table_page.route('/modify_table/delete_goal', methods=['POST'])
@login_required
def delete_goal():
    goal = models.Goal.get(models.Goal.id == int(request.form['goal_id']))

    models.Subsection.update(
        goals_num=models.Subsection.goals_num - 1
    ).where(
        models.Subsection.id == goal.subsection).execute()

    models.Goal.delete().where(models.Goal.id == goal.id).execute()

    return redirect(url_for('table.show_table', username=session['username']))


@table_page.route('/modify_table/delete_subsection', methods=['POST'])
@login_required
def delete_subsection():
    models.Subsection.delete().where(
        models.Subsection.id == int(request.form['subsection_id'])).execute()

    return redirect(url_for('table.show_table', username=session['username']))


@table_page.route('/modify_table/delete_section', methods=['POST'])
@login_required
def delete_section():
    if request.form['has_goals']:
        flash('Cant delete section which has goals', FLASH_ERROR)
        return redirect(url_for('table.show_table', username=session['username']))

    models.Subsection.delete().where(
        models.Subsection.section.id == int(request.form['section_id'])).execute()
    models.Section.delete().where(
        models.Section.id == int(request.form['section_id'])).execute()

    return redirect(url_for('table.show_table', username=session['username']))
