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
from flask import redirect, request
from flask_login import LoginManager
from flask_app import app
from db.api.user_db_api import UserDbApi

from sdproc.hrm import hrmApp
from sdproc.logbook import logbookApp
from sdproc.sessions.routes import sessions
from sdproc.files.routes import files
from sdproc.users.routes import users
from sdproc.admin.routes import a
from sdproc.hrms.routes import hrms
from sdproc.dm.routes import dm

'''
For debugging server use:
    try:
        *line you want to test*
    except Exception,e:
        print(str(e))
'''

# TODO: Fix Output behaviours
""" 
Make output button on Scans tab prompt for file name instead of default
Add a pull down menu or a way to see all the files in the /static/saved_files directory, and select a name,
then modify or not up to user. User should be able to just type in a file name too
"""
# TODO: Fix 'Peak at Point' and 'Fit around Point' options on Scans tab


login_manager = LoginManager()
login_manager.login_view = 'users.login2'
login_manager.login_message_category = 'info'
login_manager.init_app(app)

userDbApi = UserDbApi()

app.register_blueprint(hrmApp)
app.register_blueprint(logbookApp)
app.register_blueprint(sessions)
app.register_blueprint(files)
app.register_blueprint(users)
app.register_blueprint(a)
app.register_blueprint(hrms)
app.register_blueprint(dm)


""" REMOVE THIS ON SERVER - BEGIN """


@app.before_request
def fixURL():
    url = request.path
    if 'SDproc' in url:
        fixedUrl = url[7:]
        return redirect(fixedUrl, 307)
    return


""" END """


@login_manager.user_loader
def load_user(user_id):
    return userDbApi.getUserById(user_id)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
