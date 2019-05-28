import os
from flask import Blueprint, request, flash, json, redirect, url_for, render_template, current_app
from flask_login import current_user, login_required
from db.db_model import db, currentDAT, currentMeta, User, dataFile, userFiles, sessionFiles, sessionFilesMeta, \
    sessionMeta
from utilities.graphing_utility import GraphingUtility
from utilities.file_utility import FileUtility
from sqlalchemy import and_, desc
from sdproc.user import clear_rowa_wrapper
from sdproc.files.utils import file_path
sessions = Blueprint('sessions', __name__)


@sessions.route('/delete_session', methods=['GET', 'POST'])
def delete_session():
    type = request.form.get("type")
    id = request.form.get("id")

    if type == 'session':
        session = sessionFiles.query.filter_by(id=id).first()
        session_files = sessionFilesMeta.query.filter_by(sessionFiles_id=session.id).all()

        for file in session_files:
            db.session.delete(file)

        db.session.delete(session)
    elif type == 'dat':
        data_file = dataFile.query.filter_by(id=id).first()
        user_file = userFiles.query.filter_by(file_id=data_file.id).first()
        db.session.delete(user_file)
        db.session.delete(data_file)

    db.session.commit()

    return ""


@sessions.route('/get_session_comment', methods=['GET', 'POST'])
def session_comment():
    type = request.form.get("type")
    id = request.form.get("id")
    comments = ""

    if type == 'session':
        session = sessionFiles.query.filter_by(id=id).first()
        comments = session.comment
    elif type == 'dat':
        data_file = dataFile.query.filter_by(id=id).first()
        comments = data_file.comment

    return comments


@sessions.route('/save_session_comment', methods=['GET', 'POST'])
def save_session_comment():
    type = request.form.get("type")
    id = request.form.get("id")
    comments = request.form.get("comment")

    if type == 'session':
        session = sessionFiles.query.filter_by(id=id).first()
        session.comment = comments
    elif type == 'dat':
        data_file = dataFile.query.filter_by(id=id).first()
        data_file.comment = comments

    db.session.commit()

    return ""


@sessions.route('/select2', methods=['GET', 'POST'])
@login_required
def index2():
    """
    Template generator method for the select page.

    Sends all sessions and DAT files in a template for the user to use so long as they are authenticated.

    This is done with a database query and authenticated in view_output.html.
    :return:
    """
    users = User.query.filter(id != current_user.id).all()
    if current_user.id == 1:
        user_sessions = sessionFiles.query.all()
        user_data_files = dataFile.query.filter_by(type='dat')
    else:
        try:
            user_sessions = sessionFiles.query.filter_by(user_id=current_user.id)
            user_data_files = dataFile.query.filter(and_(dataFile.type=='dat', dataFile.authed==str(current_user.id)))
        except Exception, e:
            print(str(e))
            user_sessions = None
            user_data_files = None

    return render_template('session.html', title='Select Session', sessions=user_sessions, data_files = user_data_files, users = users)


@sessions.route('/clear_cmeta', methods=['GET', 'POST'])
@login_required
def clear_cmeta():
    """
    Function that clears the current user's currentMeta Table.

    This is usually called when starting a new session or resuming an old one so that prexisting data does not cause conflicts.
    :return:
    """
    current_user.current_session = 'None'
    deleting = db.session.query(currentMeta).filter(currentMeta.user_id == current_user.get_id()).all()
    for i in deleting:
        db.session.delete(i)
    deleting = db.session.query(currentDAT).filter(currentDAT.user_id == current_user.get_id()).all()
    for i in deleting:
        db.session.delete(i)
    db.session.commit()
    return 'Cleared'


