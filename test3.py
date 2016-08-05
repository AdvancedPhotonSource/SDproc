__author__ = 'caschmitz'

from flask import Flask, render_template, request, session, redirect, url_for, escape, redirect, make_response, flash
import matplotlib.pyplot as plt
import mpld3
import os
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from app import app
from db_model import db, User, logBook, dataFile, currentMeta, sessionMeta, sessionFiles, sessionFilesMeta
from forms import InputForm, CommentForm
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import math
import numpy
import uuid
from sqlalchemy import desc
import mda

login_manager = LoginManager()
login_manager.init_app(app)
ALLOWED_EXTENSIONS = {'txt', 'mda'}
usedArgs = []
current_session = 'None'


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


@app.route('/reg', methods=['GET', 'POST'])
def register():
    from forms import register_form
    form = register_form(request.form)
    if request.method == 'POST' and form.validate():
        user = User()
        form.populate_obj(user)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    from forms import login_form
    form = login_form(request.form)
    if request.method == 'POST' and form.validate():
        user = form.get_user()
        login_user(user)
        clear_cmeta()
        clear_rowa_wrapper()
        return redirect(url_for('index'))
    return render_template('login_form.html', form=form, session=session)


@app.route('/select', methods=['GET', 'POST'])
@login_required
def index():
    user = current_user
    data = []
    sessions = sessionFiles.query.all()
    names = db.session.query(User)
    for instance in sessions:
        lastMod = instance.last_used
        data.insert(0,
                    {'name': instance.name, 'id': instance.id, 'comment': instance.comment, 'authed': instance.authed,
                     'modified': lastMod})
    if request.method == 'POST':
        return redirect(url_for('dataFormat'))
    return render_template('view_output.html', data=data, user=user, names=names)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    user = current_user
    data = []
    files = dataFile.query.order_by('id')
    names = db.session.query(User)
    for instance in files:
        fsize = size(instance.path)
        lastMod = modified(instance.path)
        temp = lastMod.strftime("%d/%m/%Y %H:%M:%S")
        modname = [instance.name + temp]
        data.insert(0, {'name': instance.name, 'path': instance.path, 'id': instance.id, 'comment': instance.comment,
                        'authed': instance.authed, 'size': fsize, 'modified': lastMod, 'modname': modname})
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('upload.html', data=data, user=user, names=names)


@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/data', methods=['GET', 'POST'])
@login_required
def dataFormat():
    user = current_user
    global current_session
    thisSession = current_session
    findPlot = request.form.get('plot', type=int)
    fdata = []
    nameID = str(uuid.uuid4())
    userID = str(user.get_id())
    files = dataFile.query.filter_by(authed=userID)
    for instance in files:
        fsize = size(instance.path)
        lastMod = modified(instance.path)
        temp = lastMod.strftime("%d/%m/%Y %H:%M:%S")
        modname = [instance.name + temp]
        fdata.insert(0, {'name': instance.name, 'path': instance.path, 'id': instance.id, 'comment': instance.comment,
                         'authed': instance.authed, 'size': fsize, 'modified': lastMod, 'modname': modname})

    if findPlot != 1:
        form = InputForm(request.form)
        plt.figure(figsize=(10, 7))
        fig, ax = plt.subplots()
        mpld3.plugins.connect(fig, InteractiveLegend([], [], 0, nameID, None))
        code = mpld3.fig_to_html(fig)
        plt.clf()
        againstE = False
    else:
        idthis = request.form.get('idnext', type=int)
        file_instance = db.session.query(dataFile).filter_by(id=idthis).first()
        try:
            fpath = file_instance.path
        except AttributeError:
            flash('Please select a file')
            return redirect(url_for('dataFormat'))

        format_instance = db.session.query(currentMeta).filter_by(path=fpath).first()
        if format_instance is not None:
            againstE = format_instance.against_E
            form = populate_from_instance(format_instance)
            columns, bools = splitForm(form)
            used = []
            additional = []
            addLabels = []
            normLabels = []
            labels = []
            if str(file_instance.type) == 'mda':
                data, name, unusedpath = readMda(file_instance.path)
            else:
                data, name, unusedpath = readMdaAscii(file_instance.path)
            etype = data[columns[0].data - 1]
            for i in range(len(bools)):
                if bools[i].data:
                    if columns[i].data == None:
                        if i == 1:
                            energy = energy_xtal(data, unicode_to_int(columns[3].data - 1),
                                                 unicode_to_int(columns[4].data - 1), format_instance.hrm)
                            additional.append(energy)
                            addLabels.append('Energy')
                            etype = energy
                        elif i == 2:
                            energy = energy_xtal_temp(data, unicode_to_int(columns[3].data - 1),
                                                      unicode_to_int(columns[4].data - 1),
                                                      unicode_to_int(columns[5].data - 1),
                                                      unicode_to_int(columns[6].data - 1), format_instance.hrm)
                            additional.append(energy)
                            addLabels.append('Energy')
                            etype = energy
                        elif i == 7:
                            energy = temp_corr(data, unicode_to_int(columns[5].data - 1),
                                               unicode_to_int(columns[6].data - 1), format_instance.hrm)
                            additional.append(energy)
                            addLabels.append('Energy')
                        elif i == 9:
                            signal = signal_normalized(data, unicode_to_int(columns[8].data - 1),
                                                       unicode_to_int(columns[10].data - 1))
                            additional.append(signal)
                            addLabels.append('Signal')
                        else:
                            norm = norm_factors(data, unicode_to_int(columns[10].data - 1))
                            additional.append(norm)
                            addLabels.append('Normalized')
                        continue
                    else:
                        used.append(unicode_to_int(columns[i].data))
                        normLabels.append(str(columns[i].label.text)[:-2])
            labels.append(normLabels)
            labels.append(addLabels)
            code = plotData(data, used, againstE, additional, labels, etype)
            format_instance.plot = code
            db.session.commit()
        else:
            if str(file_instance.type) == 'mda':
                data, name, unusedpath = readMda(file_instance.path)
            else:
                data, name, unusedpath = readMdaAscii(file_instance.path)
            etype = data[1]
            used = []
            againstE = False
            format = currentMeta()
            format.name = file_instance.name
            format.path = file_instance.path
            # format.ebool = True
            format.sbool = True
            format.energy = 1
            format.signal = 11
            format.xtal1A = 2
            format.xtal2A = 3
            format.xtal1T = 12
            format.xtal2T = 15
            format.norm = 7
            format.extra = 1
            format.against_E = False
            format.fit_type = 'AtMax'
            format.fit_pos = 0
            format.fit_range = 3
            format.file_id = idthis
            format.hrm = '++'

            # used.append(1)
            used.append(11)
            labels = []
            labels.append(['Signal'])
            code = plotData(data, used, False, None, labels, etype)
            format.plot = code
            db.session.add(format)
            db.session.commit()

            code = format.plot
            form = populate_from_instance(format)
    return render_template("data_format.html", user=user, code=code, form=form, againstE=againstE, data=fdata,
                           ses=thisSession)


