__author__ = 'caschmitz'
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
'''
For debugging server use:
    try:
        *line you want to test*
    except Exception,e:
        print(str(e))
'''

# TODO: Ask Nicholas for information on xtrepid UUID and giving permissions to Michael
# TODO: Subdirectories to file structure and make them searchable within the program
# TODO: Split comments from fileComments and sessionComments on Scans Tab
# TODO: Have fileComments searchable on manageFiles and sessionComments searchable on selectSession
# TODO: Make script to restart server

from flask import redirect,request
from flask_login import LoginManager
from flask_app import app
from db.api.user_db_api import UserDbApi

from sdproc.user import userApp
from sdproc.hrm import hrmApp
from sdproc.sdproc import sdprocApp
from sdproc.logbook import logbookApp
from sdproc.comment import commentApp
from sdproc.file import fileApp

login_manager = LoginManager()
login_manager.init_app(app)

userDbApi = UserDbApi()

app.register_blueprint(sdprocApp)
app.register_blueprint(userApp)
app.register_blueprint(hrmApp)
app.register_blueprint(logbookApp)
app.register_blueprint(fileApp)
app.register_blueprint(commentApp)

""" REMOVE THIS ON SERVER """
@app.before_request
def fixURL():
	url = request.path
	if 'SDproc' in url:
		fixedUrl = url[7:]
		return redirect(fixedUrl, 307)
	return

@login_manager.user_loader
def load_user(user_id):
	return userDbApi.getUserById(user_id)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5001, debug=True)
