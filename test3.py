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
from sqlalchemy import desc
from decimal import *
import matplotlib.patches as mpatches

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
    for instance in sessions:
        lastMod = instance.last_used
        data.insert(0, {'name': instance.name, 'id': instance.id, 'comment': instance.comment, 'authed': instance.authed, 'modified': lastMod})
    if request.method == 'POST':
        return redirect(url_for('dataFormat'))
    return render_template('view_output.html', data=data, user=user)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    user = current_user
    data = []
    files = dataFile.query.order_by('id')
    for instance in files:
        fsize = size(instance.path)
        lastMod = modified(instance.path)
        temp = lastMod.strftime("%d/%m/%Y %H:%M:%S")
        modname = [instance.name + temp]
        data.insert(0, {'name': instance.name, 'path': instance.path, 'id': instance.id, 'comment': instance.comment, 'authed': instance.authed, 'size': fsize, 'modified': lastMod, 'modname': modname})
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('upload.html', data=data, user=user)


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
    userID = str(user.get_id())
    files = dataFile.query.filter_by(authed=userID)
    for instance in files:
        fsize = size(instance.path)
        lastMod = modified(instance.path)
        temp = lastMod.strftime("%d/%m/%Y %H:%M:%S")
        modname = [instance.name + temp]
        fdata.insert(0, {'name': instance.name, 'path': instance.path, 'id': instance.id, 'comment': instance.comment, 'authed': instance.authed, 'size': fsize, 'modified': lastMod, 'modname': modname})

    if findPlot != 1:
        form = InputForm(request.form)
        fig = plt.figure(figsize=(10, 7))
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
            data, name, unusedpath = readAscii(file_instance.path)
            for i in range(len(bools)):
                if bools[i].data:
                    if columns[i].data == None:
                        if i == 1:
                            energy = energy_xtal(data, unicode_to_int(columns[2].data), unicode_to_int(columns[3].data))
                            additional.append(energy)
                        elif i == 6:
                            energy = temp_corr(data, unicode_to_int(columns[4].data), unicode_to_int(columns[5].data))
                            additional.append(energy)
                        elif i == 8:
                            signal = signal_normalized(data, unicode_to_int(columns[7].data), unicode_to_int(columns[9].data))
                            additional.append(signal)
                        else:
                            norm = norm_factors(data, unicode_to_int(columns[9].data))
                            additional.append(norm)
                        continue
                    else:
                        used.append(unicode_to_int(columns[i].data))
            code = plotData(data, used, againstE, additional)
            format_instance.plot = code
            db.session.commit()
            #data.append({'form': format_instance, 'plot': plot, 'id': file_instance.id, 'comment': file_instance.comment, 'columns': columns, 'bools': bools})
        else:
            data, name, unusedpath = readAscii(file_instance.path)
            used = []
            againstE = False
            format = currentMeta()
            format.name = file_instance.name
            format.path = file_instance.path
            format.ebool = True
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
            format.file_id = idthis

            used.append(1)
            used.append(11)

            code = plotData(data, used, False, None)
            format.plot = code
            db.session.add(format)
            db.session.commit()

            code = format.plot
            form = populate_from_instance(format)
    return render_template("data_format.html", user=user, code=code, form=form, againstE=againstE, data=fdata, ses=thisSession)


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
        fpath = file_instance.path

        format_instance = db.session.query(currentMeta).filter_by(path=fpath).first()
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
        instances = user.loggedUser.order_by(desc('id'))
        for instance in instances:
            form = populate_from_instance(instance)
            columns, bools = splitForm(form)
            plot = instance.plot
            if instance.comment:
                comment = instance.comment
            else:
                comment = ''
            data.append({'form': form, 'plot': plot, 'id': instance.id, 'comment': comment, 'columns': columns, 'bools': bools, 'name': instance.name, 'time': instance.timestamp, 'ses': instance.session})
    return render_template("session.html", data=data)

