import secrets
import os
from flask_login import current_user
from db.db_model import db, DataFile
from sdproc.files.utils import file_type, root_folder, save_user_file, file_path


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
