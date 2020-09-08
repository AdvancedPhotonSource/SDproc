from db.db_model import db, DataFile


def get_comments(file_id, table):
    table = table
    file_id = file_id
    f = table.query.filter_by(id=file_id).first()
    comments = f.comment
    return comments


def save_comments(file_id, table, comments):
    f = table.query.filter_by(id=file_id).first()
    f.comment = comments
    db.session.commit()
