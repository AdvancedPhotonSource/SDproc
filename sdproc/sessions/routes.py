from flask import Blueprint, request, flash, json, redirect, url_for, render_template
from flask_login import current_user, login_required
from db.db_model import db, currentDAT, currentMeta, User, dataFile, userFiles, sessionFiles, sessionFilesMeta, \
    sessionMeta
from utilities.graphing_utility import GraphingUtility
from utilities.file_utility import FileUtility
from sqlalchemy import and_, desc
from sdproc.user import clear_rowa_wrapper
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
        user_sessions = sessionFiles.query.filter_by(user_id= current_user.id)
        user_data_files = dataFile.query.filter_by(and_(type='dat', authed=str(current_user.id)))
    return render_template('new_session.html', title='Select Session', sessions=user_sessions, data_files = user_data_files, users = users)


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
        session_files = sessionFilesMeta.query.filter_by(sessionFiles_id=shared_session.id).all()
        db.session.commit()
        add_session_files(session_files)
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


@sessions.route('/set_ses', methods=['GET', 'POST'])
@login_required
def set_ses():
    '''
    Function that updates currentMeta/currentDAT based on which type of session is selected by the user.

    By setting these tables the user is then able to view/alter the information on the corresponding tabs.
    :return:
    '''
    if request.method == 'POST':
        files = []
        sesID = request.form.get('id', type=int)
        type = request.form.get('type', type=str)
        if type == 'dat':
            dat = db.session.query(dataFile).filter_by(id=sesID).first()
            with open(dat.path, 'r') as DATfile:
                data = DATfile.read()
                cDAT = currentDAT()
                cDAT.user = current_user
                cDAT.file_id = dat.id
                xs = []
                ys = []
                user = db.session.query(User).filter_by(username=current_user.username).first()
                data = data.split("\n")
                try:
                    data = [x for x in data if not x.startswith(user.commentChar)]
                except TypeError:
                    data = [x for x in data if not x.startswith('#')]
                    flash('No comment preference set, defaulting to #')
                for i in data:
                    if not i:
                        continue
                    line = i.split()
                    xs.append(float(line[0]))
                    ys.append(float(line[1]))
                DAT = [xs, ys]
                DAT = json.dumps(DAT)
                cDAT.DAT = DAT
                cDAT.originDAT = DAT
                if dat.name is not None:
                    cDAT.DATname = dat.name
                db.session.add(cDAT)
                db.session.commit()
            return 'Saved'
        allSes = db.session.query(sessionFiles).filter_by(id=sesID).first()
        metas = db.session.query(sessionFilesMeta).filter_by(sessionFiles_id=sesID).all()
        for meta in metas:
            actualMeta = db.session.query(sessionMeta).filter_by(id=meta.sessionMeta_id).first()
            form = GraphingUtility.populate_from_instance(actualMeta)
            newCurrent = currentMeta()
            form.populate_obj(newCurrent)
            newCurrent.path = actualMeta.path
            newCurrent.comment = actualMeta.comment
            newCurrent.checked = actualMeta.checked
            newCurrent.against_E = actualMeta.against_E
            newCurrent.file_id = actualMeta.file_id
            newCurrent.fit_type = actualMeta.fit_type
            newCurrent.fit_pos = actualMeta.fit_pos
            newCurrent.fit_range = actualMeta.fit_range
            newCurrent.hrm = actualMeta.hrm
            newCurrent.user = current_user
            newCurrent.session = allSes.name
            db.session.add(newCurrent)
            db.session.commit()
            files.append(newCurrent.file_id)
        current_user.current_session = allSes.name
        db.session.commit()
        data = json.dumps(files)
        return data
    return 'Set'


@sessions.route('/save_ses', methods=['GET', 'POST'])
@login_required
def saveSession():
    '''
    This saves the current session so that the user may resume from the select page whenever they want.

    The currentMeta table is parsed and saved into the sessionFiles and sessionFilesMeta tables for more permanence.
    A check is done to ensure that the user cannot save the session under a name that has already been created.
    :return:
    '''
    checked = request.form.get("checked", type=int)
    namechk = request.form.get("name", type=str)
    if checked == 0:
        instance = db.session.query(sessionFiles).filter(
            and_(sessionFiles.user_id == current_user.get_id(), sessionFiles.name == namechk)).first()
        if instance:
            data = str(instance.id)
            return data

    session_file = sessionFiles()
    session_file.user = current_user
    session_file.user_id == current_user.get_id()
    session_file.authed = current_user.get_id()
    session_file.name = request.form.get("name", type=str)
    session_file.comment = request.form.get("comment", type=str)
    session_file.last_used = FileUtility.getTime()
    db.session.add(session_file)
    db.session.commit()

    for instance in db.session.query(currentMeta).filter(currentMeta.user_id == current_user.get_id()).all():
        form = GraphingUtility.populate_from_instance(instance)
        session_instance = sessionMeta()
        form.populate_obj(session_instance)

        session_instance.file_id = instance.file_id
        session_instance.path = instance.path
        session_instance.comment = instance.comment
        session_instance.checked = instance.checked
        session_instance.against_E = instance.against_E
        session_instance.fit_type = instance.fit_type
        session_instance.fit_pos = instance.fit_pos
        session_instance.fit_range = instance.fit_range
        session_instance.hrm = instance.hrm
        session_instance.session = session_file.name
        db.session.add(session_instance)
        db.session.commit()

        session_file_instance = sessionFilesMeta()
        session_file_instance.sessionFiles_id = session_file.id
        session_file_instance.sessionMeta_id = session_instance.id

        instance.session = session_file.name

        db.session.add(session_file_instance)
        db.session.commit()
    current_user.current_session = session_file.name
    db.session.commit()
    if checked == 1:
        return current_user.current_session
    data = ({'status': 'Saved', 'name': current_user.current_session})
    sending = json.dumps(data)
    return sending
