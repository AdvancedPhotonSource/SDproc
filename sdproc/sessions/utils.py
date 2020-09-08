from db.db_model import db, SessionMeta, CurrentMeta
from sqlalchemy import and_


def get_session_file_comments(file_id, current_session):
    f = db.session.query(CurrentMeta).filter(and_(CurrentMeta.file_id == file_id, CurrentMeta.session == current_session
                                                  )).first()
    if f.comment is None:
        return "None"
    else:
        return f.comment


def save_session_file_comments(file_id, current_session, comments):
    f = db.session.query(CurrentMeta).filter(and_(CurrentMeta.file_id == file_id, CurrentMeta.session == current_session
                                                  )).first()
    f.comment = comments
    db.session.commit()
