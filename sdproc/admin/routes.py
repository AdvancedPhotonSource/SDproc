from flask import Blueprint, redirect, render_template, url_for, request, flash
from flask_login import login_required, current_user
from db.db_model import db, SessionFiles, DataFile, User, HRM, Notification as n, SessionFilesMeta, SessionMeta, UserFiles
from utilities.file_utility import FileUtility
from sdproc.files.utils import file_path
from forms import UserInfoForm
from sqlalchemy import and_

a = Blueprint('admin', __name__)


@a.route('/admin2', methods=['GET', 'POST'])
@login_required
def admin2():
    if current_user.badge_number is None:
        flash('Please update your badge number in order to continue', 'info')
        return redirect(url_for('users.profile2'))
    form = UserInfoForm()
    users = User.query.filter(User.id != current_user.id).all()
    hrms = HRM.query.order_by('id').all()
    notifications = n.query.order_by('id').all()
    new_users = []
    for x in notifications:
        for i in users:
            if x.originUser == i.username:
                new_users.append(i)

    return render_template('new_admin.html', title="Admin", users=users, hrms=hrms, notifications=notifications,
                           form=form, new_users=new_users)


@a.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    '''
    Template generator method for the admin page.

    Gets all sessions, files, users, and notifications.

    This is done by querying each respective sqlite database.
    Information is sent with the template to be parsed as needed by the user.
    :return:
    '''
    if current_user.isAdmin != 1:
        return redirect(url_for('index'))
    names = db.session.query(User)
    sesData = []
    fileData = []
    notifData = []
    hrmData = []
    sessions = SessionFiles.query.all()
    for instance in sessions:
        lastMod = instance.last_used
        sesData.insert(0, {'name': instance.name, 'id': instance.id, 'comment': instance.comment,
                           'authed': instance.authed,
                           'modified': lastMod})
    files = DataFile.query.filter_by(treeType="File").all()
    for instance in files:
        path = file_path("." + instance.type, instance.path)
        fsize = FileUtility.size(path)
        lastMod = FileUtility.modified(path)
        temp = lastMod
        modname = [instance.name + temp]
        fileData.insert(0,
                        {'name': instance.name, 'path': instance.path, 'id': instance.id, 'comment': instance.comment,
                         'authed': instance.authed, 'size': fsize, 'modified': lastMod, 'modname': modname})

    notifications = n.query.order_by('id')
    for instance in notifications:
        userInfo = db.session.query(User).filter_by(username=instance.originUser).first()
        if userInfo != None:
            notifData.insert(0, {'id': instance.id, 'name': instance.originUser, 'time': instance.timestamp,
                                 'type': instance.type, 'username': userInfo.username, 'email': userInfo.email,
                                 'fullName': userInfo.fullName, 'institution': userInfo.institution,
                                 'reason': userInfo.reason})

    hrms = HRM.query.order_by('id')
    for instance in hrms:
        hrmData.insert(0, {'name': instance.name, 'hrm_e0': instance.hrm_e0, 'hrm_bragg1': instance.hrm_bragg1,
                           'hrm_bragg2': instance.hrm_bragg2, 'hrm_geo': instance.hrm_geo,
                           'hrm_alpha1': instance.hrm_alpha1, 'hrm_alpha2': instance.hrm_alpha2,
                           'hrm_theta1_sign': instance.hrm_theta1_sign, 'hrm_theta2_sign': instance.hrm_theta2_sign})

    return render_template('admin.html', user=current_user, fileData=fileData, sesData=sesData,
                           names=names, notifications=notifData, hrms=hrms)


@a.route('/decline_user', methods=['GET', 'POST'])
@login_required
def decline_user():
    notification_id = request.form.get("notification_id")
    notification = n.query.filter_by(id=notification_id).first()
    user = User.query.filter_by(username=notification.originUser).first()
    db.session.delete(user)
    db.session.delete(notification)
    db.session.commit()
    return "deleted"


@a.route('/approve_user', methods=['GET', 'POST'])
@login_required
def approve_user():
    notification_id = request.form.get("notification_id")
    notification = n.query.filter_by(id=notification_id).first()
    user = User.query.filter_by(username=notification.originUser).first()
    user.approved = 1
    db.session.delete(notification)
    root = DataFile(name='/' + user.username + '/', authed=str(user.id), comChar='#', parentID=0, treeType="Root")
    db.session.add(root)
    db.session.commit()
    return "approved"


@a.route('/freeze', methods=['GET', 'POST'])
@login_required
def freeze():
    '''
    Freezes the designated user's account so that they may no longer login

    This is done by setting 'aUser'.approved to be 2.

    Only accessable by admins.
    :return:
    '''
    user = request.form.get('user', type=str)
    freeze = request.form.get('freeze', type=int)
    user_instance = db.session.query(User).filter_by(username=user).first()
    if freeze == 1:
        user_instance.approved = 2
    else:
        user_instance.approved = 1
    db.session.commit()
    return 'Updated'


""" Methods from the old admin python file, may not be used """


