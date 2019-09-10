import json
import secrets
import os
from dm import ExperimentDsApi, FileCatApi
from flask import Blueprint, request, current_app
from flask_login import login_required, current_user
from db.db_model import db, GlobusTree, DataFile
from sqlalchemy import and_, or_
from sdproc.files.utils import file_type, root_folder, save_user_file, file_path


globus = Blueprint('globus', __name__)


exApi = ExperimentDsApi(username='user3id', password='j7g$MAC;kG', url='https://xraydtn01.xray.aps.anl.gov:22236')
fApi = FileCatApi(username='user3id', password='j7g$MAC;kG', url='https://s3iddm.xray.aps.anl.gov:44436')


@globus.route('/globus_tree', methods=['GET', 'POST'])
@login_required
def globus_tree():
    user = 'd' + str(current_user.badge_number)
    root_list = []
    tree_data = [{"text": "3ID", "id": 0, "parent": "#", "type": "Root", "state": {"opened": "true", "disabled": "true"}}]

    experiments = exApi.getExperimentsByStation("3ID")

    for e in experiments:
        e_name = e['name']
        experiment = exApi.getExperimentByName(e_name)
        if user in experiment['experimentUsernameList']:
            roots(e_name, root_list)
            ex = GlobusTree.query.filter_by(name=e_name).first()
            tree_data.append({"text": ex.name, "id": ex.id, "parent": ex.parent, "type": ex.type})
            get_files(ex.id, tree_data)
    get_roots(root_list, tree_data)
    print("added nodes to list")

    return json.dumps(tree_data)


@globus.route('/globus_file', methods=['GET', 'POST'])
@login_required
def globus_file():
    f_id = request.form.get("f_id")
    f = GlobusTree.query.filter_by(id=f_id).first()
    if f.type == "File":
        p = GlobusTree.query.filter_by(id=GlobusTree.query.filter_by(id=f.parent).first().parent).first()
        download = exApi.downloadFile(f.experiment_file_path, p.name, "./static/uploaded_files/" + f.name[-3:] + "/")
        save_globus(download)

    return "Done"


def save_globus(download):
    random_hex = secrets.token_hex(4)
    f_name, f_ext = os.path.splitext(download['fileName'])
    unique_name = f_name + "_" + random_hex + f_ext
    f_path = file_path(f_ext, unique_name)
    os.rename(download['localFilePath'], f_path)
    f_id = add_file_db(download['fileName'], unique_name, f_ext)
    save_user_file(f_id)


def add_file_db(file_name, unique_name, f_ext):
    name = file_name
    path = unique_name
    authed = str(current_user.id)
    # default value give, can be changed later
    comChar = "#"
    type = file_type(f_ext)
    root_id = root_folder()
    data_file = DataFile(name=name, path=path, comment="No comment(s)", authed=authed, comChar=comChar, type=type,
                         parentID=root_id, treeType="File")
    db.session.add(data_file)
    db.session.commit()
    return data_file.id


"""------------------------------------------------------------------------------------------------"""


def get_roots(root_list, tree_data):
    if root_list is not None:
        for r in root_list:
            root = GlobusTree.query.filter_by(name=r).first()
            tree_data.append({"text": root.name, "id": root.id, "parent": root.parent, "type": root.type})


def roots(experiment_name, root_list):
    experiment = exApi.getExperimentByName(experiment_name)
    try:
        folder = experiment['rootPath']
    except Exception, e:
        folder = None

    if folder is not None:
        if folder not in root_list:
            root_list.append(folder)


def get_files(parent, tree_data):
    scans = GlobusTree.query.filter(and_(GlobusTree.name == "Scans", GlobusTree.parent == parent)).first()
    data = GlobusTree.query.filter(and_(GlobusTree.name == "Data", GlobusTree.parent == parent)).first()
    files = GlobusTree.query.filter(or_(GlobusTree.parent == scans.id, GlobusTree.parent == data.id))

    tree_data.append({"text": scans.name, "id": scans.id, "parent": scans.parent, "type": scans.type})
    tree_data.append({"text": data.name, "id": data.id, "parent": data.parent, "type": data.type})
    for f in files:
        tree_data.append({"text": f.name, "id": f.id, "parent": f.parent, "type": f.type})

    return tree_data


@globus.route('/update_globus', methods=['GET', 'POST'])
@login_required
def update_globus():
    folder_list = []
    # user_id = "d65218"
    experiments = exApi.getExperimentsByStation("3ID") # hard coded station

    # clearing the database for update
    GlobusTree.query.delete()
    db.session.commit()
    print("cleared db")

    """ Getting Experiments and finding their parent folders"""
    for e in experiments:
        try:
            folder = e['rootPath']
        except Exception, e:
            folder = None
        if folder is not None:
            if folder not in folder_list:
                folder_list.append(folder)

    # adding parent folders of experiments to the db
    for f in folder_list:
        node = GlobusTree(name=f, parent=0, type="Folder")
        db.session.add(node)
        db.session.commit()
    print("added parent folders of experiments")

    # adding experiments to the db
    for e in experiments:
        e_name = e['name']
        try:
            folder = e['rootPath']
        except Exception, e:
            folder = None
        if folder is not None:
            parent = GlobusTree.query.filter_by(name=folder).first()
            node = GlobusTree(name=e_name, parent=parent.id, type="Folder")
        else:
            node = GlobusTree(name=e_name, parent=0, type="Folder")
        db.session.add(node)
        db.session.commit()
    print("added experiments to db")

    # adding scans/data folder to each experiment
    for e in experiments:
        e_name = e['name']
        parent = GlobusTree.query.filter_by(name=e_name).first()
        scans = GlobusTree(name="Scans", parent=parent.id, type="Folder")
        data = GlobusTree(name="Data", parent=parent.id, type="Folder")
        db.session.add(scans)
        db.session.add(data)
        db.session.commit()
    print("added scans/data folders to all experiments")

    # adding files to folders
    for e in experiments:
        e_name = e['name']
        files = fApi.getExperimentFiles(e_name)
        e_parent = GlobusTree.query.filter_by(name=e_name).first()
        scans = GlobusTree.query.filter(and_(GlobusTree.name == "Scans", GlobusTree.parent == e_parent.id)).first()
        data = GlobusTree.query.filter(and_(GlobusTree.name == "Data", GlobusTree.parent == e_parent.id)).first()
        for f in files:
            if f['fileName'][-3:] == 'dat':
                node = GlobusTree(name=f['fileName'], parent=data.id, type="File", experiment_file_path=f["experimentFilePath"])
                db.session.add(node)
            elif f['fileName'][-3:] == 'mda':
                node = GlobusTree(name=f['fileName'], parent=scans.id, type="File", experiment_file_path=f["experimentFilePath"])
                db.session.add(node)
            db.session.commit()
    print("added files to db")

    return "Updated"
