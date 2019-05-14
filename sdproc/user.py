'''
-    Copyright (c) UChicago Argonne, LLC. All rights reserved.
-
-    Copyright UChicago Argonne, LLC. This software was produced
-    under U.S. Government contract DE-AC02-06CH11357 for Argonne National
-    Laboratory (ANL), which is operated by UChicago Argonne, LLC for the
-    U.S. Department of Energy. The U.S. Government has rights to use,
-    reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR
-    UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR
-    ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is
-    modified to produce derivative works, such modified software should
-    be clearly marked, so as not to confuse it with the version available
-    from ANL.
-
-    Additionally, redistribution and use in source and binary forms, with
-    or without modification, are permitted provided that the following
-    conditions are met:
-
-        * Redistributions of source code must retain the above copyright
-          notice, this list of conditions and the following disclaimer.
-
-        * Redistributions in binary form must reproduce the above copyright
-          notice, this list of conditions and the following disclaimer in
-          the documentation and/or other materials provided with the
-          distribution.
-
-        * Neither the name of UChicago Argonne, LLC, Argonne National
-          Laboratory, ANL, the U.S. Government, nor the names of its
-          contributors may be used to endorse or promote products derived
-          from this software without specific prior written permission.
-
-    THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS
-    AS IS AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
-    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
-    FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago
-    Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
-    INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
-    BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
-    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
-    CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
-    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
-    ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
-    POSSIBILITY OF SUCH DAMAGE.
'''
import json
from datetime import datetime
from sqlalchemy import and_

from flask import Blueprint, render_template, url_for, request, flash, session
from flask_login import login_required, login_user, current_user
from werkzeug.utils import redirect

from db.db_model import User, sessionFiles, notification, db, currentMeta, dataFile, HRM, currentDAT, userFiles, \
    sessionFilesMeta, sessionMeta
from forms.login_form import LoginForm
# from sdproc.sessions.routes import clear_cmeta

from forms.register_form import RegisterForm
from utilities.file_utility import FileUtility
from db.api.file_db_api import FileDbApi
from utilities.graphing_utility import GraphingUtility

userApp = Blueprint('user', __name__)
fileApi = FileDbApi()


# @userApp.route('/', methods=['GET', 'POST'])
# def toLogin():
#     '''Ensures users will be redirected to login page even without /login'''
#     return redirect(url_for('user.login'))


@userApp.route('/reg', methods=['GET', 'POST'])
def register():
    '''
    Template generator method for the register page.

     Accepts register form, creates baseline user, sends notification to admin requesting account approval.
     :return:
    '''
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User()
        form.populate_obj(user)
        strength = user.is_strong_pass(form.password.data)
        if strength['password_ok']:
            user.set_password(form.password.data)
            user.approved = 0
            user.isAdmin = 0

            db.session.add(user)

            notif = notification()
            notif.originUser = user.username
            notif.type = 'Create Account'
            notif.timestamp = datetime.now()

            db.session.add(notif)

            db.session.commit()

            return redirect(url_for('user.login'))
        else:
            for key, value in strength.iteritems():
                if value:
                    flash(key)
    return render_template('register.html', form=form)


# @userApp.route('/login', methods=['GET', 'POST'])
# def login():
#     '''
#     Template generator method for the login page
#
#     Accepts login form and ensure that the user has permission to login.
#
#     This is done by using Flask's builtin login_user after checking that the user is approved in the database
#     :return:
#     '''
#     if current_user.is_authenticated:
#         return redirect(url_for('sdproc.index'))
#     form = LoginForm(request.form)
#     if request.method == 'POST' and form.validate():
#         user = form.get_user()
#         # user.approved = 1
#         # user.isAdmin = 1
#         if user.approved == 1:
#             login_user(user)
#             clear_cmeta()
#             clear_rowa_wrapper()
#             current_user.current_session = "None"
#             db.session.commit()
#             return redirect(url_for('sdproc.index'))
#         elif user.approved == 2:
#             refusePrompt = "Your account has been frozen"
#             return render_template('login_form.html', form=form, session=session, refusePrompt=refusePrompt)
#         elif user.approved == 0:
#             refusePrompt = "Wait for an admin to approve your account"
#             return render_template('login_form.html', form=form, session=session, refusePrompt=refusePrompt)
#         else:
#             flash('Login sucks', 'danger')
#     return render_template('login_form.html', form=form, session=session)