@app.route('/addf', methods=['POST'])
@login_required
def addFile():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            pathfilename = filename + str(datetime.now())
            file.save(os.path.join(app.config['UPLOAD_DIR'], pathfilename))

            dfile = dataFile()
            dfile.name = filename
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
            db.session.delete(instance)
        if table == 'Meta':
            instance = user.logBook.filter_by(id=idnum).first()
            db.session.delete(instance)
        if table == 'Session':
            instance = db.session.query(sessionFiles).filter_by(id=idnum).first()
            db.session.delete(instance)

            instances = db.session.query(sessionFilesMeta).filter_by(sessionFiles_id=idnum).all()
            for instance in instances:
                meta = db.session.query(sessionMeta).filter_by(id=instance.sessionMeta_id).first()
                db.session.delete(meta)
                db.session.delete(instance)
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
            if format_instance is not None:
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
        #lastMod = modified(instance.path)
        #temp = lastMod.strftime("%Y-%m-%d %H:%M:%S")
        #modname = str(instance.name) + ' ' + temp
        return instance.name
    return 'Holder'

@app.route('/del_entry', methods=['GET', 'POST'])
@login_required
def delete_entry():
    user = current_user
    if request.method == 'POST':
        idthis = request.form.get('id', type=int)
        if idthis == -1:
            user.logBook.delete()
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
    max = 'No File Selected'
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
            data, name, unusedpath = readAscii(file_instance.path)
            for i in range(len(bools)):
                if bools[i].data:
                    if columns[i].data == None:
                        if i == 1:
                            energy = energy_xtal(data, unicode_to_int(columns[2].data), unicode_to_int(columns[3].data))
                            additional.append(energy)
                            legendNames.append(columns[i].id)
                        elif i == 6:
                            energy = temp_corr(data, unicode_to_int(columns[4].data), unicode_to_int(columns[5].data))
                            additional.append(energy)
                            legendNames.append(columns[i].id)
                        elif i == 8:
                            signal = signal_normalized(data, unicode_to_int(columns[7].data), unicode_to_int(columns[9].data))
                            additional.append(signal)
                            legendNames.append(columns[i].id)
                        else:
                            norm = norm_factors(data, unicode_to_int(columns[9].data))
                            additional.append(norm)
                            legendNames.append(columns[i].id)
                        continue
                    else:
                        used.append(unicode_to_int(columns[i].data))
                    legendNames.append(columns[i].id)
            max, xmax, ycords = convert_Numpy(used, data, additional)
            code = simplePlot(ycords, xmax, againstE, data, file_instance.name, legendNames)
        if idthis is None:
            jidlist = json.loads(idlist)
            alldata = []
            allxmax = []
            allycords = []
            allagainstE = []

            for anID in jidlist:
                file_instance = db.session.query(dataFile).filter_by(id=anID).first()
                try:
                    fid = file_instance.id
                except AttributeError:
                    flash('Unable to find file')
                    return redirect(url_for('process'))
                format_instance = db.session.query(currentMeta).filter_by(file_id=fid).first()
                againstE = format_instance.against_E
                form = populate_from_instance(format_instance)
                columns, bools = splitForm(form)
                used = []
                additional = []
                data, name, unusedpath = readAscii(file_instance.path)
                for i in range(len(bools)):
                    if bools[i].data:
                        if columns[i].data == None:
                            if i == 1:
                                energy = energy_xtal(data, unicode_to_int(columns[2].data), unicode_to_int(columns[3].data))
                                additional.append(energy)
                            elif i == 6:
                                energy = temp_corr(data, unicode_to_int(columns[4].data), unicode_to_int(columns[5].data))
                                additional.append(energy)
                            elif i == 8:
                                signal = signal_normalized(data, unicode_to_int(columns[7].data), unicode_to_int(columns[9].data))
                                additional.append(signal)
                            else:
                                norm = norm_factors(data, unicode_to_int(columns[9].data))
                                additional.append(norm)
                            continue
                        else:
                            used.append(unicode_to_int(columns[i].data))
                max, xmax, ycords = convert_Numpy(used, data, additional)
                alldata.append(data)
                allxmax.append(xmax)
                allycords.append(ycords)
                allagainstE.append(againstE)
            code = mergePlots(allycords, allxmax, allagainstE, alldata)
    else:
        fig = plt.figure(figsize=(10, 7))
        code = mpld3.fig_to_html(fig)
    return render_template("data_process.html", user=user, ses=current_session, code=code, max=max)


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


