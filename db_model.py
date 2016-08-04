__author__ = 'caschmitz'
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from app import app
from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship


db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    pwhash = db.Column(db.String())
    email = db.Column(db.String(120), nullable=True)
    notify = db.Column(db.Boolean())

    def __repr__(self):
        return '<User %r>' % (self.username)

    def check_password(self, pw):
        return check_password_hash(self.pwhash, pw)

    def set_password(self, pw):
        self.pwhash = generate_password_hash(pw)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


class logBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String())
    path = db.Column(db.String())
    comment = db.Column(db.String(), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('loggedUser', lazy='dynamic'))
    plot = db.Column(db.String())
    timestamp = db.Column(db.DateTime())
    session = db.Column(db.String())

    against_E = db.Column(db.Boolean())

    hrm = db.Column(db.String())

    energy = db.Column(db.Integer())
    xtal1A = db.Column(db.Integer())
    xtal2A = db.Column(db.Integer())
    xtal1T = db.Column(db.Integer())
    xtal2T = db.Column(db.Integer())
    signal = db.Column(db.Integer())
    norm = db.Column(db.Integer())
    extra = db.Column(db.Integer())

    ebool = db.Column(db.Boolean())
    ecbool = db.Column(db.Boolean())
    etcbool = db.Column(db.Boolean())
    a1bool = db.Column(db.Boolean())
    a2bool = db.Column(db.Boolean())
    t1bool = db.Column(db.Boolean())
    t2bool = db.Column(db.Boolean())
    tcbool = db.Column(db.Boolean())
    sbool = db.Column(db.Boolean())
    snbool = db.Column(db.Boolean())
    nbool = db.Column(db.Boolean())
    nfbool = db.Column(db.Boolean())
    xbool = db.Column(db.Boolean())


class dataFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String())
    path = db.Column(db.String())
    comment = db.Column(db.String())
    authed = db.Column(db.String())
    delim = db.Column(db.String())
    type = db.Column(db.String())


class currentMeta(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String())
    path = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('currentUser', lazy='dynamic'))
    plot = db.Column(db.String())
    comment = db.Column(db.String())
    file_id = db.Column(db.Integer())
    session = db.Column(db.String())

    fit_type = db.Column(db.String())
    fit_pos = db.Column(db.Float())
    fit_range = db.Column(db.Float)

    hrm = db.Column(db.String())

    against_E = db.Column(db.Boolean())

    energy = db.Column(db.Integer())
    xtal1A = db.Column(db.Integer())
    xtal2A = db.Column(db.Integer())
    xtal1T = db.Column(db.Integer())
    xtal2T = db.Column(db.Integer())
    signal = db.Column(db.Integer())
    norm = db.Column(db.Integer())
    extra = db.Column(db.Integer())

    ebool = db.Column(db.Boolean())
    ecbool = db.Column(db.Boolean())
    etcbool = db.Column(db.Boolean())
    a1bool = db.Column(db.Boolean())
    a2bool = db.Column(db.Boolean())
    t1bool = db.Column(db.Boolean())
    t2bool = db.Column(db.Boolean())
    tcbool = db.Column(db.Boolean())
    sbool = db.Column(db.Boolean())
    snbool = db.Column(db.Boolean())
    nbool = db.Column(db.Boolean())
    nfbool = db.Column(db.Boolean())
    xbool = db.Column(db.Boolean())


class sessionMeta(db.Model):
    __tablename__ = 'sessionMeta'
    id = db.Column(db.Integer, primary_key=True)

    fileName = db.Column(db.String())
    path = db.Column(db.String())
    comment = db.Column(db.String())
    file_id = db.Column(db.Integer())

    against_E = db.Column(db.Boolean())

    hrm = db.Column(db.String())

    energy = db.Column(db.Integer())
    xtal1A = db.Column(db.Integer())
    xtal2A = db.Column(db.Integer())
    xtal1T = db.Column(db.Integer())
    xtal2T = db.Column(db.Integer())
    signal = db.Column(db.Integer())
    norm = db.Column(db.Integer())
    extra = db.Column(db.Integer())

    ebool = db.Column(db.Boolean())
    ecbool = db.Column(db.Boolean())
    etcbool = db.Column(db.Boolean())
    a1bool = db.Column(db.Boolean())
    a2bool = db.Column(db.Boolean())
    t1bool = db.Column(db.Boolean())
    t2bool = db.Column(db.Boolean())
    tcbool = db.Column(db.Boolean())
    sbool = db.Column(db.Boolean())
    snbool = db.Column(db.Boolean())
    nbool = db.Column(db.Boolean())
    nfbool = db.Column(db.Boolean())
    xbool = db.Column(db.Boolean())


class sessionFiles(db.Model):
    __tablename__ = 'sessionFiles'
    id = db.Column(db.Integer, primary_key=True)
    #sessionMeta_id = db.Column(db.ForeignKey('sessionMeta.id'))
    #sessionMeta = relationship("sessionMeta")

    name = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('oldUser', lazy='dynamic'))
    comment = db.Column(db.String())
    authed = db.Column(db.String())
    last_used = db.Column(db.DateTime())
    #sessionMeta_ids = db.Column(db.String())


class sessionFilesMeta(db.Model):
    __tablename__ = 'sessionFilesMeta'

    sessionFilesMeta_id = db.Column(db.Integer, primary_key=True)
    sessionFiles_id = db.Column(db.ForeignKey('sessionFiles.id'))
    sessionMeta_id = db.Column(db.ForeignKey('sessionMeta.id'))

    #session_meta = relationship("sessionMeta")
    #session_files = relationship("sessionFiles", primaryjoin="and_(sessionFiles.id == foreign(sessionFilesMeta.sessionFiles_id), "
    #                            "sessionFiles.sessionMeta_id == sessionFilesMeta.sessionMeta_id)")
    #session_files = relationship("sessionFiles")
    #__table_args__ = (PrimaryKeyConstraint('sessionFilesMeta_id', 'sessionMeta_id'),
    #                  ForeignKeyConstraint(['sessionFiles_id', 'sessionMeta_id'],
    #                                       ['sessionFiles.id', 'sessionFiles.sessionMeta_id']),)

    #PrimaryKeyConstraint('sessionFile_ID', 'sessionMeta_ID')
    #ForeignKeyConstraint(['sessionFile_ID', 'sessionMeta_ID'], ['sessionFiles.id', 'sessionMeta.id'])
