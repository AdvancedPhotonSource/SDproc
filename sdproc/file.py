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
import os
from datetime import datetime
from operator import and_

import globus_sdk
from flask import Blueprint, render_template, url_for, request, send_from_directory
from flask_login import login_required, current_user
from globusonline.transfer.api_client import get_access_token, TransferAPIClient
from werkzeug.utils import redirect, secure_filename

from db.db_model import User, sessionFiles, db, currentMeta, dataFile, userFiles, \
    sessionFilesMeta, sessionMeta
from flask_app import app
from utilities.file_utility import FileUtility

from sqlalchemy import desc

fileApp = Blueprint('file', __name__)
ALLOWED_EXTENSIONS = {'txt', 'mda', 'dat'}

CLIENT_ID = '0c5f2ef9-7898-4d24-bdbf-57c3f1a2b4ea'
globusClient = None

@fileApp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    '''
    Template generator method for the upload page.

    Sends all files in a template for the user to use so long as they are authenticated.

    this is done with a database query and authenticated in upload.html.
    :return:
    '''
    user = current_user
    data = []
    files = dataFile.query.order_by(desc('id'))
    names = db.session.query(User)
    for instance in files:
        fsize = FileUtility.size(instance.path)
        lastMod = FileUtility.modified(instance.path)
        temp = lastMod.strftime("%d/%m/%Y %H:%M:%S")
        modname = [instance.name + temp]
        if instance.type == 'dat' and instance.name[-4:] != '.dat':
            instance.name = instance.name + '.dat'
        data.insert(0, {'name': instance.name, 'path': instance.path, 'id': instance.id, 'comment': instance.comment,
                        'authed': instance.authed, 'size': fsize, 'modified': lastMod, 'modname': modname})
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('upload.html', data=data, user=user, names=names)


'''The beginning of methods for file structure'''
@fileApp.route("/jsonData", methods=["GET","POST"])
def data():
    data = []
    currentUser = current_user.get_id()

    if currentUser == 1:
        nodes = dataFile.query.all()
    else:
        nodes = dataFile.query.filter_by(authed=currentUser)

    for node in nodes:
        id = node.id
        title = node.name
        parent = node.parentID
        type = node.treeType

        if parent == 0:
            data.append({ "text" : title, "id" : id, "parent" : "#", "type" : type, "state" : { "opened" : "true", "disabled" : "true" } })
        else:
            data.append({"text": title, "id": id, "parent": parent, "type" : type})

    with open('static/someD4.json', 'w') as outfile:
        json.dump(data, outfile)

    return json.dumps(data)


@fileApp.route("/scans_data", methods=["GET","POST"])
def scans_data():
    data = []
    currentUser = current_user.get_id()

    if currentUser == 1:
        nodes = dataFile.query.all()
    else:
        nodes = dataFile.query.filter_by(authed=currentUser)

    for node in nodes:
        id = node.id
        title = node.name
        parent = node.parentID
        type = node.treeType
        file_type = node.type

        if file_type == "mda" or file_type == "txt" or file_type == "":
            if parent == 0:
                data.append({"text": title, "id": id, "parent": "#", "type": type, "state": {"opened": "true", "disabled": "true"}})
            elif type == "Folder":
                data.append({"text": title, "id": id, "parent": parent, "type": type, "state": {"disabled": "true"}})
            else:
                data.append({"text": title, "id": id, "parent": parent, "type" : type})

    with open('static/scans_data.json', 'w') as outfile:
        json.dump(data, outfile)

    return json.dumps(data)


@fileApp.route("/createNode", methods=["GET","POST"])
def create():
    parent = request.form.get("parent")
    title = request.form.get("title")

    node = dataFile(name=title, path="", comment="This is a folder.", authed=current_user.get_id(), comChar="", type="", parentID=parent, treeType="Folder")

    db.session.add(node)
    db.session.commit()
    return "Done"



@fileApp.route("/renameN", methods=["GET", "POST"])
def rename():
    node = request.form.get("node")
    newName = request.form.get("newName")

    if "j" in node:
        node = dataFile.query.order_by(desc('id')).first()
        node.name = newName
    else:
        currNode = dataFile.query.filter_by(id=node).first()
        currNode.name = newName

    db.session.commit()
    return "done"