@a.route('/notifInfo', methods=['GET', 'POST'])
@login_required
def notifInfo():
    '''
    Supplementary template generator method for admin.

    Provides additional information about a n.

    This is done by querying the sqlite database 'n' based on the ID given.
    :return:
    '''
    notifID = request.form.get('id', type=int)
    notifInfo = db.session.query(n).filter_by(id=notifID).first()
    userInfo = db.session.query(User).filter_by(username=notifInfo.originUser).first()
    userData = {'username': userInfo.username, 'email': userInfo.email,
                'fullName': userInfo.fullName, 'institution': userInfo.institution,
                'reason': userInfo.reason}
    return render_template('admin.html', user=current_user, userProf=userData)


@a.route('/solveNotif', methods=['GET', 'POST'])
@login_required
def solveNotif():
    '''
    Resolves a n based on the action taken.

    This is done by updating the User based on if they were accepted or not.

    Only currently setup to handle account creation requests.
    :return:
    '''
    id = request.form.get('id', type=int)
    action = request.form.get('action', type=int)
    notif = db.session.query(n).filter_by(id=id).first()
    if action == 1:
        user = db.session.query(User).filter_by(username=notif.originUser).first()
        user.approved = 1
        username = user.username
        id = user.id
        rootnode = DataFile(name="/" + username + "/", path="", comment="This is the root node", authed=str(id),
                            comChar="", type="", parentID=0, treeType="Root")
        db.session.add(rootnode)
        db.session.delete(notif)
    else:
        db.session.delete(notif)
        user = db.session.query(User).filter_by(username=notif.originUser).first()
        db.session.delete(user)
        sessions = db.session.query(SessionFiles).filter(SessionFiles.user == user).all()
        for session in sessions:
            auths = session.authed.split(',')
            auths.remove(str(user.id))
            if len(auths) == 0:
                db.session.delete(session)
                instances = db.session.query(SessionFilesMeta).filter_by(sessionFiles_id=session.id).all()
                for instance in instances:
                    meta = db.session.query(SessionMeta).filter_by(id=instance.sessionMeta_id).first()
                    db.session.delete(meta)
                    db.session.deleta(instance)
            else:
                session.authed = ','.join(auths)
        fileIDs = db.session.query(UserFiles).filter(UserFiles.user_id == user.id).all()
        for id in fileIDs:
            file = db.session.query(DataFile).filter(DataFile.id == id.file_id).first()
            auths = file.authed.split(',')
            auths.remove(str(user.id))
            userFile = db.session.query(UserFiles).filter(
                and_(UserFiles.user_id == user.id, UserFiles.file_id == file.id)).first()
            db.session.delete(userFile)
            if len(auths) == 0:
                db.session.delete(file)
            else:
                file.authed = ','.join(auths)
    db.session.commit()
    return 'Solved'


@a.route('/getInfo', methods=['GET', 'POST'])
@login_required
def getInfo():
    '''
    Supplementary template generator for the admin page.

    Provides additional information about a file/session/user

    This is done through queries on their corresponding databases.
    :return:
    '''
    table = request.form.get('table', type=str)
    id = request.form.get('id', type=int)
    user = request.form.get('user', type=str)
    fileUsers = []
    UserFiles = []
    userSessions = []
    sessionUsers = []
    freeze = 0
    if table == 'File':
        file_instance = db.session.query(DataFile).filter_by(id=id).first()
        if file_instance != None:
            names = file_instance.authed.split(',')
            for name in names:
                user = db.session.query(User).filter_by(id=name).first()
                fileUsers.insert(0, {'fUser': user})
    if table == 'User':
        user = db.session.query(User).filter_by(username=user).first()
        freeze = user.approved
        files = DataFile.query.all()
        for instance in files:
            fsize = FileUtility.size(instance.path)
            lastMod = FileUtility.modified(instance.path)
            temp = lastMod.strftime("%d/%m/%Y %H:%M:%S")
            modname = [instance.name + temp]
            UserFiles.insert(0,
                             {'name': instance.name, 'path': instance.path, 'id': instance.id,
                              'comment': instance.comment,
                              'authed': instance.authed, 'size': fsize, 'modified': lastMod, 'modname': modname})

        sessions = SessionFiles.query.all()
        for instance in sessions:
            lastMod = instance.last_used
            userSessions.insert(0,
                                {'name': instance.name, 'id': instance.id, 'comment': instance.comment,
                                 'authed': instance.authed, 'modified': lastMod})
    if table == 'Session':
        session_instance = db.session.query(SessionFiles).filter_by(id=id).first()
        if session_instance != None:
            names = session_instance.authed.split(',')
            for name in names:
                user = db.session.query(User).filter_by(id=name).first()
                sessionUsers.insert(0, {'sUser': user})
    return render_template('admin.html', user=user, fileUsers=fileUsers, UserFiles=UserFiles,
                           userSessions=userSessions, sessionUsers=sessionUsers, freeze=freeze)