@app.route('/save_graph', methods=['GET', 'POST'])
@login_required
def save_graph():
    form = InputForm(request.form)
    idthis = request.form.get("idnum", type=int)
    if idthis is not None:
        againstE = request.form.get("agaE", type=str)
        if againstE == 'true' or againstE == 'True':
            againstE = True
        elif againstE == 'false' or againstE == 'False':
            againstE = False
        else:
            print(againstE)
        file_instance = db.session.query(dataFile).filter_by(id=idthis).first()

        format_instance = db.session.query(currentMeta).filter_by(file_id=file_instance.id).first()

        format_instance.energy = form.energy.data
        format_instance.xtal1A = form.xtal1A.data
        format_instance.xtal2A = form.xtal2A.data
        format_instance.xtal1T = form.xtal1T.data
        format_instance.xtal2T = form.xtal2T.data
        format_instance.signal = form.signal.data
        format_instance.norm = form.norm.data
        format_instance.extra = form.extra.data

        format_instance.ebool = form.ebool.data
        format_instance.ecbool = form.ecbool.data
        format_instance.etcbool = form.etcbool.data
        format_instance.a1bool = form.a1bool.data
        format_instance.a2bool = form.a2bool.data
        format_instance.t1bool = form.t1bool.data
        format_instance.t2bool = form.t2bool.data
        format_instance.tcbool = form.tcbool.data
        format_instance.xtal1A = form.xtal1A.data
        format_instance.sbool = form.sbool.data
        format_instance.snbool = form.snbool.data
        format_instance.nbool = form.nbool.data
        format_instance.nfbool = form.nfbool.data
        format_instance.xbool = form.xbool.data
        format_instance.user = current_user
        format_instance.against_E = againstE

        db.session.commit()
    return 'Saved'


@app.route('/save_ses', methods=['GET', 'POST'])
@login_required
def saveSession():
    checked = request.form.get("checked", type=int)
    namechk = request.form.get("name", type=str)
    if checked == 0:
        instance = db.session.query(sessionFiles).filter_by(name=namechk).first()
        if instance:
            data = str(instance.id)
            return data

    session_file = sessionFiles()
    session_file.user = current_user
    session_file.authed = current_user.get_id()
    session_file.name = request.form.get("name", type=str)
    session_file.comment = request.form.get("comment", type=str)
    session_file.last_used = getTime()
    db.session.add(session_file)
    db.session.commit()

    for instance in db.session.query(currentMeta):
        form = populate_from_instance(instance)
        session_instance = sessionMeta()
        form.populate_obj(session_instance)

        session_instance.file_id = instance.file_id
        session_instance.path = instance.path
        session_instance.comment = instance.comment
        session_instance.against_E = instance.against_E
        session_instance.fit_type = instance.fit_type
        session_instance.fit_pos = instance.fit_pos
        session_instance.fit_range = instance.fit_range
        db.session.add(session_instance)
        db.session.commit()

        session_file_instance = sessionFilesMeta()
        session_file_instance.sessionFiles_id = session_file.id
        session_file_instance.sessionMeta_id = session_instance.id

        db.session.add(session_file_instance)
        db.session.commit()
    global current_session
    current_session = session_file.name
    if checked == 1:
        return current_session
    data = ({'status': 'Saved', 'name': current_session})
    sending = json.dumps(data)
    return sending


@app.route('/db')
@login_required
def sesData():
    data = []
    user = current_user
    if user.is_authenticated():
        procEntry = db.session.query(logBook).filter_by(name="Process Entry").first()
        if procEntry != None:
            db.session.delete(procEntry)
            db.session.commit()
        instances = user.loggedUser.order_by(desc('id'))
        for instance in instances:
            form = populate_from_instance(instance)
            columns, bools = splitForm(form)
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
    return render_template("session.html", data=data)


@app.route('/addf', methods=['POST'])
@login_required
def addFile():
    if request.method == 'POST':
        temp1 = request.files.listvalues()
        for file in temp1:
            file = file[0]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                pathfilename = filename + str(datetime.now())
                file.save(os.path.join(app.config['UPLOAD_DIR'], pathfilename))
                dfile = dataFile()
                dfile.name = filename
                sideVals = request.form.listvalues()
                dfile.delim = sideVals[0][0]
                dfile.type = sideVals[1][0]
                dfile.path = '/home/phoebus/CASCHMITZ/Desktop/dataDir/' + pathfilename
                dfile.comment = ''
                dfile.authed = current_user.get_id()
                db.session.add(dfile)
                db.session.commit()
    return 'Added'


@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete_file():
    if request.method == 'POST':
        idnum = request.form.get('id', type=int)
        table = request.form.get('table', type=str)
        user = current_user
        if table == 'File':
            instance = db.session.query(dataFile).filter_by(id=idnum).first()
            auths = instance.authed.split(',')
            auths.remove(str(user.id))
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
        db.session.commit()
    return 'Deleted'


@app.route('/save_comment', methods=['GET', 'POST'])
@login_required
def save_comment():
    if request.method == 'POST':
        comment = request.form.get('comment', type=str)
        idprev = request.form.get('idprev', type=int)
        formatting = request.form.get('format', type=int)
        if idprev is not None and formatting is None:
            instance = db.session.query(dataFile).filter_by(id=idprev).first()
            instance.comment = comment
            db.session.commit()
        if idprev is not None and formatting == 1:
            instance = db.session.query(dataFile).filter_by(id=idprev).first()
            format_instance = db.session.query(currentMeta).filter_by(path=instance.path).first()
            format_instance.comment = comment
            db.session.commit()
        if idprev is not None and formatting == 2:
            instance = db.session.query(sessionFiles).filter_by(id=idprev).first()
            instance.comment = comment
            db.session.commit()
    return 'Saved'


@app.route('/show_comment', methods=['GET', 'POST'])
@login_required
def show_comment():
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
                setBaseComment(idnext)
            instance = db.session.query(dataFile).filter_by(id=idnext).first()
            format_instance = db.session.query(currentMeta).filter_by(file_id=instance.id).first()
            if format_instance.comment is not None:
                send_comment = format_instance.comment
            else:
                setBaseComment(idnext)
                instance = db.session.query(dataFile).filter_by(id=idnext).first()
                format_instance = db.session.query(currentMeta).filter_by(file_id=instance.id).first()
                send_comment = format_instance.comment
        if idnext is not None and formatting == 2:
            instance = db.session.query(sessionFiles).filter_by(id=idnext).first()
            if instance is not None:
                send_comment = instance.comment
        return send_comment
    return 'Holder'


@app.route('/make_name', methods=['GET', 'POST'])
@login_required
def make_name():
    if request.method == 'POST':
        idthis = request.form.get('id', type=int)
        instance = db.session.query(dataFile).filter_by(id=idthis).first()
        # lastMod = modified(instance.path)
        # temp = lastMod.strftime("%Y-%m-%d %H:%M:%S")
        # modname = str(instance.name) + ' ' + temp
        return instance.name
    return 'Holder'


@app.route('/del_entry', methods=['GET', 'POST'])
@login_required
def delete_entry():
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


@app.route('/add_entry', methods=['GET', 'POST'])
@login_required
def add_entry():
    user = current_user
    if request.method == 'POST':
        process = request.form.get('process', type=int)
        if process != None:
            meta = logBook()
            meta.user = user
            meta.plot = db.session.query(logBook).filter_by(name="Process Entry").first().plot
            files = []
            for instance in db.session.query(currentMeta):
                fintance = db.session.query(dataFile).filter_by(id=instance.file_id).first()
                files.append(fintance.name)
            files = json.dumps(files)
            meta.name = files
            meta.timestamp = getTime()
            meta.session = current_session
            db.session.add(meta)
            db.session.commit()
            return 'Added'
        idthis = request.form.get('id', type=int)
        file_instance = db.session.query(dataFile).filter_by(id=idthis).first()
        format_instance = db.session.query(currentMeta).filter_by(path=file_instance.path).first()
        if format_instance != None:
            form = populate_from_instance(format_instance)
            meta = logBook()
            form.populate_obj(meta)
            meta.user = user
            meta.plot = format_instance.plot
            meta.comment = format_instance.comment
            meta.name = file_instance.name
            meta.timestamp = getTime()
            meta.session = current_session
            db.session.add(meta)
            db.session.commit()
    return 'Added'


