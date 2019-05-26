import json

from sqlalchemy import desc
from db.db_model import dataFile, db
from sdproc.files.forms import FileUploadForm
from flask import Blueprint, render_template, url_for, request
from flask_login import login_required, current_user
from sdproc.files.utils import save_files


files = Blueprint('files', __name__)


@files.route('/upload_files', methods=['GET', 'POST'])
@login_required
def upload_files():
    form = FileUploadForm()
    if form.validate_on_submit():
        files_uploaded = form.files.data
        save_files(files_uploaded)
    return render_template('new_upload.html', title='New Upload', form=form)


'''The beginning of methods for file structure'''
@files.route("/jsonData", methods=["GET", "POST"])
def data():
    data = []
    currentUser = current_user.get_id()

    if currentUser == 1:
        nodes = dataFile.query.all()
    else:
        nodes = dataFile.query.filter_by(authed=currentUser)

    for node in nodes:
        id = node.id
        title = node.name
        parent = node.parentID
        type = node.treeType

        if parent == 0:
            data.append({ "text" : title, "id" : id, "parent" : "#", "type" : type, "state" : { "opened" : "true", "disabled" : "true" } })
        else:
            data.append({"text": title, "id": id, "parent": parent, "type" : type})

    with open('static/someD4.json', 'w') as outfile:
        json.dump(data, outfile)

    return json.dumps(data)


@files.route("/scans_data", methods=["GET","POST"])
def scans_data():
    data = []
    currentUser = current_user.get_id()

    if currentUser == 1:
        nodes = dataFile.query.all()
    else:
        nodes = dataFile.query.filter_by(authed=currentUser)

    for node in nodes:
        id = node.id
        title = node.name
        parent = node.parentID
        type = node.treeType
        file_type = node.type

        if file_type == "mda" or file_type == "txt" or file_type == "":
            if parent == 0:
                data.append({"text": title, "id": id, "parent": "#", "type": type, "state": {"opened": "true", "disabled": "true"}})
            elif type == "Folder":
                data.append({"text": title, "id": id, "parent": parent, "type": type, "state": {"disabled": "true"}})
            else:
                data.append({"text": title, "id": id, "parent": parent, "type" : type})

    with open('static/scans_data.json', 'w') as outfile:
        json.dump(data, outfile)

    return json.dumps(data)


@files.route("/createNode", methods=["GET","POST"])
def create():
    parent = request.form.get("parent")
    title = request.form.get("title")

    node = dataFile(name=title, path="", comment="This is a folder.", authed=current_user.get_id(), comChar="", type="", parentID=parent, treeType="Folder")

    db.session.add(node)
    db.session.commit()
    return "Done"



@files.route("/renameN", methods=["GET", "POST"])
def rename():
    node = request.form.get("node")
    newName = request.form.get("newName")

    if "j" in node:
        node = dataFile.query.order_by(desc('id')).first()
        type = node.type
        node.name = newName + "." + type
    else:
        currNode = dataFile.query.filter_by(id=node).first()
        type = currNode.type
        currNode.name = newName + "." + type

    db.session.commit()
    return "done"


@files.route("/moveNode", methods=["GET", "POST"])
def move():
    parent = request.form.get("parent")
    node = request.form.get("node")
    print parent;
    print node;

    currNode = dataFile.query.filter_by(id=node).first()

    currNode.parentID = parent
    db.session.commit()
    return "done"


@files.route("/deleteNode", methods=["GET", "POST"])
def delete():
    node = request.form.get("node")

    currNode = dataFile.query.filter_by(id=node).first()

    if currNode.treeType == "File":
        db.session.delete(currNode)
    else:
        recursive(currNode.id)
        db.session.delete(currNode)

    db.session.commit()
    return "done"


@files.route("/recursiveNode", methods=["GET", "POST"])
def recursive(parentID):
    nodes = dataFile.query.filter_by(parentID=parentID)
    for node in nodes:
        if node.treeType == "File":
            db.session.delete(node)
        else:
            recursive(node.id)
            db.session.delete(node)

    return "done"


@files.route("/show_NewComment", methods=["GET", "POST"])
def newC():
    id = request.form.get("id")
    node = dataFile.query.filter_by(id=id).first()
    nodecomment = node.comment
    return nodecomment


@files.route("/saveNC", methods=["GET", "POST"])
def sc():
    id = request.form.get("id")
    newcomment = request.form.get("comment")
    node = dataFile.query.filter_by(id=id).first()
    node.comment = newcomment
    db.session.commit()
    return "done"


'''The end of methods for file structure'''
