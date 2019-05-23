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

from flask import Blueprint, request
from flask_login import login_required, current_user
from sqlalchemy import and_

from db.api.file_db_api import FileDbApi
from db.db_model import sessionFiles, db, currentMeta, dataFile, currentDAT

commentApp = Blueprint('comment', __name__)

fileApi = FileDbApi()

@commentApp.route('/show_comment', methods=['GET', 'POST'])
@login_required
def show_comment():
    '''
    General function that is called when showing any comment.

    This function is usually called when a user selects something that has a comment associated with it.
    Similar to save_comment this function is used for all types of comments.
    :return:
    '''
    if request.method == 'POST':
        send_comment = ''
        idnext = request.form.get('idnext', type=int)
        formatting = request.form.get('format', type=int)
        usingSes = request.form.get('ses', type=int)
        if idnext is not None and formatting is None:
            instance = db.session.query(dataFile).filter_by(id=idnext).first()
            if instance is not None:
                send_comment = instance.comment
        if idnext is not None and formatting == 1:
            if usingSes != 1:
                fileApi.setBaseComment(idnext, current_user.get_id(), current_user.current_session)
            instance = db.session.query(dataFile).filter_by(id=idnext).first()
            format_instance = db.session.query(currentMeta).filter(and_(currentMeta.user_id == current_user.get_id(),
                                                                        currentMeta.file_id == instance.id,
                                                                        currentMeta.session == current_user.current_session)).first()
            if format_instance is None:
                send_comment = instance.comment
            elif format_instance.comment is not None:
                send_comment = format_instance.comment
            else:
                fileApi.setBaseComment(idnext, current_user.get_id(), current_user.current_session)
                instance = db.session.query(dataFile).filter_by(id=idnext).first()
                format_instance = db.session.query(currentMeta).filter(
                    and_(currentMeta.user_id == current_user.get_id(),
                         currentMeta.file_id == instance.id,
                         currentMeta.session == current_user.current_session)).first()
                send_comment = format_instance.comment
        if idnext is not None and formatting == 2:
            instance = db.session.query(sessionFiles).filter_by(id=idnext).first()
            if instance is not None:
                send_comment = instance.comment
        if formatting == 3:
            DAT = db.session.query(currentDAT).filter(currentDAT.user == current_user).first()
            instance = db.session.query(dataFile).filter_by(id=DAT.file_id).first()
            if instance is not None:
                send_comment = instance.comment
        return send_comment
    return 'Holder'


@commentApp.route('/make_name', methods=['GET', 'POST'])
@login_required
def make_name():
    '''
    This function takes a file by id and returns the name assigned to it.

    This is needed as otherwise the entire filename would be displayed to users with the extensive datetime at the end.
    :return:
    '''
    if request.method == 'POST':
        idthis = request.form.get('id', type=int)
        idlist = json.loads(request.form.get('ids', type=str))
        if idthis:
            instance = db.session.query(dataFile).filter_by(id=idthis).first()

            format_instance = db.session.query(currentMeta).filter(and_(currentMeta.user_id == current_user.get_id(),
                                                                        currentMeta.file_id == instance.id,
                                                                        currentMeta.session == current_user.current_session)).first()
            return json.dumps([instance.name, format_instance.checked])
        else:
            names = []
            for id in idlist:
                instance = db.session.query(dataFile).filter_by(id=id).first()
                temp = db.session.query(currentMeta).all()
                format_instance = db.session.query(currentMeta).filter(and_(currentMeta.user_id == current_user.get_id(),
                         currentMeta.file_id == instance.id,
                         currentMeta.session == current_user.current_session)).first()
                names.append([instance.name, format_instance.checked, id])
            return json.dumps(names)
    return 'Made'

@commentApp.route('/save_comment', methods=['GET', 'POST'])
@login_required
def save_comment():
    '''
    General function that is called when saving any type of comment.

    Session comments, file comments, and DAT comments are all saved here.  Generally this function is called upon navigating away from the comment box.

    ***There is currently the issue that if a user is commenting a shared file/session while a different user also
    commenting the same shared file/session the comment that is saved belongs to the user that navigated away last.
    Not sure hot to fix this issue without an immense amount of work.***
    :return:
    '''
    if request.method == 'POST':
        comment = request.form.get('comment', type=str)
        idprev = request.form.get('idprev', type=int)
        formatting = request.form.get('format', type=int)
        if idprev is not None and formatting is None:
            instance = db.session.query(dataFile).filter_by(id=idprev).first()
            instance.comment = comment
            db.session.commit()
        elif idprev is not None and formatting == 1:
            instance = db.session.query(dataFile).filter_by(id=idprev).first()
            format_instance = db.session.query(currentMeta).filter(and_(currentMeta.user_id == current_user.get_id(),
                                                                        currentMeta.file_id == instance.id,
                                                                        currentMeta.session == current_user.current_session)).first()
            if format_instance is None:
                instance.comment = comment
            else:
                format_instance.comment = comment
            db.session.commit()
        elif idprev is not None and formatting == 2:
            instance = db.session.query(sessionFiles).filter_by(id=idprev).first()
            instance.comment = comment
            db.session.commit()
        elif formatting == 3:
            DAT = db.session.query(currentDAT).filter(currentDAT.user == current_user).first()
            instance = db.session.query(dataFile).filter_by(id=DAT.file_id).first()
            if instance is not None:
                instance.comment = comment
                db.session.commit()
    return 'Saved'