@app.route('/clear_rowa', methods=['GET', 'POST'])
@login_required
def clear_rowa_wrapper():
    setBaseComment(-1)
    return 'Cleared'


@app.route('/clear_cmeta', methods=['GET', 'POST'])
@login_required
def clear_cmeta():
    global current_session
    current_session = 'None'
    meta = db.metadata
    for table in (meta.sorted_tables):
        if table.name == 'current_meta':
            db.session.execute(table.delete())
    db.session.commit()
    return 'Cleared'


@app.route('/clearPart_cmeta', methods=['GET', 'POST'])
@login_required
def clearPart_cmeta():
    idthis = request.form.get('id', type=int)
    deleting = db.session.query(currentMeta).filter_by(file_id=idthis).first()
    db.session.delete(deleting)
    db.session.commit()
    return 'Cleared'


@app.route('/set_ses', methods=['GET', 'POST'])
@login_required
def set_ses():
    if request.method == 'POST':
        files = []
        sesID = request.form.get('id', type=int)
        metas = db.session.query(sessionFilesMeta).filter_by(sessionFiles_id=sesID).all()
        for meta in metas:
            actualMeta = db.session.query(sessionMeta).filter_by(id=meta.sessionMeta_id).first()
            form = populate_from_instance(actualMeta)
            newCurrent = currentMeta()
            form.populate_obj(newCurrent)
            newCurrent.path = actualMeta.path
            newCurrent.comment = actualMeta.comment
            newCurrent.against_E = actualMeta.against_E
            newCurrent.file_id = actualMeta.file_id
            newCurrent.fit_type = actualMeta.fit_type
            newCurrent.fit_pos = actualMeta.fit_pos
            newCurrent.fit_range = actualMeta.fit_range
            db.session.add(newCurrent)
            db.session.commit()

            files.append(newCurrent.file_id)
        global current_session
        allSes = db.session.query(sessionFiles).filter_by(id=sesID).first()
        current_session = allSes.name
        data = json.dumps(files)
        return data
    return 'Set'


@app.route('/close_plots', methods=['GET', 'POST'])
@login_required
def close_plots():
    if request.method == 'POST':
        plt.close("all")
    return 'Closed'


@app.route('/process', methods=['GET', 'POST'])
@login_required
def process():
    user = current_user
    idthis = request.form.get('idnext', type=int)
    idlist = request.form.get('idList', type=str)
    pltLeg = request.form.get('pltLeg', type=int)
    binWidth = request.form.get('binWidth', type=int)
    endmax = 'No File Selected'
    senddata = []
    allFileNames = []
    if idthis is not None or idlist is not None:
        if idlist is None:
            file_instance = db.session.query(dataFile).filter_by(id=idthis).first()
            try:
                fid = file_instance.id
            except AttributeError:
                flash('Please select a file')
                return redirect(url_for('process'))
            format_instance = db.session.query(currentMeta).filter_by(file_id=fid).first()
            againstE = format_instance.against_E
            form = populate_from_instance(format_instance)
            columns, bools = splitForm(form)
            used = []
            additional = []
            legendNames = []
            endmax = []
            allFileNames = []
            if str(file_instance.type) == 'mda':
                data, name, unusedpath = readMda(file_instance.path)
            else:
                data, name, unusedpath = readMdaAscii(file_instance.path)
            if bools[1].data:
                energy = energy_xtal(data, unicode_to_int(columns[3].data - 1), unicode_to_int(columns[4].data - 1),
                                     format_instance.hrm)
                additional.append(energy)
                legendNames.append(columns[1].id)
            elif bools[2].data:
                energy = energy_xtal_temp(data, unicode_to_int(columns[3].data - 1),
                                          unicode_to_int(columns[4].data - 1), unicode_to_int(columns[5].data - 1),
                                          unicode_to_int(columns[6].data - 1), format_instance.hrm)
                additional.append(energy)
                legendNames.append(columns[2].id)
            else:
                used.append(unicode_to_int(columns[0].data))
                legendNames.append(columns[0].id)
            if bools[9].data:
                signal = signal_normalized(data, unicode_to_int(columns[8].data - 1),
                                           unicode_to_int(columns[10].data - 1))
                additional.append(signal)
                legendNames.append(columns[9].id)
            else:
                used.append(unicode_to_int(columns[8].data))
                legendNames.append(columns[8].id)
            max, xmax, ycords = convert_Numpy(used, data, additional)
            fitType = format_instance.fit_type
            inputCord = format_instance.fit_pos
            fitRange = format_instance.fit_range
            if fitType == 'AtMax':
                temp = xmax[1]
                xmax[1] = ycords[0][xmax[1]]
                npXcords = numpy.array(ycords[0])
                center = atMax(ycords, npXcords, xmax, fitRange)
                xmax[1] = temp
                moveXcords(ycords, center)
                format_instance.fit_type = 'AtMax'
                format_instance.fit_pos = center
                format_instance.fit_range = fitRange
                db.session.commit()
            else:
                moveXcords(ycords, inputCord)
            endmax.append([format(max[0], '.6f'), format(max[1], '.6f')])
            allFileNames.append(file_instance.name)
            code = simplePlot(ycords, xmax, file_instance.name, legendNames, pltLeg, 1)
        if idthis is None:
            jidlist = json.loads(idlist)
            alldata = []
            allxmax = []
            allycords = []
            allagainstE = []
            allLegendNames = []
            allFileNames = []
            endmax = []

            for anID in jidlist:
                file_instance = db.session.query(dataFile).filter_by(id=anID).first()
                used = []
                try:
                    fid = file_instance.id
                except AttributeError:
                    flash('Unable to find file')
                    return redirect(url_for('process'))
                format_instance = db.session.query(currentMeta).filter_by(file_id=fid).first()
                againstE = format_instance.against_E
                form = populate_from_instance(format_instance)
                columns, bools = splitForm(form)
                if str(file_instance.type) == 'mda':
                    data, name, unusedpath = readMda(file_instance.path)
                else:
                    data, name, unusedpath = readMdaAscii(file_instance.path)
                if bools[1].data:
                    energy = energy_xtal(data, unicode_to_int(columns[3].data - 1), unicode_to_int(columns[4].data - 1),
                                         format_instance.hrm)
                    used.append(energy)
                elif bools[2].data:
                    energy = energy_xtal_temp(data, unicode_to_int(columns[3].data - 1),
                                              unicode_to_int(columns[4].data - 1), unicode_to_int(columns[5].data - 1),
                                              unicode_to_int(columns[6].data - 1), format_instance.hrm)
                    used.append(energy)
                else:
                    used.append(unicode_to_int(columns[0].data))
                if bools[9].data:
                    signal = signal_normalized(data, unicode_to_int(columns[8].data - 1),
                                               unicode_to_int(columns[10].data - 1))
                    used.append(signal)
                    allLegendNames.append(columns[9].id)
                else:
                    used.append(unicode_to_int(columns[8].data))
                    allLegendNames.append(columns[8].id)
                max, xmax, ycords = convert_Numpy(used, data, None)
                fitType = format_instance.fit_type
                inputCord = format_instance.fit_pos
                fitRange = format_instance.fit_range
                if fitType == 'AtMax':
                    temp = xmax[1]
                    xmax[1] = ycords[0][xmax[1]]
                    npXcords = numpy.array(ycords[0])
                    center = atMax(ycords, npXcords, xmax, fitRange)
                    xmax[1] = temp
                    moveXcords(ycords, center)
                    format_instance.fit_type = 'AtMax'
                    format_instance.fit_pos = center
                    format_instance.fit_range = fitRange
                    db.session.commit()
                else:
                    moveXcords(ycords, inputCord)
                endmax.append([format(max[0], '.6f'), format(max[1], '.6f')])
                alldata.append(data)
                allxmax.append(xmax)
                allycords.append(ycords)
                allagainstE.append(againstE)
                allFileNames.append(file_instance.name)
            if binWidth == None:
                code, sumxmax, sumymax = mergePlots(allycords, allxmax, allagainstE, alldata, allLegendNames,
                                                    allFileNames, pltLeg)
            else:
                code, sumxmax, sumymax = mergeBin(allycords, allxmax, allagainstE, alldata, allLegendNames,
                                                  allFileNames,
                                                  pltLeg, binWidth)
            endmax.append([format(sumxmax, '.6f'), format(sumymax, '.6f')])
            allFileNames.append('Summed Files')
    else:
        fig = plt.figure(figsize=(15, 10))
        code = mpld3.fig_to_html(fig)
    procEntry = db.session.query(logBook).filter_by(name="Process Entry").first()
    if procEntry != None:
        procEntry.plot = code
        db.session.commit()
    else:
        processEntry = logBook()
        processEntry.name = "Process Entry"
        processEntry.plot = code
        processEntry.user = user
        db.session.add(processEntry)
        db.session.commit()
    senddata.append({'max': endmax, 'filenames': allFileNames})
    return render_template("data_process.html", user=user, ses=current_session, code=code, data=senddata)


