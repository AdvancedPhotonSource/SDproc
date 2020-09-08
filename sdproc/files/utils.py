import os
import secrets

from flask import current_app
from flask_login import current_user
from sqlalchemy import and_, desc

from db.db_model import db, DataFile, UserFiles

"""
  definitions used to upload files. All of these definitions are used to handle file uploads.
"""


def save_files(form_files):
    for file in form_files:
        random_hex = secrets.token_hex(4)
        f_name, f_ext = os.path.splitext(file.filename)
        unique_name = f_name + "_" + random_hex + f_ext
        f_path = file_path(f_ext, unique_name)
        f_id = save_data_file(f_name, unique_name, file, f_ext)
        save_user_file(f_id)
        file.save(f_path)


def save_data_file(file_name, unique_name, file, f_ext):
    name = file_name + f_ext
    path = unique_name
    authed = str(current_user.id)
    comChar = comment_character(f_ext, file)
    type = file_type(f_ext)
    root_id = root_folder()
    data_file = DataFile(name=name, path=path, comment="No comment(s)", authed=authed, comChar=comChar, type=type,
                         parentID=root_id, treeType="File")
    db.session.add(data_file)
    db.session.commit()
    return data_file.id


def save_user_file(f_id):
    user_file = UserFiles(user_id=current_user.id, file_id=f_id)
    db.session.add(user_file)
    db.session.commit()


def delete_user_file(f_id):
    user_file = UserFiles.query.filter(and_(UserFiles.user_id == current_user.id, UserFiles.file_id == f_id)).first()
    db.session.delete(user_file)
    db.session.commit()


def root_folder():
    authed = str(current_user.id)
    user_root = DataFile.query.filter(and_(DataFile.authed == authed, DataFile.treeType == "Root")).first()
    root_id = user_root.id
    return root_id


def comment_character(f_ext, file):
    """
    This function returns the character used to comment out lines in a file. MDA files default
    comment character is '#'. TXT and DAT files do not have default comment characters because
    they are set by the user who created the file. The function reads the first character of a
    TXT or DAT file and interprets it as the comment character.
    :param f_ext: File extension. e.g. .mda, .txt., .dat
    :param file: The file being uploaded.
    :return: character used to comment out lines in the file
    """
    if f_ext == ".mda":
        comment_char = "#"
    else:
        comment_char = file.read(1)
    return comment_char


def file_path(f_ext, unique_name):
    type = file_type(f_ext)
    path = os.path.join(current_app.root_path, 'static/uploaded_files', type, unique_name)
    return path


def file_type(f_ext):
    """
    This function removes the dot (.) from a file extension
    :param f_ext: the file extension. e.g. .mda, .txt, .dat
    :return: file type. e.g. mda, txt, dat
    """
    type = None
    if f_ext == ".mda":
        type = "mda"
    elif f_ext == ".dat":
        type = "dat"
    elif f_ext == ".txt":
        type = "txt"
    return type