@sessions.route("/share_session", methods=['GET', 'POST'])
@login_required
def share_session():
    user_id = request.form.get("user_id")
    user = User.query.filter_by(id=user_id).first()
    type = request.form.get("type")
    file_id = request.form.get("session_id")

    root_folder = dataFile.query.filter(and_(dataFile.name == "/" + user.username + "/", dataFile.treeType == "Root")).first()

    if type == 'session':
        shared_session = sessionFiles.query.filter_by(id=file_id).first()
        new_session = sessionFiles(name=shared_session.name, user_id=user.id, user=user, comment=shared_session.comment,
                                authed=str(user.id), last_used=shared_session.last_used)
        db.session.add(new_session)
        db.session.commit()
        session_files = sessionFilesMeta.query.filter_by(sessionFiles_id=shared_session.id).all()
        add_user_file(session_files)
        flash("You have shared your file.", "success")
        return ""
    elif type == 'dat':
        shared_file = dataFile.query.filter_by(id=file_id).first()
        new_file = dataFile(name=shared_file.name, path=shared_file.path, comment=shared_file.comment,
                            authed=str(user.id), comChar=shared_file.comChar, type=shared_file.type,
                            parentID=root_folder.id, treeType=shared_file.treeType)
        db.session.add(new_file)
        db.session.commit()
        add_user_file(user)
        flash("You have shared your file.", "success")
        return ""


def add_user_file(user):
    user = user
    new_file = dataFile.query.order_by(desc('id')).first()

    new_user_file = userFiles(user_id=user.id,file_id=new_file.id)
    db.session.add(new_user_file)
    db.session.commit()


def add_session_files(session_files):
    session_files = session_files
    new_session = sessionFiles.query.order_by(desc('id')).first()

    for file in session_files:
        new_session_file = sessionFilesMeta(sessionFiles_id=new_session.id, sessionMeta_id=file.sessionMeta_id)
        db.session.add(new_session_file)

    db.session.commit()


@sessions.route('/new_session2', methods=['POST'])
def new_session2():
    clear_cmeta()
    clear_rowa_wrapper()
    return ""


def data_file_path(file_name):
    file_path = os.path.join(current_app.root_path, 'static/saved_files/dat', file_name)
    return file_path


@sessions.route("/continue_session", methods=['GET', 'POST'])
def continue_session():
    type = request.form.get("type")
    id = request.form.get("id")
    user = current_user

    if type == "session":
        clear_cmeta()
        clear_rowa_wrapper()
        data_files = []
        session = sessionFiles.query.filter_by(id=id).first()
        session_files = sessionFilesMeta.query.filter_by(sessionFiles_id=session.id).all()
        for file in session_files:
            file_meta = sessionMeta.query.filter_by(id=file.sessionMeta_id).first()
            data_file = dataFile.query.filter_by(id=file_meta.file_id).first()
            form = GraphingUtility.populate_from_instance(file_meta) # populates the input form
            current_meta = currentMeta() # makes a currentMeta() object
            form.populate_obj(current_meta) # populates fields in the currentMeta object from the form
            current_meta.path = file_path("." + data_file.type, data_file.path)
            current_meta.comment = file_meta.comment
            current_meta.checked = file_meta.checked
            current_meta.against_E = file_meta.against_E
            current_meta.file_id = file_meta.file_id
            current_meta.fit_type = file_meta.fit_type
            current_meta.fit_pos = file_meta.fit_pos
            current_meta.fit_range = file_meta.fit_range
            current_meta.hrm = file_meta.hrm
            current_meta.user = current_user
            current_meta.session = session.name
            db.session.add(current_meta)
            db.session.commit()
            data_files.append(current_meta.file_id)
        current_user.current_session = session.name
        db.session.commit()
        data = json.dumps(data_files)
        return data
    elif type == "dat":
        try:
            data_file = dataFile.query.filter_by(id=id).first()
            path = data_file_path(data_file.path)
            x_values = []
            y_values = []
            with open(path, 'r') as current_file:
                current_file = current_file.readlines()
                for line in current_file:
                    if not line.startswith("#"):
                        line = line.split()
                        x_values.append(float(line[0]))
                        y_values.append(float(line[1]))
            data = [x_values, y_values]
            data = json.dumps(data)
            current_data = currentDAT(user_id=user.id, file_id=data_file.id, user=user, DATname=data_file.name, DAT=data, originDAT=data)
            db.session.add(current_data)
            db.session.commit()
        except Exception, e:
            print(str(e))
        return ""
