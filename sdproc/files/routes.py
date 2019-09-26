import json
import os

from sqlalchemy import desc, and_
from db.db_model import DataFile, db, UserFiles, SessionFilesMeta, SessionMeta, CurrentMeta
from sdproc.files.forms import FileUploadForm
from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from sdproc.files.utils import save_files, file_path, delete_user_file
from sdproc.utils.utils import get_comments, save_comments
from utilities.file_utility import FileUtility


files = Blueprint('files', __name__)


@files.route('/upload_files', methods=['GET', 'POST'])
@login_required
def upload_files():
    if current_user.badge_number is None:
        flash('Please update your badge number in order to continue', 'info')
        return redirect(url_for('users.profile2'))
    form = FileUploadForm()
    if form.validate_on_submit():
        files_uploaded = form.files.data
        save_files(files_uploaded)
    return render_template('upload.html', title='New Upload', form=form)


'''The beginning of methods for file structure'''
@files.route("/jsonData", methods=["GET", "POST"])
def data():
    data = []
    currentUser = current_user.get_id()

    if currentUser == 1:
        nodes = DataFile.query.all()
    else:
        nodes = DataFile.query.filter_by(authed=currentUser)

    for node in nodes:
        id = node.id
        title = node.name
        parent = node.parentID
        type = node.treeType

        if parent == 0:
            data.append({ "text": title, "id": id, "parent": "#", "type": type, "state": {"opened": "true", "disabled": "true"}})
        else:
            data.append({"text": title, "id": id, "parent": parent, "type": type})

    return json.dumps(data)


@files.route("/scans_data", methods=["GET","POST"])
def scans_data():
    data = []
    currentUser = current_user.get_id()

    if currentUser == 1:
        nodes = DataFile.query.all()
    else:
        nodes = DataFile.query.filter_by(authed=currentUser)

    for node in nodes:
        id = node.id
        title = node.name
        parent = node.parentID
        type = node.treeType
        file_type = node.type

        if parent == 0:
            data.append({"text": title, "id": id, "parent": "#", "type": type,
                         "state": {"opened": "true", "disabled": "true"}})
        else:
            if type == 'Folder':
                data.append({"text": title, "id": id, "parent": parent, "type": type, "state": {"disabled": "true"}})
            else:
                data.append({"text": title, "id": id, "parent": parent, "type": type})

    return json.dumps(data)


@files.route("/createNode", methods=["GET", "POST"])
def create():
    parent = request.form.get("parent")
    title = request.form.get("title")

    node = DataFile(name=title, path="", comment="This is a folder.", authed=current_user.get_id(), comChar="", type="",
                    parentID=parent, treeType="Folder")

    db.session.add(node)
    db.session.commit()
    return str(node.id)


@files.route("/renameN", methods=["GET", "POST"])
def rename():
    node_id = request.form.get("node")
    new_name = request.form.get("newName")

    node = DataFile.query.filter_by(id=node_id).first()

    if node.treeType == 'Folder':
        node.name = new_name
    else:
        node_type = node.type
        node.name = new_name + "." + node_type

    db.session.commit()
    return "done"


@files.route("/moveNode", methods=["GET", "POST"])
def move():
    parent = request.form.get("parent")
    node = request.form.get("node")

    currNode = DataFile.query.filter_by(id=node).first()

    currNode.parentID = parent
    db.session.commit()
    return "done"


@files.route("/deleteNode", methods=["GET", "POST"])
def delete():
    nodes = json.loads(request.form.get("nodes"))
    node = request.form.get("node")
    df = DataFile.query.filter_by(id=node).first()

    if df.treeType == "File":
        delete_user_file(df.id)
        path = file_path("." + df.type, df.path)
        os.remove(path)
    else:
        for f in nodes:
            df = DataFile.query.filter_by(id=f).first()
            db.session.delete(df)
    db.session.delete(df)
    db.session.commit()
    return "done"


@files.route("/get_file_comments", methods=["GET", "POST"])
def newC():
    file_id = request.form.get("id")
    return get_comments(file_id, DataFile)


@files.route("/save_file_comments", methods=["GET", "POST"])
def sc():
    file_id = request.form.get("id")
    comments = request.form.get("comment")
    save_comments(file_id, DataFile, comments)
    return "done"


'''The end of methods for file structure'''

''' methods for adding/removing files on current meta'''
@files.route("/remove_current_meta", methods=['GET', 'POST'])
def remove_current_meta():
    id = request.form.get("id")
    file = CurrentMeta.query.filter(and_(CurrentMeta.user_id==current_user.id,CurrentMeta.file_id == id)).first()
    db.session.delete(file)
    db.session.commit()
    return ""


@files.route("/add_file_current_meta", methods=['GET', 'POST'])
def add_file_current_meta():
    id = request.form.get("id")
    file = DataFile.query.filter_by(id=id).first()
    return "done"


@files.route("/get_file_name", methods=['GET', 'POST'])
def get_file_name():
    file_id = request.form.get('id', type=int)
    file_ids = json.loads(request.form.get('ids', type=str))

    if file_id:
        current_meta = db.session.query(CurrentMeta).filter(and_(CurrentMeta.user_id == current_user.get_id(),
                                                                 CurrentMeta.file_id == file_id,
                                                                 CurrentMeta.session == current_user.current_session)).\
                                                                 first()
        return json.dumps([current_meta.name, current_meta.checked])
    else:
        names = []
        for f_id in file_ids:
            current_meta = db.session.query(CurrentMeta).filter(and_(CurrentMeta.user_id == current_user.get_id(),
                                                                     CurrentMeta.file_id == f_id,
                                                                     CurrentMeta.session == current_user.current_session
                                                                     )).first()
            names.append([current_meta.name, current_meta.checked, f_id])
        return json.dumps(names)


@files.route('/header_file', methods=['GET', 'POST'])
@login_required
def header_file():
    idthis = request.form.get('id', type=int)
    file_instance = db.session.query(DataFile).filter_by(id=idthis).first()
    path = file_path("." + file_instance.type, file_instance.path)
    header = FileUtility.getHeader(file_instance.name, path)
    return json.dumps(header)


@files.route('/updateSumCheck', methods=['GET', 'POST'])
@login_required
def updateSumCheck():
    '''
    Updates the current meta to keep track of the checkbox associated with adding the file to the sum.
    :return:
    '''
    idthis = request.form.get('id', type=int)
    checkVal = request.form.get('check').lower() == "true"
    file = CurrentMeta.query.filter(and_(CurrentMeta.user_id==current_user.id,CurrentMeta.file_id == idthis)).first()
    file.checked = checkVal
    db.session.commit()
    return 'Updated'