@userApp.route('/logout')
@login_required
def logout():
    # Logs out a user by clearing session information
    session.clear()
    return redirect(url_for('user.login'))


@userApp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    '''
    Template generator method for the profile page.

    Sends information on the current user and their notifications as template.

    This is done by querying respective databases.
    :return:
    '''
    notifData = []
    thisProfile = []

    thisProfile.insert(0, {'username': current_user.username, 'email': current_user.email,
                           'fullName': current_user.fullName, 'institution': current_user.institution, 'password': '',
                           'commentChar': current_user.commentChar})

    # notifications = notification.query.order_by('id')
    # for instance in notifications:
    #    userInfo = db.session.query(User).filter_by(username=instance.originUser).first()
    #    if userInfo != None:
    #        notifData.insert(0, {'id': instance.id, 'name': instance.originUser, 'time': instance.timestamp,
    #                             'type': instance.type, 'username': userInfo.username, 'email': userInfo.email,
    #                             'fullName': userInfo.fullName, 'institution': userInfo.institution,
    #                             'reason': userInfo.reason})
    return render_template('profile.html', user=current_user, notifications=notifData, userProf=thisProfile)


@userApp.route('/updateProf', methods=['GET', 'POST'])
@login_required
def updateProf():
    '''
    Updates the current user's profile in the database with any new information they may have added.

    This is done by accepting request information (AJAX generally) and updating the User database accordingly
    :return:
    '''
    user_instance = db.session.query(User).filter_by(username=current_user.username).first()
    comChar = request.form.get('comChar', type=str)
    password = request.form.get('pass', type=str)
    email = request.form.get('email', type=str)

    if comChar != '0':
        user_instance.commentChar = comChar
    if password != '0':
        user_instance.set_password(password)
    if email != '0':
        user_instance.email = email
    db.session.commit()
    return 'Updated'


@userApp.route('/admin', methods=['GET', 'POST'])
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
    sessions = sessionFiles.query.all()
    for instance in sessions:
        lastMod = instance.last_used
        sesData.insert(0, {'name': instance.name, 'id': instance.id, 'comment': instance.comment,
                           'authed': instance.authed,
                           'modified': lastMod})
    files = dataFile.query.order_by('id')
    for instance in files:
        fsize = FileUtility.size(instance.path)
        lastMod = FileUtility.modified(instance.path)
        temp = lastMod.strftime("%d/%m/%Y %H:%M:%S")
        modname = [instance.name + temp]
        fileData.insert(0,
                        {'name': instance.name, 'path': instance.path, 'id': instance.id, 'comment': instance.comment,
                         'authed': instance.authed, 'size': fsize, 'modified': lastMod, 'modname': modname})

    notifications = notification.query.order_by('id')
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


@userApp.route('/freeze', methods=['GET', 'POST'])
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


# @userApp.route('/clear_cmeta', methods=['GET', 'POST'])
# @login_required
# def clear_cmeta():
#     '''
#     Function that clears the current user's currentMeta Table.
#
#     This is usually called when starting a new session or resuming an old one so that prexisting data does not cause conflicts.
#     :return:
#     '''
#     current_user.current_session = 'None'
#     deleting = db.session.query(currentMeta).filter(currentMeta.user_id == current_user.get_id()).all()
#     for i in deleting:
#         db.session.delete(i)
#     deleting = db.session.query(currentDAT).filter(currentDAT.user_id == current_user.get_id()).all()
#     for i in deleting:
#         db.session.delete(i)
#     db.session.commit()
#     return 'Cleared'


@userApp.route('/clearPart_cmeta', methods=['GET', 'POST'])
@login_required
def clearPart_cmeta():
    '''
    Function that deletes a single file from the current users currentMeta table.

    This is called when removing a file on the format page.
    :return:
    '''
    idthis = request.form.get('id', type=int)
    deleting = db.session.query(currentMeta).filter(and_(currentMeta.user_id == current_user.get_id(),
                                                         currentMeta.file_id == idthis,
                                                         currentMeta.session == current_user.current_session)).first()
    db.session.delete(deleting)
    db.session.commit()
    temp = db.session.query(currentMeta).all()
    return 'Cleared'


