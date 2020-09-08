import secrets
import os
from dm import ExperimentDsApi, FileCatApi
from flask_login import current_user
from db.db_model import db, DataFile
from sdproc.files.utils import file_type, root_folder, save_user_file, file_path

exApi = ExperimentDsApi(username='username', password='password', url='URL')
fApi = FileCatApi(username='username', password='password', url='URL')
exApi30id = ExperimentDsApi(username='username', password='password', url='URL')
fApi30id = FileCatApi(username='username', password='password', url='URL')


def get_download(station, path, exp, type):
    if station == "3ID":
        f = exApi.downloadFile(path, exp, "./static/uploaded_files/" + type + "/")
    elif station == "30ID":
        f = exApi30id.downloadFile(path, exp, "./static/uploaded_files/" + type + "/")

    save_file(f)


def lazy_load(station, exp_nm, badge_number, parent, new_data):
    if station == "3ID":
        e = exApi.getExperimentByName(exp_nm)
        files = fApi.getExperimentFiles(exp_nm)
    elif station == "30ID":
        e = exApi30id.getExperimentByName(exp_nm)
        files = fApi30id.getExperimentFiles(exp_nm)

    if 'd' + str(badge_number) in e['experimentUsernameList'] or str(badge_number) == str(300123):
        for f in files:
            filePath = f['experimentFilePath']
            folders = filePath.split("/")
            fID = f['id']
            do_fold(folders, parent, new_data, fID, exp_nm, filePath)


def add_exp_to_root(station, tree):
    if station == "3ID":
        experiments = exApi.getExperimentsByStation(station)
    elif station == "30ID":
        experiments = exApi30id.getExperimentsByStation(station)

    for e in experiments:
        exp = e['name']
        try:
            root = e['rootPath']
        except KeyError:
            root = None

        if root is not None:
            if not any(obj['text'] == root for obj in tree):
                tree.append({"text": root, "id": root, "parent": station, "type": "Folder"})
            tree.append({"text": exp, "id": exp, "parent": root, "type": "Folder", "children": True})
        else:
            tree.append({"text": exp, "id": exp, "parent": station, "type": "Folder", "children": True})

    return tree


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
