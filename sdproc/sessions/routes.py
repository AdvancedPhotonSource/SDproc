import os
import matplotlib

matplotlib.use('Agg')

from flask import Blueprint, request, flash, json, redirect, url_for, render_template, current_app
from flask_login import current_user, login_required
from db.db_model import db, CurrentDAT, CurrentMeta, User, DataFile, UserFiles, SessionFiles, SessionFilesMeta, \
    SessionMeta
from utilities.graphing_utility import GraphingUtility
from utilities.file_utility import FileUtility
from sqlalchemy import and_, desc
from sdproc.files.utils import file_path, delete_user_file
from sdproc.utils.utils import get_comments, save_comments
from sdproc.sessions.utils import get_session_file_comments, save_session_file_comments
from db.api.file_db_api import FileDbApi

sessions = Blueprint('sessions', __name__)
fileApi = FileDbApi()


@sessions.route('/delete_session', methods=['GET', 'POST'])
def delete_session():
    type = request.form.get("type")
    id = request.form.get("id")

    if type == 'session':
        session = SessionFiles.query.filter_by(id=id).first()
        session_files = SessionFilesMeta.query.filter_by(sessionFiles_id=session.id).all()

        for file in session_files:
            session_meta = SessionMeta.query.filter_by(id=file.sessionMeta_id).first()
            db.session.delete(session_meta)
            db.session.delete(file)

        db.session.delete(session)
    elif type == 'dat':
        data_file = DataFile.query.filter_by(id=id).first()
        delete_user_file(data_file.id)
        path = file_path("." + data_file.type, data_file.path)
        os.remove(path)
        db.session.delete(data_file)

    db.session.commit()

    return ""


@sessions.route('/get_session_comment', methods=['GET', 'POST'])
def session_comment():
    f_type = request.form.get("type")
    file_id = request.form.get("id")

    if f_type == 'session':
        return get_comments(file_id, SessionFiles)
    elif f_type == 'dat':
        return get_comments(file_id, DataFile)


@sessions.route('/save_session_comment', methods=['GET', 'POST'])
def save_session_comment():
    f_type = request.form.get("type")
    file_id = request.form.get("id")
    comments = request.form.get("comment")

    if f_type == 'session':
        save_comments(file_id, SessionFiles, comments)
    elif f_type == 'dat':
        save_comments(file_id, DataFile, comments)
    return "Saved"


@sessions.route('/get_fsession_comment', methods=['GET', 'POST'])
def fsession_comment():
    file_id = request.form.get('id')
    print file_id
    session = current_user.current_session
    print session
    return get_session_file_comments(file_id, session)


@sessions.route('/save_fsession_comment', methods=['GET', 'POST'])
def save_fsession_comment():
    file_id = request.form.get('id')
    session = current_user.current_session
    comments = request.form.get('comment')
    save_session_file_comments(file_id, session, comments)
    return "Saved"


@sessions.route('/select2', methods=['GET', 'POST'])
@login_required
def index2():
    if current_user.badge_number is None:
        flash('Please update your badge number in order to continue', 'info')
        return redirect(url_for('users.profile2'))
    """
    Template generator method for the select page.

    Sends all sessions and DAT files in a template for the user to use so long as they are authenticated.

    This is done with a database query and authenticated in view_output.html.
    :return:
    """
    users = User.query.filter(User.id != current_user.id).all()
    if current_user.id == 1:
        user_sessions = SessionFiles.query.all()
        user_data_files = DataFile.query.filter_by(type='dat')
    else:
        try:
            user_sessions = SessionFiles.query.filter_by(user_id=current_user.id)
            user_data_files = DataFile.query.filter(and_(DataFile.type == 'dat', DataFile.authed ==
                                                         str(current_user.id)))
        except Exception, e:
            print(str(e))
            user_sessions = None
            user_data_files = None

    return render_template('session.html', title='Select Session', sessions=user_sessions, data_files=user_data_files,
                           users=users)