@fileApp.route("/moveNode", methods=["GET", "POST"])
def move():
    parent = request.form.get("parent")
    node = request.form.get("node")
    print parent;
    print node;

    currNode = dataFile.query.filter_by(id=node).first()

    currNode.parentID = parent
    db.session.commit()
    return "done"


@fileApp.route("/deleteNode", methods=["GET", "POST"])
def delete():
    node = request.form.get("node")

    currNode = dataFile.query.filter_by(id=node).first()

    if currNode.treeType == "File":
        db.session.delete(currNode)
    else:
        recursive(currNode.id)
        db.session.delete(currNode)

    db.session.commit()
    return "done"


@fileApp.route("/recursiveNode", methods=["GET", "POST"])
def recursive(parentID):
    nodes = dataFile.query.filter_by(parentID=parentID)
    for node in nodes:
        if node.treeType == "File":
            db.session.delete(node)
        else:
            recursive(node.id)
            db.session.delete(node)

    return "done"


@fileApp.route("/show_NewComment", methods=["GET", "POST"])
def newC():
    id = request.form.get("id")
    node = dataFile.query.filter_by(id=id).first()
    nodecomment = node.comment
    return nodecomment


@fileApp.route("/saveNC", methods=["GET", "POST"])
def sc():
    id = request.form.get("id")
    newcomment = request.form.get("comment")
    node = dataFile.query.filter_by(id=id).first()
    node.comment = newcomment
    db.session.commit()
    return "done"


'''The end of methods for file structure'''


@fileApp.route('/linkGlobus', methods=['GET', 'POST'])
@login_required
def linkGlobus():
    '''
    client = globus_sdk.NativeAppAuthClient(CLIENT_ID)
    #client.oauth2_start_flow(refresh_tokens=True)
    client.oauth2_start_flow()
    authorize_url = client.oauth2_get_authorize_url()
    print('Please go to this URL and login: {0}'.format(authorize_url))
    get_input = getattr(__builtins__, 'raw_input', input)
    auth_code = get_input('Please enter the code you get after login here: ').strip()
    token_response = client.oauth2_exchange_code_for_tokens(auth_code)
    globus_auth_data = token_response.by_resource_server['auth.globus.org']
    globus_transfer_data = token_response.by_resource_server['transfer.api.globus.org']
    AUTH_TOKEN = globus_auth_data['access_token']
    TRANSFER_TOKEN = globus_transfer_data['access_token']
    TRANSFER_REFRESH = globus_transfer_data['refresh_token']
    TRANSFER_EXP = globus_transfer_data['expires_at_seconds']
    #authorizer = globus_sdk.RefreshTokenAuthorizer(TRANSFER_REFRESH, client, access_token=TRANSFER_TOKEN, expires_at=TRANSFER_EXP)
    authorizer = globus_sdk.AccessTokenAuthorizer(access_token=TRANSFER_TOKEN)
    tc = globus_sdk.TransferClient(authorizer=authorizer)
    petrel = 'e890db9e-8182-11e5-993f-22000b96db58'
    ep = tc.get_endpoint(petrel)
    epResult = tc.endpoint_autoactivate(petrel)
    r = tc.operation_ls(petrel, path='/')
    for item in r:
        print("{}: {} [{}]".format(item["type"], item["name"], item["size"]))
    return 'Linked'
    '''
    '''
    api = getApi('caschmitz', 'password')
    print api.endpoint_ls('petrel#sdm')
    code, reason, result = api.endpoint_autoactivate('petrel#sdm', if_expires_in=600)
    print code, reason, result
    code, message, data = api.transfer_submission_id()
    print code, message, data
    submission_id = data['value']
    t = Transfer(submission_id, "petrel#sdm", "petrel#sdm")
    t.add_item("/test/testfile.txt", "/test/col/dir1/testfile01")
    code, reason, data = api.transfer(t)
    task_id = data['task_id']
    print "TASK_ID: ", task_id
    for i in range(0, 10):
        code, reason, data = api.task(task_id, fields="status")
        status = data["status"]
        print "STATUS: ", status
        time.sleep(10)
    '''
    global globusClient
    globusClient = globus_sdk.NativeAppAuthClient(CLIENT_ID)
    globusClient.oauth2_start_flow()
    authorize_url = globusClient.oauth2_get_authorize_url()
    return format(authorize_url)