@app.route('/peakFit', methods=['GET', 'POST'])
@login_required
def peak_at_max():
    idthis = request.form.get('idnum', type=int)
    fitType = request.form.get('fitType', type=int)
    inputCord = request.form.get('inputCord', type=float)
    fitRange = request.form.get('inputRange', type=float)
    localRange = request.form.get('localRange', type=float)
    file_instance = db.session.query(dataFile).filter_by(id=idthis).first()
    format_instance = db.session.query(currentMeta).filter_by(file_id=idthis).first()
    if str(file_instance.type) == 'mda':
        data, name, unusedpath = readMda(file_instance.path)
    else:
        data, name, unusedpath = readMdaAscii(file_instance.path)
    form = populate_from_instance(format_instance)
    columns, bools = splitForm(form)
    used = []
    additional = []
    legendNames = []
    if bools[1].data:
        energy = energy_xtal(data, unicode_to_int(columns[3].data - 1),
                             unicode_to_int(columns[4].data - 1), format_instance.hrm)
        additional.append(energy)
        legendNames.append(columns[1].id)
    elif bools[2].data:
        energy = energy_xtal_temp(data, unicode_to_int(columns[3].data - 1),
                                  unicode_to_int(columns[4].data - 1), unicode_to_int(columns[5].data - 1),
                                  unicode_to_int(columns[6].data - 1), format_instance.hrm)
        additional.append(energy)
        legendNames.append(columns[2].id)
    else:
        used.append(unicode_to_int(columns[0].data))
        legendNames.append(columns[0].id)
    if bools[9].data:
        signal = signal_normalized(data, unicode_to_int(columns[8].data - 1),
                                   unicode_to_int(columns[10].data - 1))
        additional.append(signal)
        legendNames.append(columns[9].id)
    else:
        used.append(unicode_to_int(columns[8].data))
        legendNames.append(columns[8].id)
    max, xmax, ycords = convert_Numpy(used, data, additional)
    npXcords = numpy.array(ycords[0])
    npYcords = numpy.array(ycords[1])
    if fitType == 0:
        leftBound = (find_nearest(npXcords, npXcords[xmax[1]] - (fitRange / 2)))
        rightBound = (find_nearest(npXcords, npXcords[xmax[1]] + (fitRange / 2)))
        targetRange = [x for x in ycords[0] if x >= leftBound]
        targetRange = [x for x in targetRange if x <= rightBound]
        npData = []
        for xcord in targetRange:
            oneCord = numpy.where(npXcords == xcord)[0][0]
            npData.append(ycords[1][oneCord])
        targetX = numpy.array(targetRange)
        targetY = numpy.array(npData)
        center = centroid(targetX, targetY)
        moveXcords(ycords, center)
        format_instance.fit_type = 'AtMax'
        format_instance.fit_pos = center
        format_instance.fit_range = fitRange
    elif fitType == 1:
        leftBound = (find_nearest(npXcords, inputCord - (fitRange / 2)))
        rightBound = (find_nearest(npXcords, inputCord + (fitRange / 2)))
        targetRange = [x for x in ycords[0] if x >= leftBound]
        targetRange = [x for x in targetRange if x <= rightBound]
        npData = []
        for xcord in targetRange:
            oneCord = numpy.where(npXcords == xcord)[0][0]
            npData.append(ycords[1][oneCord])
        targetX = numpy.array(targetRange)
        targetY = numpy.array(npData)
        center = centroid(targetX, targetY)
        moveXcords(ycords, center)
        format_instance.fit_type = 'AtPoint'
        format_instance.fit_pos = center
        format_instance.fit_range = fitRange
    else:
        leftBound = (find_nearest(npXcords, inputCord - (localRange / 2)))
        rightBound = (find_nearest(npXcords, inputCord + (localRange / 2)))
        targetRange = [x for x in ycords[0] if x >= leftBound]
        targetRange = [x for x in targetRange if x <= rightBound]
        npData = []
        for xcord in targetRange:
            oneCord = numpy.where(npXcords == xcord)[0][0]
            npData.append(ycords[1][oneCord])
        npData = numpy.array(npData)
        max = numpy.argmax(npData)
        maxIndex = numpy.where(npYcords == npData[max])[0][0]

        leftBound = (find_nearest(npXcords, npXcords[maxIndex] - (fitRange / 2)))
        rightBound = (find_nearest(npXcords, npXcords[maxIndex] + (fitRange / 2)))
        targetRange = [x for x in ycords[0] if x >= leftBound]
        targetRange = [x for x in targetRange if x <= rightBound]
        npData = []
        for xcord in targetRange:
            oneCord = numpy.where(npXcords == xcord)[0][0]
            npData.append(ycords[1][oneCord])
        targetX = numpy.array(targetRange)
        targetY = numpy.array(npData)
        center = centroid(targetX, targetY)
        moveXcords(ycords, center)
        format_instance.fit_type = 'AtPoint'
        format_instance.fit_pos = center
        format_instance.fit_range = fitRange
    db.session.commit()
    code = simplePlot(ycords, xmax, file_instance.name, legendNames, 0, 0)
    return render_template("data_format.html", user=current_user, ses=current_session, code=code, form=form)


@app.route('/updateHRM', methods=['GET', 'POST'])
@login_required
def updateHRM():
    idthis = request.form.get('idnum', type=int)
    hrm = request.form.get('hrm', type=str)
    format_instance = db.session.query(currentMeta).filter_by(file_id=idthis).first()
    format_instance.hrm = hrm
    db.session.commit()
    return 'Updated'