@sessions.route('/clear_cmeta', methods=['GET', 'POST'])
@login_required
def clear_cmeta():
    """
    Function that clears the current user's CurrentMeta Table.

    This is usually called when starting a new session or resuming an old one so that prexisting data
    does not cause conflicts.
    :return:
    """
    current_user.current_session = 'None'
    deleting = db.session.query(CurrentMeta).filter(CurrentMeta.user_id == current_user.get_id()).all()
    for i in deleting:
        db.session.delete(i)
    deleting = db.session.query(CurrentDAT).filter(CurrentDAT.user_id == current_user.get_id()).all()
    for i in deleting:
        db.session.delete(i)
    db.session.commit()
    return 'Cleared'


@sessions.route('/clearPart_cmeta', methods=['GET', 'POST'])
@login_required
def clearPart_cmeta():
    """
        Function that deletes a single file from the current users CurrentMeta table.

        This is called when removing a file on the format page.
        :return:
        """
    idthis = request.form.get('id', type=int)
    deleting = db.session.query(CurrentMeta).filter(and_(CurrentMeta.user_id == current_user.get_id(),
                                                         CurrentMeta.file_id == idthis,
                                                         CurrentMeta.session == current_user.current_session)).first()
    db.session.delete(deleting)
    db.session.commit()
    return 'Cleared'


@sessions.route('/clear_rowa', methods=['GET', 'POST'])
@login_required
def clear_rowa_wrapper():
    '''Simple function to clear the run_once_with_args decorator for loading the base comments of files.'''
    fileApi.setBaseComment(-1, current_user.get_id(), current_user.current_session)
    return 'Cleared'


@sessions.route("/share_session", methods=['GET', 'POST'])
@login_required
def share_session():
    user_id = request.form.get("user_id")
    user = User.query.filter_by(id=user_id).first()
    type = request.form.get("type")
    file_id = request.form.get("session_id")

    root_folder = DataFile.query.filter(and_(DataFile.name == "/" + user.username + "/", DataFile.treeType == "Root")).first()

    if type == 'session':
        shared_session = SessionFiles.query.filter_by(id=file_id).first()
        new_session = SessionFiles(name=shared_session.name, user_id=user.id, user=user, comment=shared_session.comment,
                                authed=str(user.id), last_used=shared_session.last_used)
        db.session.add(new_session)
        db.session.commit()
        session_files = SessionFilesMeta.query.filter_by(sessionFiles_id=shared_session.id).all()
        add_session_metas(session_files)
        flash("You have shared your file.", "success")
        return ""
    elif type == 'dat':
        shared_file = DataFile.query.filter_by(id=file_id).first()
        new_file = DataFile(name=shared_file.name, path=shared_file.path, comment=shared_file.comment,
                            authed=str(user.id), comChar=shared_file.comChar, type=shared_file.type,
                            parentID=root_folder.id, treeType=shared_file.treeType)
        db.session.add(new_file)
        db.session.commit()
        add_user_file(user)
        flash("You have shared your file.", "success")
        return ""


def add_session_metas(session_files):
    session_files = session_files
    counter = 0
    list = [0]

    for x in session_files:
        counter += 1
        list.append(counter)
        shared_meta = SessionMeta.query.filter_by(id=x.sessionMeta_id).first()
        session_meta = SessionMeta()
        session_meta.fileName = shared_meta.fileName
        session_meta.path = shared_meta.path
        session_meta.comment = shared_meta.comment
        session_meta.file_id = shared_meta.file_id
        session_meta.session = shared_meta.session
        session_meta.checked = shared_meta.checked

        session_meta.fit_type = shared_meta.fit_type
        session_meta.fit_pos = shared_meta.fit_pos
        session_meta.fit_range = shared_meta.fit_range
        session_meta.fit_localRange = shared_meta.fit_localRange
        session_meta.fit_energy = shared_meta.fit_energy
        session_meta.fit_signal = shared_meta.fit_signal

        session_meta.against_E = shared_meta.against_E

        session_meta.hrm = shared_meta.hrm

        session_meta.energy = shared_meta.energy
        session_meta.xtal1A = shared_meta.xtal1A
        session_meta.xtal2A = shared_meta.xtal2A
        session_meta.xtal1T = shared_meta.xtal1T
        session_meta.xtal2T = shared_meta.xtal2T
        session_meta.signal = shared_meta.signal
        session_meta.norm = shared_meta.norm
        session_meta.extra = shared_meta.extra

        session_meta.ebool = shared_meta.ebool
        session_meta.ecbool = shared_meta.ecbool
        session_meta.etcbool = shared_meta.etcbool
        session_meta.a1bool = shared_meta.a1bool
        session_meta.a2bool = shared_meta.a2bool
        session_meta.t1bool = shared_meta.t1bool
        session_meta.t2bool = shared_meta.t2bool
        session_meta.tcbool = shared_meta.tcbool
        session_meta.sbool = shared_meta.sbool
        session_meta.snbool = shared_meta.snbool
        session_meta.nbool = shared_meta.nbool
        session_meta.nfbool = shared_meta.nfbool
        session_meta.xbool = shared_meta.xbool
        db.session.add(session_meta)
    db.session.commit()
    list.remove(counter)
    add_session_files(list)