def simplePlot(data, xmax, againstE, raw, filename, linenames):
    plt.close()
    fig = plt.figure(figsize=(10, 7))
    count = 0
    for plot in data:
        xs = range(1, len(plot) + 1)
        ys = plot
        if againstE:
            xs = raw[0]
        line = plt.plot(xs, ys)
        plt.plot(xs[xmax[count]], ys[xmax[count]], '-bD')
        color = line[0].get_color()
        patch = mpatches.Patch(color=str(line[0].get_color()), label=filename + ' ' + linenames[count])
        plt.legend(handles=[patch])
        count += 1
    code = mpld3.fig_to_html(fig)
    plt.close()
    return code

def mergePlots(allycords, allxmax, allagainstE, alldata):
    fig = plt.figure(figsize=(10, 7))
    count1 = 0
    for oneDat in allycords:
        count2 = 0
        for plot in oneDat:
            xs = range(1, len(plot) + 1)
            ys = plot
            if allagainstE[count1]:
                xs = alldata[count1][0]
            plt.plot(xs, ys)
            plt.plot(xs[allxmax[count1][count2]], ys[allxmax[count1][count2]], '-bD')
            count2 += 1
        count1 += 1
    code = mpld3.fig_to_html(fig)
    plt.close()
    return code



def plotData(data, used, againstE, additional):
    plt.close()
    fig = plt.figure(figsize=(10, 7))
    xs = []
    ys = []

    for idx, column in enumerate(data):
        for i in used:
            if (idx + 1) == i:
                xs = range(1, len(data[idx]) + 1)
                ys = data[idx]
                if againstE:
                    xs = data[0]
                ax = plt.plot(xs, ys)

    if additional:
        for i in range(len(additional)):
            xs = range(1, len(additional[i]) + 1)
            ys = additional[i]
            if againstE:
                xs = data[0]
            ax = plt.plot(xs, ys)

    if not used and not additional:
        ax = plt.plot(ys, ys)
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
                dat = [float(j) for j in data[i-1]]
                toNumpy.append(dat)
    npData = numpy.array(toNumpy)
    max = []
    xcord = []
    for plot in npData:
        max.append(numpy.amax(plot))
        xcord.append(numpy.argmax(plot))
    return max, xcord, toNumpy

def energy_xtal(data, a1, a2):
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

    a = 1.0e-6 * hrm_e0 / (hrm_tan1 + hrm_tan2)
    b = a1Dat[0] + a2Dat[0]
    for i in range(len(a1Dat)):
        energy.append(a * (a1Dat[i] + a2Dat[i] - b))
    return energy

def temp_corr(data, t1, t2):
    energy = []
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

    a = - hrm_e0 / (hrm_tan1 + hrm_tan2)
    b = at1 * t1Dat[0] + at2 * t2Dat[0]
    for i in range(len(t1Dat)):
        energy.append(a * (at1 * t1Dat[i] + at2 * t2Dat[i] - b))
    return energy

def signal_normalized(data, sCol, nCol):
    signal = []
    sDat = data[sCol]
    nDat = data[nCol]
    sDat = [float(i) for i in sDat]
    nDat = [float(i) for i in nDat]

    ave = numpy.mean(nDat)
    for i in range(len(sDat)):
        signal.append(sDat[i] * ave / nDat[i])
    return signal

def norm_factors(data, nCol):
    norm = []
    nDat = data[nCol]
    nDat = [float(i) for i in nDat]

    ave = numpy.mean(nDat)
    for i in range(len(nDat)):
        norm.append(ave / nDat[i])
    return norm


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