@app.route('/shareSes', methods=['GET', 'POST'])
@login_required
def shareSes():
    idthis = request.form.get('id', type=int)
    shareUser = request.form.get('toUser', type=str)
    thisUser = db.session.query(User).filter_by(username=shareUser).first()
    toAuth = thisUser.id
    session_instance = db.session.query(sessionFiles).filter_by(id=idthis).first()
    session_instance.authed = session_instance.authed + ',' + str(toAuth)
    db.session.commit()
    return 'Shared'


@app.route('/shareFile', methods=['GET', 'POST'])
@login_required
def shareFile():
    idthis = request.form.get('id', type=int)
    shareUser = request.form.get('toUser', type=str)
    thisUser = db.session.query(User).filter_by(username=shareUser).first()
    toAuth = thisUser.id
    file_instance = db.session.query(dataFile).filter_by(id=idthis).first()
    file_instance.authed = file_instance.authed + ',' + str(toAuth)
    db.session.commit()
    return 'Shared'


def atMax(ycords, npXcords, xmax, fitRange):
    leftBound = (find_nearest(npXcords, xmax[1] - (fitRange / 2)))
    rightBound = (find_nearest(npXcords, xmax[1] + (fitRange / 2)))
    targetRange = [x for x in ycords[0] if x >= leftBound]
    targetRange = [x for x in targetRange if x <= rightBound]
    npData = []
    for xcord in targetRange:
        oneCord = numpy.where(npXcords == xcord)[0][0]
        npData.append(ycords[1][oneCord])
    targetX = numpy.array(targetRange)
    targetY = numpy.array(npData)
    center = centroid(targetX, targetY)
    return center


def moveXcords(data, max):
    data[0] = numpy.subtract(data[0], max)
    return data


def centroid(xVals, yVals):
    top = 0
    bot = 0
    for i in range(len(xVals)):
        top = top + xVals[i] * yVals[i]
        bot = bot + yVals[i]
    shiftVal = top / bot
    return shiftVal


def unicode_to_int(unicode):
    convertI = int(unicode)
    return convertI


def splitForm(form):
    columns = []
    bools = []
    for field in form:
        if field.type == 'IntegerField':
            columns.append(field)
        else:
            bools.append(field)
    return columns, bools


def modified(path):
    """Returns modified time of this."""
    return datetime.fromtimestamp(os.path.getmtime(path))


def getTime():
    return datetime.now()


def size(path):
    """A size of this file."""
    return os.path.getsize(path)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def populate_from_instance(instance):
    form = InputForm()
    for field in form:
        try:
            field.data = getattr(instance, field.name)
        except AttributeError:
            continue
    return form


def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)

    wrapper.has_run = False
    return wrapper


def run_once_with_args(f):
    def wrapper(*args, **kwargs):
        global usedArgs
        if not args[0] in usedArgs:
            if args[0] != -1:
                usedArgs.append(*args)
                return f(*args, **kwargs)
            else:
                usedArgs = []

    return wrapper


@run_once_with_args
def setBaseComment(idnext):
    file_instance = db.session.query(dataFile).filter_by(id=idnext).first()
    format_instance = db.session.query(currentMeta).filter_by(path=file_instance.path).first()
    if format_instance is not None:
        format_instance.comment = file_instance.comment
        db.session.commit()


def find_nearest(array, value):
    idx = (numpy.abs(array - value)).argmin()
    return array[idx]


def readAscii(path):
    count = 0
    with open(path) as f:
        for line in f:
            line = line.rstrip()
            if line.startswith("%File name:"):
                path = line.split('W:', 1)[-1]
                name = path.rsplit('/', 1)[-1]
            if line.startswith("%"):
                continue
            line = line[1:]
            line = line.split("   ")
            if count == 0:
                data = [[] for x in xrange(len(line))]
            count += 1
            for i in range(len(line)):
                data[i].append(line[i])
    return data, name, path


def readMdaAscii(path):
    count = 0
    name = path.split("/")
    name = name[-1]
    with open(path) as f:
        for line in f:
            line = line.rstrip()
            if line.startswith("#"):
                continue
            if len(line) == 0:
                continue
            line = line.split(" ")
            if count == 0:
                data = [[] for x in xrange(len(line))]
            count += 1
            for i in range(len(line)):
                data[i].append(line[i])
    return data, name, path


def readMda(path):
    name = path.split("/")
    name = name[-1]
    endData = []
    mdaData = mda.readMDA(path, 1, 0, 0)
    for column in mdaData[1].p:
        endData.append(column.data)
    for column in mdaData[1].d:
        endData.append(column.data)
    return endData, name, path



def simplePlot(data, xmax, filename, linenames, legend, sized):
    plt.close()
    fig = plt.figure(figsize=(10, 7))
    css = """
    .legend-box{
        cursor: pointer;
    }
    """
    labels = []
    lines = []
    nameID = str(uuid.uuid4())
    if legend == 0:
        fig, ax = plt.subplots()
        xs = numpy.multiply(data[0], 1000000)
        ys = data[1]
        plt.plot(xs, ys)
        plt.plot(xs[xmax[1]], ys[xmax[1]], '-bD')
    else:
        fig, ax = plt.subplots()
        xs = numpy.multiply(data[0], 1000000)
        ys = data[1]
        line = ax.plot(xs, ys, alpha=0, label=filename + ' ' + linenames[0])
        lines.append(line[0])
        point = ax.plot(xs[xmax[1]], ys[xmax[1]], '-bD')
        labels.append(filename + ' ' + linenames[0])
        lines.append(point[0])

        mpld3.plugins.connect(fig, InteractiveLegend(lines, labels, sized, nameID, css))
        mpld3.plugins.connect(fig, HideLegend(nameID))
    code = mpld3.fig_to_html(fig)
    plt.close()
    return code