def add_user_file(user):
    user = user
    new_file = DataFile.query.order_by(desc('id')).first()

    new_user_file = UserFiles(user_id=user.id,file_id=new_file.id)
    db.session.add(new_user_file)
    db.session.commit()


def add_session_files(list):
    new_session = SessionFiles.query.order_by(desc('id')).first()
    new_meta = SessionMeta.query.order_by(desc('id')).first()

    for x in reversed(list):
        new_session_file = SessionFilesMeta(sessionFiles_id=new_session.id, sessionMeta_id=(new_meta.id - x))
        db.session.add(new_session_file)

    db.session.commit()


@sessions.route('/new_session2', methods=['POST'])
def new_session2():
    clear_cmeta()
    clear_rowa_wrapper()
    return ""


@sessions.route("/continue_session", methods=['GET', 'POST'])
def continue_session():
    type = request.form.get("type")
    id = request.form.get("id")
    user = current_user

    if type == "session":
        clear_cmeta()
        clear_rowa_wrapper()
        data_files = []
        session = SessionFiles.query.filter_by(id=id).first()
        session_files = SessionFilesMeta.query.filter_by(sessionFiles_id=session.id).all()
        for file in session_files:
            file_meta = SessionMeta.query.filter_by(id=file.sessionMeta_id).first()
            data_file = DataFile.query.filter_by(id=file_meta.file_id).first()
            form = GraphingUtility.populate_from_instance(file_meta) # populates the input form
            current_meta = CurrentMeta() # makes a CurrentMeta() object
            form.populate_obj(current_meta) # populates fields in the CurrentMeta object from the form
            current_meta.name = data_file.name
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
            data_file = DataFile.query.filter_by(id=id).first()
            path = file_path("." + data_file.type, data_file.path)
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
            current_data = CurrentDAT(user_id=user.id, file_id=data_file.id, user=user, DATname=data_file.name, DAT=data, originDAT=data)
            db.session.add(current_data)
            db.session.commit()
        except Exception, e:
            print(str(e))
        return ""


@sessions.route('/save_ses', methods=['GET', 'POST'])
@login_required
def saveSession():
    '''
    This saves the current session so that the user may resume from the select page whenever they want.

    The CurrentMeta table is parsed and saved into the SessionFiles and SessionFilesMeta tables for more permanence.
    A check is done to ensure that the user cannot save the session under a name that has already been created.
    :return:
    '''
    checked = request.form.get("checked", type=int)
    namechk = request.form.get("name", type=str)
    if checked == 0:
        instance = db.session.query(SessionFiles).filter(
            and_(SessionFiles.user_id == current_user.get_id(), SessionFiles.name == namechk)).first()
        if instance:
            data = str(instance.id)
            return data

    session_file = SessionFiles()
    session_file.user = current_user
    session_file.user_id = current_user.get_id()
    session_file.authed = current_user.get_id()
    session_file.name = request.form.get("name", type=str)
    session_file.comment = request.form.get("comment", type=str)
    session_file.last_used = FileUtility.getTime()
    db.session.add(session_file)
    db.session.commit()

    for instance in db.session.query(CurrentMeta).filter(CurrentMeta.user_id == current_user.get_id()).all():
        form = GraphingUtility.populate_from_instance(instance)
        session_instance = SessionMeta()
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

        session_file_instance = SessionFilesMeta()
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