@userApp.route('/clear_rowa', methods=['GET', 'POST'])
@login_required
def clear_rowa_wrapper():
    '''Simple function to clear the run_once_with_args decorator for loading the base comments of files.'''
    fileApi.setBaseComment(-1, current_user.get_id(), current_user.current_session)
    return 'Cleared'


@userApp.route('/notifInfo', methods=['GET', 'POST'])
@login_required
def notifInfo():
    '''
    Supplementary template generator method for admin.

    Provides additional information about a notification.

    This is done by querying the sqlite database 'notification' based on the ID given.
    :return:
    '''
    notifID = request.form.get('id', type=int)
    notifInfo = db.session.query(notification).filter_by(id=notifID).first()
    userInfo = db.session.query(User).filter_by(username=notifInfo.originUser).first()
    userData = {'username': userInfo.username, 'email': userInfo.email,
                'fullName': userInfo.fullName, 'institution': userInfo.institution,
                'reason': userInfo.reason}
    return render_template('admin.html', user=current_user, userProf=userData)


# @userApp.route('/shareSes', methods=['GET', 'POST'])
# @login_required
# def shareSes():
#     '''
#     Shares a session with another user.
#
#     Similar to the admin sharing feature, but for users.
#
#     *Should probably be implemented with other sharing features*
#     :return:
#     '''
#     idthis = request.form.get('id', type=int)
#     shareUser = request.form.get('toUser', type=str)
#     type = request.form.get('type', type=str)
#     thisUser = db.session.query(User).filter_by(username=shareUser).first()
#     toAuth = thisUser.id
#     if type == 'dat':
#         dat_instance = db.session.query(dataFile).filter_by(id=idthis).first()
#         auths = dat_instance.authed.split(',')
#         if toAuth in auths:
#             return 'Already Shared'
#         else:
#             dat_instance.authed = dat_instance.authed + ',' + str(toAuth)
#             userFile = userFiles()
#             userFile.file_id = idthis
#             userFile.user_id = thisUser.id
#             db.session.add(userFile)
#             db.session.commit()
#     else:
#         session_instance = db.session.query(sessionFiles).filter_by(id=idthis).first()
#         auths = session_instance.authed.split(',')
#         if toAuth in auths:
#             return 'Already Shared'
#         else:
#             session_instance.authed = session_instance.authed + ',' + str(toAuth)
#             db.session.commit()
#     return 'Shared'


@userApp.route('/shareFile', methods=['GET', 'POST'])
@login_required
def shareFile():
    '''
    Shares a file with another user.

    Similar to the admin sharing feature, but for users.

    *Should probably be implemented with other sharing features*
    :return:
    '''
    idthis = request.form.get('id', type=int)
    shareUser = request.form.get('toUser', type=str)
    thisUser = db.session.query(User).filter_by(username=shareUser).first()
    toAuth = thisUser.id
    file_instance = db.session.query(dataFile).filter_by(id=idthis).first()
    auths = file_instance.authed.split(',')
    if toAuth in auths:
        return 'Already Shared'
    else:
        file_instance.authed = file_instance.authed + ',' + str(toAuth)
        userFile = userFiles()
        userFile.file_id = idthis
        userFile.user_id = thisUser.id
        db.session.add(userFile)
        db.session.commit()
    return 'Shared'