def mergePlots(allycords, allxmax, allagainstE, alldata, allLegendNames, allFileNames, pltLeg):
    plt.close()
    fig = plt.figure(figsize=(10, 7))
    css = """
    .legend-box{
        cursor: pointer;
    }
    """
    count1 = 0
    count2 = 0
    labels = []
    lines = []
    nameID = str(uuid.uuid4())
    if pltLeg == 0:
        for plot in alldata:
            xs = range(1, len(plot) + 1)
            ys = plot
            if allagainstE[count1]:
                xs = alldata[count1][1]
            plt.plot(xs, ys)
            plt.plot(xs[allxmax[count1][count2]], ys[allxmax[count2]], '-bD')
            count2 += 1
    else:
        fig, ax = plt.subplots()
        for oneDat in allycords:
            xs = oneDat[0]
            ys = oneDat[1]
            line = ax.plot(xs, ys, alpha=0, label=allFileNames[count1] + ' ' + allLegendNames[count1])
            lines.append(line[0])
            point = ax.plot(xs[allxmax[count1][1]], ys[allxmax[count1][1]], '-bD')
            labels.append(allFileNames[count1] + ' ' + allLegendNames[count1])
            lines.append(point[0])
            count1 += 1
        sumNumpy = []
        YVals = []
        for i in allycords:
            sumNumpy.append(i[0])
            YVals.append(i[1])
            if len(sumNumpy) == 2:
                numCat = numpy.array(sumNumpy)
                numCat[0] = numpy.array(numCat[0])
                numCat[1] = numpy.array(numCat[1])
                YVals[0] = numpy.array(YVals[0])
                YVals[1] = numpy.array(YVals[1])
                if numCat[0].size > numCat[1].size:
                    smallerx = numCat[1]
                    smallery = YVals[1]
                    largerx = numCat[0]
                    largery = YVals[0]
                else:
                    smallerx = numCat[0]
                    smallery = YVals[0]
                    largerx = numCat[1]
                    largery = YVals[1]
                smallLeft = (find_nearest(largerx, smallerx[0]))
                smallRight = (find_nearest(largerx, smallerx[-1]))
                largeLeft = (find_nearest(smallerx, largerx[0]))
                largeRight = (find_nearest(smallerx, largerx[-1]))
                smallleftPad = 0
                smallrightPad = 0
                largeleftPad = 0
                largerightPad = 0
                largeInnerX = []
                largeInnerY = []
                smallInnerX = []
                smallInnerY = []
                first = 0
                smallRightPadIndex = 'None'
                largeRightPadIndex = 'None'
                for element in largerx:
                    if element < smallLeft:
                        smallleftPad += 1
                    elif element > smallRight:
                        if first == 0:
                            smallRightPadIndex = numpy.where(largerx == element)[0][0]
                            first = 1
                        smallrightPad += 1
                    else:
                        largeInnerX.append(element)
                        atIndex = numpy.where(largerx == element)[0][0]
                        largeInnerY.append(largery[atIndex])
                first = 0
                for element in smallerx:
                    if element < largeLeft:
                        largeleftPad += 1
                    elif element > largeRight:
                        if first == 0:
                            largeRightPadIndex = numpy.where(smallerx == element)[0][0]
                            first = 1
                        largerightPad += 1
                    else:
                        smallInnerX.append(element)
                        atIndex = numpy.where(smallerx == element)[0][0]
                        smallInnerY.append(smallery[atIndex])

                smallInnerX = numpy.array(smallInnerX)
                smallInnerY = numpy.array(smallInnerY)
                largeInnerX = numpy.array(largeInnerX)
                largeInnerY = numpy.array(largeInnerY)

                if largeInnerX.size > smallInnerX.size:
                    smallInnerY = numpy.interp(largeInnerX, smallInnerX, smallInnerY)
                    adjLargex = largerx
                    if largeRightPadIndex != 'None':
                        adjSmallx = numpy.concatenate((smallerx[:largeleftPad], largeInnerX, smallerx[largeRightPadIndex:]))
                        smallery = numpy.concatenate((smallery[:largeleftPad], smallInnerY, smallery[largeRightPadIndex:]))
                    else:
                        adjSmallx = numpy.concatenate((smallerx[:largeleftPad], largeInnerX))
                        smallery = numpy.concatenate((smallery[:largeleftPad], smallInnerY))
                elif largeInnerX.size < smallInnerX.size:
                    adjSmallx = smallerx
                    largeInnerY = numpy.interp(smallInnerX, largeInnerX, largeInnerY)
                    if smallRightPadIndex != 'None':
                        adjLargex = numpy.concatenate((largerx[:smallleftPad], smallInnerX, largerx[smallRightPadIndex:]))
                        largery = numpy.concatenate((largery[:smallleftPad], largeInnerY, largery[smallRightPadIndex:]))
                    else:
                        adjLargex = numpy.concatenate((largerx[:smallleftPad], smallInnerX))
                        largery = numpy.concatenate((largery[:smallleftPad], largeInnerY))
                else:
                    if smallRightPadIndex != 'None':
                        adjLargex = numpy.concatenate((largerx[:smallleftPad], largeInnerX, largerx[smallRightPadIndex:]))
                    else:
                        adjLargex = numpy.concatenate((largerx[:smallleftPad], largeInnerX))
                    if largeRightPadIndex != 'None':
                        adjSmallx = numpy.concatenate((smallerx[:largeleftPad], largeInnerX, smallerx[largeRightPadIndex:]))
                    else:
                        adjSmallx = numpy.concatenate((smallerx[:largeleftPad], largeInnerX))

                smallPady = numpy.pad(smallery, (smallleftPad, smallrightPad), 'constant', constant_values=(0, 0))
                largePady = numpy.pad(largery, (largeleftPad, largerightPad), 'constant', constant_values=(0, 0))

                if largeRightPadIndex != 'None':
                    largePadx = numpy.concatenate((smallerx[:largeleftPad], adjLargex, smallerx[largeRightPadIndex:]))
                else:
                    largePadx = numpy.concatenate((smallerx[:largeleftPad], adjLargex))
                if smallRightPadIndex != 'None':
                    smallPadx = numpy.concatenate((largerx[:smallleftPad], adjSmallx, largerx[smallRightPadIndex:]))
                else:
                    smallPadx = numpy.concatenate((largerx[:smallleftPad], adjSmallx))

                small = numpy.array((smallPadx, smallPady))
                large = numpy.array((largePadx, largePady))
                ySummed = numpy.add(small[1], large[1])
                sum2D = numpy.array((largePadx, ySummed))
                sumNumpyStep = largePadx.tolist()
                YValsStep = ySummed.tolist()
                sumNumpy = []
                YVals = []
                sumNumpy.append(sumNumpyStep)
                YVals.append(YValsStep)

        sum2Dymax = numpy.amax(sum2D)
        sum2Dxmax = numpy.ndarray.argmax(sum2D)
        line = ax.plot(largePadx, ySummed, color='k', alpha=0, label='Sum of selected')
        lines.append(line[0])

        point = ax.plot(sum2D[0][sum2Dxmax - largePadx.size], sum2Dymax, '-bD')
        labels.append('Sum of selected')
        lines.append(point[0])
        mpld3.plugins.connect(fig, InteractiveLegend(lines, labels, 1, nameID, css))
    mpld3.plugins.connect(fig, HideLegend(nameID))
    code = mpld3.fig_to_html(fig)
    plt.close()
    return code, sum2D[0][sum2Dxmax - largePadx.size], sum2Dymax