@fileApp.route('/connectGlobus', methods=['GET', 'POST'])
@login_required
def connectGlobus():
    authID = request.form.get('authURL')
    token_response = globusClient.oauth2_exchange_code_for_tokens(authID)
    globus_transfer_data = token_response.by_resource_server['transfer.api.globus.org']
    authorizer = globus_sdk.AccessTokenAuthorizer(access_token=globus_transfer_data['access_token'])
    tc = globus_sdk.TransferClient(authorizer=authorizer)
    extrepid = '9c9cb97e-de86-11e6-9d15-22000a1e3b52'
    ep = tc.get_endpoint(extrepid)
    r = tc.operation_ls(extrepid, path='/gdata/dm')
    for item in r:
        print("{}: {} [{}]".format(item["type"], item["name"], item["size"]))

    # Setup for actually transferring files
    '''
    local_ep = globus_sdk.LocalGlobusConnectPersonal()
    local_ep_id = local_ep.endpoint_id
    tdata = globus_sdk.TransferData(tc, ep.endpoint_id, local_ep_id)
    searchPath = "/test"
    for file in searchPath:
        tdata.add_item(file, app.config['UPLOAD_DIR'] + '/rawData')
    tc.submit_transfer(tdata)


    r = tc.operation_ls(petrel, path='/test')
    for item in r:
        print("{}: {} [{}]".format(item["type"], item["name"], item["size"]))
    '''

    return 'Connected'


def getApi(username, password):
    goAuthTuple = get_access_token(username=username, password=password)
    api = TransferAPIClient(goAuthTuple.usernmae, goauth=goAuthTuple.token)
    return api

@fileApp.route('/updateSumCheck', methods=['GET', 'POST'])
@login_required
def updateSumCheck():
    '''
    Updates the current meta to keep track of the checkbox associated with adding the file to the sum.
    :return:
    '''
    idthis = request.form.get('id', type=int)
    checkVal = request.form.get('check').lower() == "true"
    format_instance = db.session.query(currentMeta).filter(and_(currentMeta.user_id == current_user.get_id(),
                                                                currentMeta.file_id == idthis,
                                                                currentMeta.session == current_user.current_session)).first()
    format_instance.checked = checkVal
    db.session.commit()
    return 'Updated'


@fileApp.route('/headerFile', methods=['GET', 'POST'])
@login_required
def headerFile():
    idthis = request.form.get('id', type=int)
    file_instance = db.session.query(dataFile).filter_by(id=idthis).first()
    header = FileUtility.getHeader(file_instance.name, file_instance.path)
    return json.dumps(header)