# @userApp.route('/set_ses', methods=['GET', 'POST'])
# @login_required
# def set_ses():
#     '''
#     Function that updates currentMeta/currentDAT based on which type of session is selected by the user.
#
#     By setting these tables the user is then able to view/alter the information on the corresponding tabs.
#     :return:
#     '''
#     if request.method == 'POST':
#         files = []
#         sesID = request.form.get('id', type=int)
#         type = request.form.get('type', type=str)
#         if type == 'dat':
#             dat = db.session.query(dataFile).filter_by(id=sesID).first()
#             with open(dat.path, 'r') as DATfile:
#                 data = DATfile.read()
#                 cDAT = currentDAT()
#                 cDAT.user = current_user
#                 cDAT.file_id = dat.id
#                 xs = []
#                 ys = []
#                 user = db.session.query(User).filter_by(username=current_user.username).first()
#                 data = data.split("\n")
#                 try:
#                     data = [x for x in data if not x.startswith(user.commentChar)]
#                 except TypeError:
#                     data = [x for x in data if not x.startswith('#')]
#                     flash('No comment preference set, defaulting to #')
#                 for i in data:
#                     if not i:
#                         continue
#                     line = i.split()
#                     xs.append(float(line[0]))
#                     ys.append(float(line[1]))
#                 DAT = [xs, ys]
#                 DAT = json.dumps(DAT)
#                 cDAT.DAT = DAT
#                 cDAT.originDAT = DAT
#                 if dat.name is not None:
#                     cDAT.DATname = dat.name
#                 db.session.add(cDAT)
#                 db.session.commit()
#             return 'Saved'
#         allSes = db.session.query(sessionFiles).filter_by(id=sesID).first()
#         metas = db.session.query(sessionFilesMeta).filter_by(sessionFiles_id=sesID).all()
#         for meta in metas:
#             actualMeta = db.session.query(sessionMeta).filter_by(id=meta.sessionMeta_id).first()
#             form = GraphingUtility.populate_from_instance(actualMeta)
#             newCurrent = currentMeta()
#             form.populate_obj(newCurrent)
#             newCurrent.path = actualMeta.path
#             newCurrent.comment = actualMeta.comment
#             newCurrent.checked = actualMeta.checked
#             newCurrent.against_E = actualMeta.against_E
#             newCurrent.file_id = actualMeta.file_id
#             newCurrent.fit_type = actualMeta.fit_type
#             newCurrent.fit_pos = actualMeta.fit_pos
#             newCurrent.fit_range = actualMeta.fit_range
#             newCurrent.hrm = actualMeta.hrm
#             newCurrent.user = current_user
#             newCurrent.session = allSes.name
#             db.session.add(newCurrent)
#             db.session.commit()
#             files.append(newCurrent.file_id)
#         current_user.current_session = allSes.name
#         db.session.commit()
#         data = json.dumps(files)
#         return data
#     return 'Set'


# @userApp.route('/save_ses', methods=['GET', 'POST'])
# @login_required
# def saveSession():
#     '''
#     This saves the current session so that the user may resume from the select page whenever they want.
#
#     The currentMeta table is parsed and saved into the sessionFiles and sessionFilesMeta tables for more permanence.
#     A check is done to ensure that the user cannot save the session under a name that has already been created.
#     :return:
#     '''
#     checked = request.form.get("checked", type=int)
#     namechk = request.form.get("name", type=str)
#     if checked == 0:
#         instance = db.session.query(sessionFiles).filter(
#             and_(sessionFiles.user_id == current_user.get_id(), sessionFiles.name == namechk)).first()
#         if instance:
#             data = str(instance.id)
#             return data
#
#     session_file = sessionFiles()
#     session_file.user = current_user
#     session_file.user_id == current_user.get_id()
#     session_file.authed = current_user.get_id()
#     session_file.name = request.form.get("name", type=str)
#     session_file.comment = request.form.get("comment", type=str)
#     session_file.last_used = FileUtility.getTime()
#     db.session.add(session_file)
#     db.session.commit()
#
#     for instance in db.session.query(currentMeta).filter(currentMeta.user_id == current_user.get_id()).all():
#         form = GraphingUtility.populate_from_instance(instance)
#         session_instance = sessionMeta()
#         form.populate_obj(session_instance)
#
#         session_instance.file_id = instance.file_id
#         session_instance.path = instance.path
#         session_instance.comment = instance.comment
#         session_instance.checked = instance.checked
#         session_instance.against_E = instance.against_E
#         session_instance.fit_type = instance.fit_type
#         session_instance.fit_pos = instance.fit_pos
#         session_instance.fit_range = instance.fit_range
#         session_instance.hrm = instance.hrm
#         session_instance.session = session_file.name
#         db.session.add(session_instance)
#         db.session.commit()
#
#         session_file_instance = sessionFilesMeta()
#         session_file_instance.sessionFiles_id = session_file.id
#         session_file_instance.sessionMeta_id = session_instance.id
#
#         instance.session = session_file.name
#
#         db.session.add(session_file_instance)
#         db.session.commit()
#     current_user.current_session = session_file.name
#     db.session.commit()
#     if checked == 1:
#         return current_user.current_session
#     data = ({'status': 'Saved', 'name': current_user.current_session})
#     sending = json.dumps(data)
#     return sending