def mergeBin(allycords, allxmax, allagainstE, alldata, allLegendNames, allFileNames, pltLeg, binWidth):
    plt.close()
    fig = plt.figure(figsize=(10, 7))
    css = """
    .legend-box{
        cursor: pointer;
    }
    """
    count1 = 0
    count2 = 0
    labels = []
    lines = []
    nameID = str(uuid.uuid4())
    if pltLeg == 0:
        for plot in alldata:
            xs = range(1, len(plot) + 1)
            ys = plot
            if allagainstE[count1]:
                xs = alldata[count1][1]
            plt.plot(xs, ys)
            plt.plot(xs[allxmax[count1][count2]], ys[allxmax[count2]], '-bD')
            count2 += 1
    else:
        fig, ax = plt.subplots()
        for oneDat in allycords:
            xs = oneDat[0]
            ys = oneDat[1]
            line = ax.plot(xs, ys, alpha=0, label=allFileNames[count1] + ' ' + allLegendNames[count1])
            lines.append(line[0])
            point = ax.plot(xs[allxmax[count1][1]], ys[allxmax[count1][1]], '-bD')
            labels.append(allFileNames[count1] + ' ' + allLegendNames[count1])
            lines.append(point[0])
            count1 += 1
        minValue = 0
        maxValue = 0
        endX = []
        endY = []
        for i in allycords:
            if i[0][0] < minValue:
                minValue = i[0][0]
            if i[0][-1] > maxValue:
                maxValue = i[0][-1]
        bins = numpy.arange(minValue, maxValue, binWidth)
        for i in range(len(allycords)):
            sumNumpy = []
            YVals = []
            endX.append([])
            endY.append([])
            binnedIdx = numpy.digitize(allycords[i][0], bins)
            resultIdx = 0
            for j in range(len(binnedIdx)):
                if j == 0:
                    YVals.append([allycords[i][1][j], binnedIdx[j], 1])
                    sumNumpy.append([allycords[i][0][j], binnedIdx[j], 1])
                    continue
                if binnedIdx[j] == binnedIdx[j - 1]:
                    YVals[resultIdx][0] += allycords[i][1][j]
                    YVals[resultIdx][2] += 1
                    sumNumpy[resultIdx][0] += allycords[i][0][j]
                    sumNumpy[resultIdx][2] += 1
                else:
                    resultIdx += 1
                    YVals.append([allycords[i][1][j], binnedIdx[j], 1])
                    sumNumpy.append([allycords[i][0][j], binnedIdx[j], 1])
            for k in range(len(sumNumpy)):
                endX[i].append([sumNumpy[k][0] / sumNumpy[k][2], sumNumpy[k][1]])
                endY[i].append([YVals[k][0] / YVals[k][2], YVals[k][1]])
        sumXvals = []
        sumYvals = []
        binIdx = 1
        for i in range(len(bins)):
            sumXvals.append(None)
            sumYvals.append(None)
            for j in range(len(endX)):
                for k in range(len(endX[j])):
                    if endX[j][k][1] == binIdx:
                        if sumXvals[binIdx - 1] == None:
                            sumXvals[binIdx - 1] = endX[j][k][0]
                            sumYvals[binIdx - 1] = endY[j][k][0]
                        else:
                            sumXvals[binIdx - 1] = (sumXvals[binIdx - 1] + endX[j][k][0]) / 2
                            sumYvals[binIdx - 1] = sumYvals[binIdx - 1] + endY[j][k][0]
            binIdx += 1
        sumXvals = [value for value in sumXvals if value != None]
        sumYvals = [value for value in sumYvals if value != None]
        line = ax.plot(sumXvals, sumYvals, color='k', alpha=0, label='Sum of selected')
        lines.append(line[0])

        sum2D = numpy.array((sumXvals, sumYvals))
        sum2Dymax = numpy.amax(sum2D)
        sum2Dxmax = numpy.ndarray.argmax(sum2D)

        point = ax.plot(sum2D[0][sum2Dxmax - len(sumXvals)], sum2Dymax, '-bD')
        labels.append('Sum of selected')
        lines.append(point[0])
        mpld3.plugins.connect(fig, InteractiveLegend(lines, labels, 1, nameID, css))
    mpld3.plugins.connect(fig, HideLegend(nameID))
    code = mpld3.fig_to_html(fig)
    plt.close()
    return code, sum2D[0][sum2Dxmax - len(sumXvals)], sum2Dymax


def plotData(data, used, againstE, additional, lineNames, eType):
    plt.close()
    fig = plt.figure(figsize=(10, 7))
    css = """
    .legend-box{
        cursor: pointer;
    }
    """
    xs = []
    ys = []
    labels = []
    lines = []
    count = 0
    nameID = str(uuid.uuid4())
    fig, ax = plt.subplots()
    for idx, column in enumerate(data):
        for i in used:
            if (idx + 1) == i:
                xs = range(1, len(data[idx]) + 1)
                ys = data[idx]

                if againstE:
                    xs = [float(x) for x in eType]
                    xs = numpy.multiply(xs, 1000000)
                line = ax.plot(xs, ys, alpha=0, label=lineNames[0][count])
                lines.append(line[0])
                lines.append(line[0])
                labels.append(lineNames[0][count])
                count += 1

    if additional:
        for i in range(len(additional)):
            xs = range(1, len(additional[i]) + 1)

            ys = additional[i]
            if againstE:
                xs = [float(x) for x in eType]
                xs = numpy.multiply(xs, 1000000)
            line = ax.plot(xs, ys, alpha=0, label=lineNames[1][i])
            lines.append(line[0])
            lines.append(line[0])
            labels.append(lineNames[1][i])

    if not used and not additional:
        ax = plt.plot(ys, ys)
    else:
        mpld3.plugins.connect(fig, InteractiveLegend(lines, labels, 0, nameID, css))
        mpld3.plugins.connect(fig, HideLegend(nameID))
    code = mpld3.fig_to_html(fig)
    plt.close()
    return code


def convert_Numpy(used, data, additional):
    toNumpy = []

    if additional:
        for i in range(len(additional)):
            dat = additional[i]
            toNumpy.append(dat)

    for idx, column in enumerate(data):
        for i in used:
            if (idx + 1) == i:
                dat = [float(j) for j in data[i - 1]]
                toNumpy.append(dat)
    npData = numpy.array(toNumpy)
    max = []
    xcord = []
    for plot in npData:
        max.append(numpy.amax(plot))
        xcord.append(numpy.argmax(plot))
    return max, xcord, toNumpy


def energy_xtal(data, a1, a2, hrm):
    energy = []
    a1Dat = data[a1]
    a2Dat = data[a2]
    a1Dat = [float(i) for i in a1Dat]
    a2Dat = [float(i) for i in a2Dat]
    hrm_e0 = 14412500.0
    hrm_bragg1 = 18.4704
    hrm_bragg2 = 77.5328
    hrm_tan1 = math.tan(math.radians(hrm_bragg1))
    hrm_tan2 = math.tan(math.radians(hrm_bragg2))

    if hrm == '++':
        a = 1.0e-6 * hrm_e0 / (hrm_tan1 + hrm_tan2)
        b = a1Dat[0] - a2Dat[0]
        for i in range(len(a1Dat)):
            energy.append(a * (a1Dat[i] - a2Dat[i] - b))
    else:
        a = 1.0e-6 * hrm_e0 / (hrm_tan1 - hrm_tan2)
        b = a1Dat[0] + a2Dat[0]
        for i in range(len(a1Dat)):
            energy.append(a * (a1Dat[i] + a2Dat[i] - b))
    return energy


def energy_xtal_temp(data, a1, a2, t1, t2, hrm):
    energy = []
    xtal = energy_xtal(data, a1, a2, hrm)
    corr = temp_corr(data, t1, t2, hrm)
    for i in range(len(xtal)):
        energy.append(xtal[i] + corr[i])
    return energy


def temp_corr(data, t1, t2, hrm):
    corr = []
    t1Dat = data[t1]
    t2Dat = data[t2]
    t1Dat = [float(i) for i in t1Dat]
    t2Dat = [float(i) for i in t2Dat]
    hrm_e0 = 14412500.0
    hrm_bragg1 = 18.4704
    hrm_bragg2 = 77.5328
    hrm_tan1 = math.tan(math.radians(hrm_bragg1))
    hrm_tan2 = math.tan(math.radians(hrm_bragg2))
    hrm_alpha1 = 2.6e-6
    hrm_alpha2 = 2.6e-6
    at1 = hrm_alpha1 * hrm_tan1
    at2 = hrm_alpha2 * hrm_tan2

    if hrm == '++':
        a = - hrm_e0 / (hrm_tan1 + hrm_tan2)
        b = at1 * t1Dat[0] + at2 * t2Dat[0]
        for i in range(len(t1Dat)):
            corr.append(a * (at1 * t1Dat[i] + at2 * t2Dat[i] - b))
    else:
        a = - hrm_e0 / (hrm_tan1 - hrm_tan2)
        b = at1 * t1Dat[0] - at2 * t2Dat[0]
        for i in range(len(t1Dat)):
            corr.append(a * (at1 * t1Dat[i] - at2 * t2Dat[i] - b))
    return corr


def signal_normalized(data, sCol, nCol):
    signal = []
    sDat = data[sCol]
    nDat = data[nCol]
    sDat = [float(i) for i in sDat]
    nDat = [float(i) for i in nDat]

    normFac = norm_factors(data, nCol)

    for i in range(len(sDat)):
        signal.append(sDat[i] / nDat[i])
    for i in range(len(signal)):
        signal[i] = signal[i] * normFac[i]
    return signal