@fileApp.route('/delete', methods=['GET', 'POST'])
@login_required
def delete_file():
    '''
    General delete function that is used for deleting entries from the database.

    Files, metadata, sessions, and users are all deleted in this function.
    The authentication list is updated if there are still users that need to have access to the session/file after a deletion is made.
    :return:
    '''
    if request.method == 'POST':
        idnum = request.form.get('id', type=int)
        delUser = request.form.get('delUser', type=str)
        table = request.form.get('table', type=str)
        user = current_user
        if table == 'File':
            instance = db.session.query(dataFile).filter_by(id=idnum).first()
            auths = instance.authed.split(',')
            auths.remove(str(user.id))
            temp = db.session.query(userFiles).all()
            userFile = db.session.query(userFiles).filter(
                and_(userFiles.user_id == user.id, userFiles.file_id == instance.id)).first()
            db.session.delete(userFile)
            db.session.commit()
            if len(auths) == 0:
                db.session.delete(instance)
            else:
                instance.authed = ','.join(auths)
        if table == 'Meta':
            instance = user.logBook.filter_by(id=idnum).first()
            db.session.delete(instance)
        if table == 'Session':
            instance = db.session.query(sessionFiles).filter_by(id=idnum).first()
            auths = instance.authed.split(',')
            auths.remove(str(user.id))
            if len(auths) == 0:
                db.session.delete(instance)
                instances = db.session.query(sessionFilesMeta).filter_by(sessionFiles_id=idnum).all()
                for instance in instances:
                    meta = db.session.query(sessionMeta).filter_by(id=instance.sessionMeta_id).first()
                    db.session.delete(meta)
                    db.session.delete(instance)
            else:
                instance.authed = ','.join(auths)
        if table == 'User':
            user_instance = db.session.query(User).filter_by(username=delUser).first()
            sessions = db.session.query(sessionFiles).filter(sessionFiles.user_id == user_instance.id).all()
            for session in sessions:
                auths = session.authed.split(',')
                auths.remove(str(user_instance.id))
                if len(auths) == 0:
                    db.session.delete(session)
                    instances = db.session.query(sessionFilesMeta).filter_by(sessionFiles_id=session.id).all()
                    for instance in instances:
                        meta = db.session.query(sessionMeta).filter_by(id=instance.sessionMeta_id).first()
                        db.session.delete(meta)
                        db.session.delete(instance)
                else:
                    session.authed = ','.join(auths)
            fileIDs = db.session.query(userFiles).filter(userFiles.user_id == user_instance.id).all()
            for id in fileIDs:
                file = db.session.query(dataFile).filter(dataFile.id == id.file_id).first()
                auths = file.authed.split(',')
                auths.remove(str(user_instance.id))
                userFile = db.session.query(userFiles).filter(
                    and_(userFiles.user_id == user_instance.id, userFiles.file_id == file.id)).first()
                db.session.delete(userFile)
                if len(auths) == 0:
                    db.session.delete(file)
                else:
                    file.authed = ','.join(auths)
            db.session.delete(user_instance)
        db.session.commit()
    return 'Deleted'

@fileApp.route('/addf', methods=['POST'])
@login_required
def addFile():
    '''
    Adds a file to the manage file page based on a file that the user selects from their local machine.

    Files are restricted to the extensions defined in ALLOWED_EXTENSIONS.  Usage of the for loop allows the user to
        shift/control click multiple files to upload simultaneously.
    After upload the files are stored in UPLOAD_DIR/rawData so that the server has its own copy to reference.
    :return:
    '''
    if request.method == 'POST':
        temp1 = request.files.listvalues()
        for file in temp1:
            file = file[0]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                pathfilename = filename + str(datetime.now())
                file.save(os.path.join((app.config['UPLOAD_DIR'] + '/rawData'), pathfilename))
                dfile = dataFile()
                dfile.name = filename
                if dfile.name[-4:] == '.dat':
                    dfile.name = dfile.name[:-4]
                sideVals = request.form.listvalues()
                dfile.comChar = sideVals[0][0]
                dfile.type = sideVals[1][0]
                dfile.path = app.config['UPLOAD_DIR'] + '/rawData/' + pathfilename
                dfile.comment = ''
                dfile.authed = current_user.get_id()
                currUser = db.session.query(User).filter(User.id == current_user.get_id()).first().username
                parentNode = db.session.query(dataFile).filter(and_(dataFile.name == "/" + currUser + "/", dataFile.authed == str(current_user.get_id()))).first()
                dfile.parentID = parentNode.id
                dfile.treeType = "File"
                db.session.add(dfile)
                db.session.commit()
                userFile = userFiles()
                userFile.file_id = dfile.id
                userFile.user_id = current_user.get_id()
                db.session.add(userFile)
                db.session.commit()
    return 'Added'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@fileApp.route('/outData/<path:filename>/<displayName>', methods=['GET', 'POST'])
@login_required
def sendOut(filename, displayName):
    '''
    Sends the file to the user for doanloading using flask's send_from_directory
    :param filename:
    The absolute name of the file that is saved in the database.
    :param displayName:
    The simplistic name of the file that the user chose.
    :return:
    '''
    if displayName != 'None' and displayName is not None:
        return send_from_directory(directory=app.config['UPLOAD_DIR'] + '/outData', filename=filename,
                                   as_attachment=True, attachment_filename=displayName + '.dat')
    else:
        return send_from_directory(directory=app.config['UPLOAD_DIR'] + '/outData', filename=filename,
                                   as_attachment=True)