@userApp.route('/solveNotif', methods=['GET', 'POST'])
@login_required
def solveNotif():
    '''
    Resolves a notification based on the action taken.

    This is done by updating the User based on if they were accepted or not.

    Only currently setup to handle account creation requests.
    :return:
    '''
    id = request.form.get('id', type=int)
    action = request.form.get('action', type=int)
    notif = db.session.query(notification).filter_by(id=id).first()
    if action == 1:
        user = db.session.query(User).filter_by(username=notif.originUser).first()
        user.approved = 1
        username = user.username
        id = user.id
        rootnode = dataFile(name="/" + username + "/", path="", comment="This is the root node", authed=str(id),
                            comChar="", type="", parentID=0, treeType="Root")
        db.session.add(rootnode)
        db.session.delete(notif)
    else:
        db.session.delete(notif)
        user = db.session.query(User).filter_by(username=notif.originUser).first()
        db.session.delete(user)
        sessions = db.session.query(sessionFiles).filter(sessionFiles.user == user).all()
        for session in sessions:
            auths = session.authed.split(',')
            auths.remove(str(user.id))
            if len(auths) == 0:
                db.session.delete(session)
                instances = db.session.query(sessionFilesMeta).filter_by(sessionFiles_id=session.id).all()
                for instance in instances:
                    meta = db.session.query(sessionMeta).filter_by(id=instance.sessionMeta_id).first()
                    db.session.delete(meta)
                    db.session.deleta(instance)
            else:
                session.authed = ','.join(auths)
        fileIDs = db.session.query(userFiles).filter(userFiles.user_id == user.id).all()
        for id in fileIDs:
            file = db.session.query(dataFile).filter(dataFile.id == id.file_id).first()
            auths = file.authed.split(',')
            auths.remove(str(user.id))
            userFile = db.session.query(userFiles).filter(
                and_(userFiles.user_id == user.id, userFiles.file_id == file.id)).first()
            db.session.delete(userFile)
            if len(auths) == 0:
                db.session.delete(file)
            else:
                file.authed = ','.join(auths)
    db.session.commit()
    return 'Solved'


@userApp.route('/getInfo', methods=['GET', 'POST'])
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
    userFiles = []
    userSessions = []
    sessionUsers = []
    freeze = 0
    if table == 'File':
        file_instance = db.session.query(dataFile).filter_by(id=id).first()
        if file_instance != None:
            names = file_instance.authed.split(',')
            for name in names:
                user = db.session.query(User).filter_by(id=name).first()
                fileUsers.insert(0, {'fUser': user})
    if table == 'User':
        user = db.session.query(User).filter_by(username=user).first()
        freeze = user.approved
        files = dataFile.query.all()
        for instance in files:
            fsize = FileUtility.size(instance.path)
            lastMod = FileUtility.modified(instance.path)
            temp = lastMod.strftime("%d/%m/%Y %H:%M:%S")
            modname = [instance.name + temp]
            userFiles.insert(0,
                             {'name': instance.name, 'path': instance.path, 'id': instance.id,
                              'comment': instance.comment,
                              'authed': instance.authed, 'size': fsize, 'modified': lastMod, 'modname': modname})

        sessions = sessionFiles.query.all()
        for instance in sessions:
            lastMod = instance.last_used
            userSessions.insert(0,
                                {'name': instance.name, 'id': instance.id, 'comment': instance.comment,
                                 'authed': instance.authed, 'modified': lastMod})
    if table == 'Session':
        session_instance = db.session.query(sessionFiles).filter_by(id=id).first()
        if session_instance != None:
            names = session_instance.authed.split(',')
            for name in names:
                user = db.session.query(User).filter_by(id=name).first()
                sessionUsers.insert(0, {'sUser': user})
    return render_template('admin.html', user=user, fileUsers=fileUsers, userFiles=userFiles,
                           userSessions=userSessions, sessionUsers=sessionUsers, freeze=freeze)