@a.route('/addThing', methods=['GET', 'POST'])
@login_required
def addThing():
    '''
    Helper method for the /admin page used to add something to the user/file/session database.

    This is done by taking the ID of something that already exists in the database and updating the authentication list.
    :return:
    '''
    if request.method == 'POST':
        thing = request.form.get('id', type=str)
        location = request.form.get('from', type=str)
        table = request.form.get('table', type=str)
        user = request.form.get('user', type=str)
        if thing != None:
            user = db.session.query(User).filter_by(username=location).first()
            if table == '#userFileTable':
                instance = db.session.query(DataFile).filter_by(id=thing).first()
                auths = instance.authed.split(',')
                if user.id in auths:
                    return 'Already Shared'
                else:
                    instance.authed = instance.authed + ',' + str(user.id)
                    userFile = UserFiles()
                    userFile.user_id = user.id
                    userFile.file_id = instance.id
                    db.session.add(userFile)
                    db.session.commit()
            if table == '#userSessionTable':
                instance = db.session.query(SessionFiles).filter_by(id=thing).first()
                auths = instance.authed.split(',')
                if user.id in auths:
                    return 'Already Shared'
                else:
                    instance.authed = instance.authed + ',' + str(user.id)
        else:
            user = db.session.query(User).filter_by(username=user).first()
            if table == '#fileNameTable':
                instance = db.session.query(DataFile).filter_by(id=location).first()
                auths = instance.authed.split(',')
                if user.id in auths:
                    return 'Already Shared'
                else:
                    instance.authed = instance.authed + ',' + str(user.id)
                    userFile = UserFiles()
                    userFile.user_id = user.id
                    userFile.file_id = instance.id
                    db.session.add(userFile)
                    db.session.commit()
            if table == '#sessionUserTable':
                instance = db.session.query(SessionFiles).filter_by(id=location).first()
                auths = instance.authed.split(',')
                if user.id in auths:
                    return 'Already Shared'
                else:
                    instance.authed = instance.authed + ',' + str(user.id)
        db.session.commit()
        user = user.username
    return user


@a.route('/removeThing', methods=['GET', 'POST'])
@login_required
def removeThing():
    '''
    Updates the user/file/session database with a deletion as requested by the admin page

    This is done by getting information from a request and deleting the appropriate thing from the authentication list.
    If this changes leaves the authentication list empty then the thing is deleted from the database.
    :return:
    '''
    if request.method == 'POST':
        thing = request.form.get('id', type=str)
        location = request.form.get('from', type=str)
        table = request.form.get('table', type=str)
        user = request.form.get('user', type=str)
        if thing != None:
            user = db.session.query(User).filter_by(username=location).first()
            if table == '#userFileTable':
                instance = db.session.query(DataFile).filter_by(id=thing).first()
                auths = instance.authed.split(',')
                auths.remove(str(user.id))
                userFile = db.session.query(UserFiles).filter(
                    and_(UserFiles.user_id == user.id, UserFiles.file_id == instance.id)).first()
                db.session.delete(userFile)
                db.session.commit()
                if len(auths) == 0:
                    db.session.delete(instance)
                else:
                    instance.authed = ','.join(auths)
            if table == '#userSessionTable':
                instance = db.session.query(SessionFiles).filter_by(id=thing).first()
                auths = instance.authed.split(',')
                auths.remove(str(user.id))
                if len(auths) == 0:
                    db.session.delete(instance)
                    instances = db.session.query(SessionFilesMeta).filter_by(sessionFiles_id=thing).all()
                    for instance in instances:
                        meta = db.session.query(SessionMeta).filter_by(id=instance.sessionMeta_id).first()
                        db.session.delete(meta)
                        db.session.delete(instance)
                else:
                    instance.authed = ','.join(auths)
            if table == 'HRM':
                user = db.session.query(User).filter_by(id=current_user.get_id()).first()
                instance = db.session.query(HRM).filter_by(id=thing).first()
                if instance.name == 'Fe-inline-1meV':
                    return "Request to delete base HRM denied"
                db.session.delete(instance)
        else:
            user = db.session.query(User).filter_by(username=user).first()
            if table == '#fileNameTable':
                file_instance = db.session.query(DataFile).filter_by(id=location).first()
                auths = file_instance.authed.split(',')
                auths.remove(str(user.id))
                userFile = db.session.query(UserFiles).filter(
                    and_(UserFiles.user_id == user.id, UserFiles.file_id == file_instance.id)).first()
                db.session.delete(userFile)
                db.session.commit()
                if len(auths) == 0:
                    db.session.delete(file_instance)
                else:
                    file_instance.authed = ','.join(auths)
            if table == '#sessionUserTable':
                session_instance = db.session.query(SessionFiles).filter_by(id=location).first()
                auths = session_instance.authed.split(',')
                auths.remove(str(user.id))
                if len(auths) == 0:
                    db.session.delete(session_instance)
                    instances = db.session.query(SessionFilesMeta).filter_by(sessionFiles_id=thing).all()
                    for instance in instances:
                        meta = db.session.query(SessionMeta).filter_by(id=instance.sessionMeta_id).first()
                        db.session.delete(meta)
                        db.session.delete(instance)
                else:
                    session_instance.authed = ','.join(auths)
        db.session.commit()
        user = user.username
    return user
