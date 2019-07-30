from db.db_model import db, sessionMeta
from sqlalchemy import and_


def get_session_file_comments(file_id, current_session):
    f = db.session.query(sessionMeta).filter(and_(sessionMeta.file_id == file_id, sessionMeta.session == current_session)).first()
    if f.comment is None:
        return "None"
    else:
        return f.comment


def save_session_file_comments(file_id, current_session, comments):
    f = db.session.query(sessionMeta).filter(and_(sessionMeta.file_id == file_id, sessionMeta.session == current_session)).first()
    f.comment = comments
    db.session.commit()
