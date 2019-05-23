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

from flask import Blueprint, render_template, request
import matplotlib

from utilities.file_utility import FileUtility
from utilities.graphing_utility import GraphingUtility

matplotlib.use('Agg')
from flask_login import current_user, login_required
from db.db_model import db, logBook, dataFile, currentMeta
import json
from sqlalchemy import desc, and_


logbookApp = Blueprint('logbook', __name__)

@logbookApp.route('/del_entry', methods=['GET', 'POST'])
@login_required
def delete_entry():
	'''
    Simple delete function for the logbook.

    This function handles both mass deletion and singular deletion from the logbook.

    *Should probably be moved to within /delete*
    :return:
    '''
	user = current_user
	if request.method == 'POST':
		idthis = request.form.get('id', type=int)
		if idthis == -1:
			userBook = db.session.query(logBook).filter_by(user=user)
			for instance in userBook:
				db.session.delete(instance)
		else:
			instance = db.session.query(logBook).filter_by(id=idthis).first()
			db.session.delete(instance)
		db.session.commit()
	return 'Deleted'


@logbookApp.route('/add_entry', methods=['GET', 'POST'])
@login_required
def add_entry():
	'''
    Adds an entry to the logbook.

    This function handles standard logging from the format page and the logs from the sum page.
    Data is pulled from the user's currentMeta to log relevant information to the table.
    :return:
    '''
	user = current_user
	if request.method == 'POST':
		process = request.form.get('process', type=int)
		if process != None:
			meta = logBook()
			meta.user = user
			meta.plot = db.session.query(logBook).filter_by(name="Process Entry").first().plot
			files = []
			for instance in db.session.query(currentMeta).filter(currentMeta.user == current_user).all():
				fintance = db.session.query(dataFile).filter_by(id=instance.file_id).first()
				files.append(fintance.name)
			files = json.dumps(files)
			meta.name = files
			meta.timestamp = FileUtility.getTime()
			meta.session = current_user.current_session
			db.session.add(meta)
			db.session.commit()
			return 'Added'
		idthis = request.form.get('id', type=int)
		file_instance = db.session.query(dataFile).filter_by(id=idthis).first()
		format_instance = db.session.query(currentMeta).filter(and_(currentMeta.user_id == current_user.get_id(),
		                                                            currentMeta.file_id == file_instance.id,
		                                                            currentMeta.session == current_user.current_session)).first()
		if format_instance != None:
			form = GraphingUtility.populate_from_instance(format_instance)
			meta = logBook()
			form.populate_obj(meta)
			meta.user = user
			meta.plot = format_instance.plot
			meta.comment = format_instance.comment
			meta.name = file_instance.name
			meta.timestamp = FileUtility.getTime()
			meta.session = current_user.current_session
			db.session.add(meta)
			db.session.commit()
	return 'Added'

@logbookApp.route('/db')
@login_required
def sesData():
	'''
    Template generator for the logbook page.

    Queries the database of the loggedUser to get all instances of plots they have logged.
    :return:
    '''
	data = []
	user = current_user
	if user.is_authenticated():
		procEntry = db.session.query(logBook).filter_by(name="Process Entry").first()
		if procEntry != None:
			db.session.delete(procEntry)
			db.session.commit()
		instances = user.loggedUser.order_by(desc('id'))
		for instance in instances:
			form = GraphingUtility.populate_from_instance(instance)
			columns, bools = GraphingUtility.splitForm(form)
			plot = instance.plot
			if instance.comment:
				comment = instance.comment
			else:
				comment = ''
			try:
				json.loads(instance.name)
				data.append({'plot': plot, 'comment': comment, 'name': instance.name, 'time': instance.timestamp,
				             'ses': instance.session, 'id': instance.id})
			except ValueError:
				data.append({'form': form, 'plot': plot, 'id': instance.id, 'comment': comment, 'columns': columns,
				             'bools': bools, 'name': instance.name, 'time': instance.timestamp,
				             'ses': instance.session})
	return render_template("logbook.html", data=data)