def norm_factors(data, nCol):
    norm = []
    nDat = data[nCol]
    nDat = [float(i) for i in nDat]

    ave = numpy.mean(nDat)  ##Using mean here, do you want to average it instead?
    # ave = numpy.average(nDat)
    for i in range(len(nDat)):
        norm.append(ave / nDat[i])
    return norm


class HideLegend(mpld3.plugins.PluginBase):
    """mpld3 plugin to hide legend on plot"""

    JAVASCRIPT = """
    var my_icon = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABVklEQVR42pXTO0sDQRSG4dmsyXptQ8BKCwsbq4CCiPgDrOwkIsTSf2Ul2KidhaAWYiFBFC1UWKN4VzTeQ0DfDd8u47gpLB4yc3Zy9szMWWOM8ZARz/ltFRvGlmJJ8D928axxy0UDKGMdo8gqfo66te7Xn9owhX3c4AWXGl/hBA1ne8kkh2+8KtEsPpXkHmP4wiN60iq4xYTGG1i1ys6jigX040kvaSbI6y1lBbpQsRIHOMAi9hQbwUec4B13mvgoIbTmb6rGtxJH4zPMG2UqKBg9nMGpxnVtx76+uPROVW6KOES3kkzjAkuqzLcSVKwDj148GB9iUYtzmofOQWV0eNtKeI1l9xYmdeeB9ldDu571qfM6dM1zSvSnlaP7fcAKhtRAUWWbGNezNWdbycBXt4Uq8Rg7cqTu7E1p+WRQ06nH2bPaTmA1lKu5BU+ZG1pof762tJj3A656Tx0L91EcAAAAAElFTkSuQmCC";
    mpld3.register_plugin("hidelegend", HideLegend);
    HideLegend.prototype = Object.create(mpld3.Plugin.prototype);
    HideLegend.prototype.constructor = HideLegend;
    HideLegend.prototype.requiredProps = ["nameID"];
    HideLegend.prototype.defaultProps = {};
    function HideLegend(fig, props){
        var tempName = props.nameID
        mpld3.Plugin.call(this, fig, props);
        var HideLegendButton = mpld3.ButtonFactory({
            buttonID: "hideLegend",
            sticky: false,
            onActivate: function(){
                var legend = $('[name=' + tempName + ']');
                var pltStat = localStorage.getItem('pltStat');
                if (pltStat == 0){
                    legend[0].style.visibility = "visible";
                    localStorage.setItem('pltStat', 1);
                }
                else{
                    legend[0].style.visibility = "hidden";
                    localStorage.setItem('pltStat', 0);
                }
            },
            icon: function(){
                return my_icon;
            }
        });
        this.fig.buttons.push(HideLegendButton);
    }
    """

    def __init__(self, nameID):
        self.dict_ = {'type': 'hidelegend',
                      'nameID': nameID}


class InteractiveLegend(mpld3.plugins.PluginBase):
    """"A plugin that allows the user to toggle lines though clicking on the legend"""

    JAVASCRIPT = """
        mpld3.register_plugin("interactive_legend", InteractiveLegend);
        InteractiveLegend.prototype = Object.create(mpld3.Plugin.prototype);
        InteractiveLegend.prototype.constructor = InteractiveLegend;
        InteractiveLegend.prototype.requiredProps = ["line_ids", "labels", "sized", "nameID"];
        InteractiveLegend.prototype.defaultProps = {};
        function InteractiveLegend(fig, props){
           mpld3.Plugin.call(this, fig, props);
        };
        InteractiveLegend.prototype.draw = function(){
            if (this.props.sized == 1){
                var svg = document.getElementsByClassName("mpld3-figure");
                svg[0].setAttribute("viewBox", "0 0 600 480");
                svg[0].setAttribute("width", 900);
                svg[0].setAttribute("height", 600);
            }
            var labels = new Array();
            for(var i=1; i<=this.props.labels.length; i++){
                var obj = {};
                obj.label = this.props.labels[i - 1];
                line = mpld3.get_element(this.props.line_ids[(i * 2) - 2], this.fig);
                obj.line1 = line
                point = mpld3.get_element(this.props.line_ids[(i * 2) - 1], this.fig);
                obj.line2 = point;
                obj.visible = false;
                obj.lineNum = i;
                var outer = point.parent.baseaxes[0][0].children[1];
                var points = outer.getElementsByTagName("g");
                points[3-i].firstChild.style.setProperty('stroke-opacity', 0, 'important');
                points[3-i].firstChild.style.setProperty('fill-opacity', 0, 'important');

               labels.push(obj);
            }
            var ax = this.fig.axes[0];
            var legend = this.fig.canvas.append("svg:g")
                                    .attr("name", this.props.nameID)
                                    .style("overflow", "auto")
                                    .style("max-height", "300px")

            legend.selectAll("rect")
                        .data(labels)
                    .enter().append("rect")
                        .attr("height", 10)
                        .attr("width", 25)
                        .attr("x", ax.width+10+ax.position[0] - 150)
                        .attr("y", function(d, i){
                            return ax.position[1] + i * 25 - 10;})
                        .attr("stroke", function(d){
                            return d.line1.props.edgecolor})
                        .attr("class", "legend-box")
                        .style("fill", "white")
                        .on("click", click)

            legend.selectAll("text")
                        .data(labels)
                    .enter().append("text")
                        .attr("x", function(d){
                            return ax.width+10+ax.position[0] + 25 + 15 - 150
                            })
                        .attr("y", function(d, i){
                            return ax.position[1] + i * 25
                            })
                        .text(function(d){return d.label})

            if (this.props.sized == 1){
                var boxes = legend.selectAll("rect");
                var lastbox = $(boxes[0]).last();
                lastbox[0].__onclick();
            }
            else{
                var boxes = legend.selectAll("rect")
                var tempboxes = boxes[0]
                for (var i = 0; i < tempboxes.length; i++){
                    var temp = tempboxes[i];
                    temp.__onclick();
                }

            }


            function click(d, i){
                d.visible = !d.visible;
                d3.select(this)
                    .style("fill", function(d, i){
                        var color = d.line1.props.edgecolor;
                        return d.visible ? color : "white";
                    })
                d3.select(d.line1.path[0][0])
                    .style("stroke-opacity", d.visible? 1 : d.line1.props.alpha)

                if(d.visible == true){
                    var outer = d.line2.parent.baseaxes[0][0].children[1];
                    var points = outer.getElementsByTagName("g");
                    points[3-d.lineNum].firstChild.style.setProperty('stroke-opacity', 1, 'important');
                    points[3-d.lineNum].firstChild.style.setProperty('fill-opacity', 1, 'important');
                }
                else{
                    var outer = d.line2.parent.baseaxes[0][0].children[1];
                    var points = outer.getElementsByTagName("g");
                    points[3-d.lineNum].firstChild.style.setProperty('stroke-opacity', 0, 'important');
                    points[3-d.lineNum].firstChild.style.setProperty('fill-opacity', 0, 'important');
                }
            }
        };
    """

    def __init__(self, lines, labels, sized, nameID, css):
        self.css_ = css or ""

        self.lines = lines

        self.dict_ = {"type": "interactive_legend",
                      "line_ids": [mpld3.utils.get_id(line) for line in lines],
                      "labels": labels,
                      "nameID": nameID,
                      "sized": sized}


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
