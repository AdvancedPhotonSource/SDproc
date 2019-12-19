import json
import secrets
import os
from dm import ExperimentDsApi, FileCatApi
from flask import Blueprint, request
from flask_login import login_required, current_user
from db.db_model import db, DataFile
from sdproc.files.utils import file_type, root_folder, save_user_file, file_path


dm = Blueprint('dm', __name__)


exApi = ExperimentDsApi(username='username', password='password', url='url')
fApi = FileCatApi(username='username', password='password', url='url')


@dm.route('/get_dm_file', methods=['GET', 'POST'])
@login_required
def dm_file():
    path = request.form.get("path")
    exp = request.form.get('exp')
    type = request.form.get('type')

    download = exApi.downloadFile(path, exp, "./static/uploaded_files/" + type + "/")
    save_file(download)

    return "Done"


def save_file(download):
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


@dm.route('/dm_tree', methods=['GET', 'POST'])
@login_required
def dm_tree():
    exp_nm = request.args.get('id')
    parent = exp_nm

    new_data = []

    if exp_nm == '#':
        new_data = [{"text": "3ID", "id": "3ID", "parent": "#", "type": "Root",
                     "state": {"opened": "true", "disabled": "true"}}]

        experiments = exApi.getExperimentsByStation("3ID")

        for e in experiments:
            exp = e['name']
            try:
                root = e['rootPath']
            except KeyError:
                root = None

            if root is not None:
                if not any(obj['text'] == root for obj in new_data):
                    new_data.append({"text": root, "id": root, "parent": "3ID", "type": "Folder"})
                new_data.append({"text": exp, "id": exp, "parent": root, "type": "Folder", "children": True})
            else:
                new_data.append({"text": exp, "id": exp, "parent": "3ID", "type": "Folder", "children": True})
    else:
        e = exApi.getExperimentByName(exp_nm)
        if 'd' + str(current_user.badge_number) in e['experimentUsernameList']:
            files = fApi.getExperimentFiles(exp_nm)
            for f in files:
                filePath = f['experimentFilePath']
                folders = filePath.split("/")
                fID = f['id']
                do_fold(folders, parent, new_data, fID, exp_nm, filePath)

    return json.dumps(new_data)


def do_fold(folderList, parent, tree, fID, exp, path):
    if len(folderList) == 1:
        tree.append({"text": folderList[0], "id": fID, "parent": parent, "type": "File", "data": {"expName": exp,
                                                                                                  "path": path}})
    else:
        newFolder = folderList[0]
        if not any((obj['text'] == newFolder and obj['parent'] == parent) for obj in tree):
            tree.append({"text": newFolder, "id": newFolder, "parent": parent, "type": "Folder"})
        folderList.pop(0)
        do_fold(folderList, newFolder, tree, fID, exp, path)