@userApp.route('/addThing', methods=['GET', 'POST'])
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
                instance = db.session.query(dataFile).filter_by(id=thing).first()
                auths = instance.authed.split(',')
                if user.id in auths:
                    return 'Already Shared'
                else:
                    instance.authed = instance.authed + ',' + str(user.id)
                    userFile = userFiles()
                    userFile.user_id = user.id
                    userFile.file_id = instance.id
                    db.session.add(userFile)
                    db.session.commit()
            if table == '#userSessionTable':
                instance = db.session.query(sessionFiles).filter_by(id=thing).first()
                auths = instance.authed.split(',')
                if user.id in auths:
                    return 'Already Shared'
                else:
                    instance.authed = instance.authed + ',' + str(user.id)
        else:
            user = db.session.query(User).filter_by(username=user).first()
            if table == '#fileNameTable':
                instance = db.session.query(dataFile).filter_by(id=location).first()
                auths = instance.authed.split(',')
                if user.id in auths:
                    return 'Already Shared'
                else:
                    instance.authed = instance.authed + ',' + str(user.id)
                    userFile = userFiles()
                    userFile.user_id = user.id
                    userFile.file_id = instance.id
                    db.session.add(userFile)
                    db.session.commit()
            if table == '#sessionUserTable':
                instance = db.session.query(sessionFiles).filter_by(id=location).first()
                auths = instance.authed.split(',')
                if user.id in auths:
                    return 'Already Shared'
                else:
                    instance.authed = instance.authed + ',' + str(user.id)
        db.session.commit()
        user = user.username
    return user


@userApp.route('/removeThing', methods=['GET', 'POST'])
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
                instance = db.session.query(dataFile).filter_by(id=thing).first()
                auths = instance.authed.split(',')
                auths.remove(str(user.id))
                userFile = db.session.query(userFiles).filter(
                    and_(userFiles.user_id == user.id, userFiles.file_id == instance.id)).first()
                db.session.delete(userFile)
                db.session.commit()
                if len(auths) == 0:
                    db.session.delete(instance)
                else:
                    instance.authed = ','.join(auths)
            if table == '#userSessionTable':
                instance = db.session.query(sessionFiles).filter_by(id=thing).first()
                auths = instance.authed.split(',')
                auths.remove(str(user.id))
                if len(auths) == 0:
                    db.session.delete(instance)
                    instances = db.session.query(sessionFilesMeta).filter_by(sessionFiles_id=thing).all()
                    for instance in instances:
                        meta = db.session.query(sessionMeta).filter_by(id=instance.sessionMeta_id).first()
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
                file_instance = db.session.query(dataFile).filter_by(id=location).first()
                auths = file_instance.authed.split(',')
                auths.remove(str(user.id))
                userFile = db.session.query(userFiles).filter(
                    and_(userFiles.user_id == user.id, userFiles.file_id == file_instance.id)).first()
                db.session.delete(userFile)
                db.session.commit()
                if len(auths) == 0:
                    db.session.delete(file_instance)
                else:
                    file_instance.authed = ','.join(auths)
            if table == '#sessionUserTable':
                session_instance = db.session.query(sessionFiles).filter_by(id=location).first()
                auths = session_instance.authed.split(',')
                auths.remove(str(user.id))
                if len(auths) == 0:
                    db.session.delete(session_instance)
                    instances = db.session.query(sessionFilesMeta).filter_by(sessionFiles_id=thing).all()
                    for instance in instances:
                        meta = db.session.query(sessionMeta).filter_by(id=instance.sessionMeta_id).first()
                        db.session.delete(meta)
                        db.session.delete(instance)
                else:
                    session_instance.authed = ','.join(auths)
        db.session.commit()
        user = user.username
    return user
