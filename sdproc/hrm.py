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

import os

from flask import render_template, request, Blueprint, url_for, redirect, flash, send_from_directory, current_app
from flask_login import current_user, login_required

from sessions.routes import add_user_file
from files.utils import file_path

import matplotlib
import mpld3

from sdproc.hrms.forms import InputForm
from utilities.graphing_utility import GraphingUtility
from utilities.sdproc_mpld3.hide_legend import HideLegend

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from utilities.file_utility import FileUtility
from utilities.sdproc_mpld3.interactive_legend import InteractiveLegend

from db.db_model import db, User, LogBook, CurrentMeta, CurrentDAT, UserFiles, HRM, DataFile, SessionFiles

import json
import numpy
import uuid
from sqlalchemy import and_
from sessions.forms import SessionForm

hrmApp = Blueprint('hrm', __name__)

""" start of main routes for web pages """


@hrmApp.route('/data', methods=['GET', 'POST'])
@login_required
def dataFormat():
    """
    Template generator for the data page. Has a multitude of options that allow the user to display file information
    in the form of a plot. Options are saved to a live-updated session for each respective file that persists through
    temporarily leaving the page. Defaults are assigned to all files within this method.
    :return:
    """
    user = current_user
    thisSession = current_user.current_session
    if thisSession != 'None':
        comments = SessionFiles.query.filter_by(name=thisSession).first().comment
    else:
        comments = None
    findPlot = request.form.get('plot', type=int)
    unit = request.form.get('unit', type=str)
    nameID = str(uuid.uuid4())

    user_sessions = SessionFiles.query.filter_by(user_id=user.id).all()

    if findPlot != 1:
        form = InputForm(request.form)
        plt.figure(figsize=(10, 7))
        fig, ax = plt.subplots()
        mpld3.plugins.connect(fig, InteractiveLegend([], [], 0, nameID, None))
        code = mpld3.fig_to_html(fig)
        plt.clf()
        againstE = 'Point #'
    else:
        idthis = request.form.get('idnext', type=int)
        file_instance = db.session.query(DataFile).filter(DataFile.id == idthis).first()
        format_instance = db.session.query(CurrentMeta).filter(and_(CurrentMeta.user_id == current_user.get_id(),
                                                                    CurrentMeta.file_id == file_instance.id,
                                                                    CurrentMeta.session == current_user.current_session)).first()
        if format_instance is not None:
            againstE = format_instance.against_E
            form = GraphingUtility.populate_from_instance(format_instance)
            columns, bools = GraphingUtility.splitForm(form)
            basedColumns = GraphingUtility.zeroBaseColumns(columns)
            used = []
            additional = []
            addLabels = []
            normLabels = []
            labels = []
            path = file_path("." + file_instance.type, file_instance.path)
            if str(file_instance.type) == 'mda':
                data, name, unusedpath = FileUtility.readMda(path)
            else:
                data, name, unusedpath = FileUtility.readAscii(path, file_instance.comChar)
            for i in range(len(bools)):
                if bools[i].data:
                    if columns[i].data == None:
                        if i == 1:
                            energy = GraphingUtility.energy_xtal(data,
                                                                 GraphingUtility.unicode_to_int(basedColumns[3].data),
                                                                 GraphingUtility.unicode_to_int(basedColumns[4].data),
                                                                 format_instance.hrm)
                            additional.append(energy)
                            addLabels.append('Energy xtal')
                            energy = numpy.divide(energy, 1000000)
                        elif i == 2:
                            energy = GraphingUtility.energy_xtal_temp(data, GraphingUtility.unicode_to_int(
                                basedColumns[3].data),
                                                                      GraphingUtility.unicode_to_int(
                                                                          basedColumns[4].data),
                                                                      GraphingUtility.unicode_to_int(
                                                                          basedColumns[5].data),
                                                                      GraphingUtility.unicode_to_int(
                                                                          basedColumns[6].data), format_instance.hrm)
                            additional.append(energy)
                            addLabels.append('Energy xtal w/T')
                            energy = numpy.divide(energy, 1000000)
                        elif i == 7:
                            energy = GraphingUtility.temp_corr(data,
                                                               GraphingUtility.unicode_to_int(basedColumns[5].data),
                                                               GraphingUtility.unicode_to_int(basedColumns[6].data),
                                                               format_instance.hrm)
                            additional.append(energy)
                            addLabels.append('Temp. corr')
                        elif i == 9:
                            signal = GraphingUtility.signal_normalized(data, GraphingUtility.unicode_to_int(
                                basedColumns[8].data),
                                                                       GraphingUtility.unicode_to_int(
                                                                           basedColumns[10].data))
                            additional.append(signal)
                            addLabels.append('Signal Normalized')
                        else:
                            norm = GraphingUtility.norm_factors(data,
                                                                GraphingUtility.unicode_to_int(basedColumns[10].data))
                            additional.append(norm)
                            addLabels.append('Normalized')
                        continue
                    else:
                        used.append(GraphingUtility.unicode_to_int(basedColumns[i].data))
                        normLabels.append(str(basedColumns[i].label.text)[:-2])
            if againstE == 'Energy':
                etype = data[GraphingUtility.unicode_to_int(basedColumns[0].data)]
            elif againstE == 'Energy xtal':
                etype = numpy.divide(
                    GraphingUtility.energy_xtal(data, GraphingUtility.unicode_to_int(basedColumns[3].data),
                                                GraphingUtility.unicode_to_int(basedColumns[4].data),
                                                format_instance.hrm), 1000000)
            elif againstE == 'Energy xtal w/T':
                etype = numpy.divide(
                    GraphingUtility.energy_xtal_temp(data, GraphingUtility.unicode_to_int(basedColumns[3].data),
                                                     GraphingUtility.unicode_to_int(basedColumns[4].data),
                                                     GraphingUtility.unicode_to_int(basedColumns[5].data),
                                                     GraphingUtility.unicode_to_int(basedColumns[6].data),
                                                     format_instance.hrm),
                    1000000)
            elif againstE == 'Energy Fitted':
                code, ycords, form = GraphingUtility.peakFit(idthis, format_instance.fit_energy,
                                                             format_instance.fit_signal, unit,
                                                             format_instance.fit_type, format_instance.fit_range,
                                                             format_instance.fit_pos, format_instance.fit_localRange)
                etype = ycords[0]
            else:
                etype = 0
            labels.append(normLabels)
            labels.append(addLabels)
            code = GraphingUtility.plotData(data, used, againstE, additional, labels, etype, unit)
            format_instance.plot = code
            db.session.commit()
        else:
            if str(file_instance.type) == 'mda':
                path = file_path("." + file_instance.type, file_instance.path)
                data, name, unusedpath = FileUtility.readMda(path)
            else:
                path = file_path("." + file_instance.type, file_instance.path)
                data, name, unusedpath = FileUtility.readAscii(path, file_instance.comChar)
            etype = data[1]
            used = []
            againstE = 'Point #'
            format = CurrentMeta()
            format.name = file_instance.name
            format.path = file_instance.path
            format.comment = file_instance.comment
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
            format.against_E = 'Point #'
            format.fit_type = 'Unfit'
            format.fit_pos = 0
            format.fit_range = 3
            format.fit_energy = 'Energy'
            format.fit_signal = 'Signal'
            format.fit_localRange = None
            format.file_id = idthis
            format.checked = True
            hrmInstance = db.session.query(HRM).filter_by(name='Fe-inline-1meV').first()
            hrm = {'name': hrmInstance.name, 'hrm_e0': hrmInstance.hrm_e0, 'hrm_bragg1': hrmInstance.hrm_bragg1,
                   'hrm_bragg2': hrmInstance.hrm_bragg2, 'hrm_geo': hrmInstance.hrm_geo,
                   'hrm_alpha1': hrmInstance.hrm_alpha1,
                   'hrm_alpha2': hrmInstance.hrm_alpha2, 'hrm_theta1_sign': hrmInstance.hrm_theta1_sign,
                   'hrm_theta2_sign': hrmInstance.hrm_theta2_sign}
            hrm = json.dumps(hrm)
            format.hrm = hrm
            format.session = current_user.current_session
            format.user = current_user

            used.append(10)
            labels = [['Signal']]
            code = GraphingUtility.plotData(data, used, 'Point', None, labels, etype, unit)
            format.plot = code
            db.session.add(format)
            db.session.commit()

            code = format.plot
            form = GraphingUtility.populate_from_instance(format)
    return render_template("new_df.html", user=user, code=code, form=form, againstE=againstE,
                           ses=thisSession, comments=comments, user_sessions=user_sessions)


@hrmApp.route('/modifyDAT', methods=['GET', 'POST'])
@login_required
def modifyDAT():
    if current_user.badge_number is None:
        flash('Please update your badge number in order to continue', 'info')
        return redirect(url_for('users.profile2'))
    '''
	Template function for the modifyDAT page.

	Essentially just plotting the DAT information stored in the user's CurrentDAT.

	Must have generated a DAT file via either a DAT session being loaded or summing data on the sum page.
	:return:
	'''
    try:
        DAT = db.session.query(CurrentDAT).filter(CurrentDAT.user == current_user).first()
    except Exception, e:
        code = 'No DAT selected'
        return render_template("new_mdat.html", user=current_user, ses=current_user.current_session, code=code)
    if DAT == None:
        code = 'No DAT selected'
        return render_template("new_mdat.html", user=current_user, ses=current_user.current_session, code=code)
    user = db.session.query(User).filter_by(username=current_user.username).first()
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
    nameID = str(uuid.uuid4())
    fig, ax = plt.subplots()
    data = json.loads(DAT.DAT)
    xs = data[0]
    ys = data[1]
    line = ax.plot(xs, ys, alpha=0, label='Summed')
    lines.append(line[0])
    labels.append('Summed')
    mpld3.plugins.connect(fig, InteractiveLegend(lines, labels, 1, nameID, css))
    mpld3.plugins.connect(fig, HideLegend(nameID))
    code = mpld3.fig_to_html(fig)
    plt.close('all')
    return render_template("new_mdat.html", user=current_user, ses=DAT.DATname, code=code)


@hrmApp.route('/process', methods=['GET', 'POST'])
@login_required
def process():
    """
    Large function that uses the peakfit setting saved to each file to peak fit and sum all of the files the user has in
    their CurrentMeta. Summing can be done with a binning or interpolation method. Maxes are extracted the same either
    way.
    :return:
    """
    user = current_user
    idthis = request.form.get('idnext', type=int)
    idlist = request.form.get('idList', type=str)
    pltLeg = request.form.get('pltLeg', type=int)
    binWidth = request.form.get('binWidth', type=float)
    output = request.form.get('output', type=int)
    endmax = 'No File Selected'
    senddata = []
    allFileNames = []
    outputs = ''
    if idthis is not None or idlist is not None:
        if idlist is None:
            file_instance = db.session.query(DataFile).filter_by(id=idthis).first()
            try:
                fid = file_instance.id
            except AttributeError:
                flash('Please select a file')
                return redirect(url_for('waitProc'))
            format_instance = db.session.query(CurrentMeta).filter(and_(CurrentMeta.user_id == current_user.get_id(),
                                                                        CurrentMeta.file_id == file_instance.id,
                                                                        CurrentMeta.session == current_user.current_session)).first()
            againstE = format_instance.against_E
            form = GraphingUtility.populate_from_instance(format_instance)
            columns, bools = GraphingUtility.splitForm(form)
            basedColumns = GraphingUtility.zeroBaseColumns(columns)
            used = []
            additional = []
            legendNames = []
            endmax = []
            allFileNames = []
            path = file_path("." + file_instance.type, file_instance.path)
            if str(file_instance.type) == 'mda':
                data, name, unusedpath = GraphingUtility.readMda(path)
            else:
                data, name, unusedpath = GraphingUtility.readAscii(path, file_instance.comChar)
            fitType = format_instance.fit_type
            if fitType == 'Unfit':
                used.append(GraphingUtility.unicode_to_int(basedColumns[0].data))
                legendNames.append(basedColumns[0].id)
                used.append(GraphingUtility.unicode_to_int(basedColumns[8].data))
                legendNames.append(basedColumns[8].id)
            else:
                if bools[1].data:
                    energy = GraphingUtility.energy_xtal(data, GraphingUtility.unicode_to_int(basedColumns[3].data),
                                                         GraphingUtility.unicode_to_int(basedColumns[4].data),
                                                         format_instance.hrm)
                    additional.append(energy)
                    legendNames.append(basedColumns[1].id)
                elif bools[2].data:
                    energy = GraphingUtility.energy_xtal_temp(data,
                                                              GraphingUtility.unicode_to_int(basedColumns[3].data),
                                                              GraphingUtility.unicode_to_int(basedColumns[4].data),
                                                              GraphingUtility.unicode_to_int(basedColumns[5].data),
                                                              GraphingUtility.unicode_to_int(basedColumns[6].data),
                                                              format_instance.hrm)
                    additional.append(energy)
                    legendNames.append(basedColumns[2].id)
                else:
                    used.append(GraphingUtility.unicode_to_int(basedColumns[0].data))
                    legendNames.append(basedColumns[0].id)
                if bools[9].data:
                    signal = GraphingUtility.signal_normalized(data,
                                                               GraphingUtility.unicode_to_int(basedColumns[8].data),
                                                               GraphingUtility.unicode_to_int(basedColumns[10].data))
                    additional.append(signal)
                    legendNames.append(basedColumns[9].id)
                else:
                    used.append(GraphingUtility.unicode_to_int(basedColumns[8].data))
                    legendNames.append(basedColumns[8].id)
            max, xmax, ycords = GraphingUtility.convert_Numpy(used, data, additional)
            inputCord = format_instance.fit_pos
            fitRange = format_instance.fit_range
            if fitType == 'AtMax' or fitType == 'Unfit':
                temp = xmax[1]
                xmax[1] = (ycords[0][xmax[1]] * 1000000)
                npXcords = numpy.array(ycords[0])
                npXcords = numpy.multiply(npXcords, 1000000)
                center = GraphingUtility.atMax(ycords, npXcords, xmax, fitRange)
                xmax[1] = temp
                ycords[0] = numpy.multiply(ycords[0], 1000000)
                GraphingUtility.moveXcords(ycords, center)
                format_instance.fit_type = 'AtMax'
                format_instance.fit_pos = center
                format_instance.fit_range = fitRange
                db.session.commit()
            else:
                ycords[0] = numpy.multiply(ycords[0], 1000000)
                GraphingUtility.moveXcords(ycords, inputCord)
            endmax.append([format(max[0], '.6f'), format(max[1], '.6f')])
            allFileNames.append(file_instance.name)
            if output == 1:
                outputData = []
                outputData.append(ycords[0].tolist())
                outputData.append(ycords[1])
                outputs = json.dumps(outputData)
            code = GraphingUtility.simple_plot(ycords, xmax, file_instance.name, legendNames, pltLeg, 1)
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
                file_instance = db.session.query(DataFile).filter_by(id=anID).first()
                used = []
                try:
                    fid = file_instance.id
                except AttributeError:
                    flash('Unable to find file')
                    return redirect(url_for('waitProc'))
                format_instance = db.session.query(CurrentMeta).filter(
                    and_(CurrentMeta.user_id == current_user.get_id(),
                         CurrentMeta.file_id == file_instance.id,
                         CurrentMeta.session == current_user.current_session)).first()
                againstE = format_instance.against_E
                form = GraphingUtility.populate_from_instance(format_instance)
                columns, bools = GraphingUtility.splitForm(form)
                basedColumns = GraphingUtility.zeroBaseColumns(columns)
                path = file_path("." + file_instance.type, file_instance.path)
                if str(file_instance.type) == 'mda':
                    data, name, unusedpath = FileUtility.readMda(path)
                else:
                    data, name, unusedpath = GraphingUtility.readAscii(path, file_instance.comChar)
                if bools[1].data:
                    energy = GraphingUtility.energy_xtal(data, GraphingUtility.unicode_to_int(basedColumns[3].data),
                                                         GraphingUtility.unicode_to_int(basedColumns[4].data),
                                                         format_instance.hrm)
                    used.append(energy)
                elif bools[2].data:
                    energy = GraphingUtility.energy_xtal_temp(data,
                                                              GraphingUtility.unicode_to_int(basedColumns[3].data),
                                                              GraphingUtility.unicode_to_int(basedColumns[4].data),
                                                              GraphingUtility.unicode_to_int(basedColumns[5].data),
                                                              GraphingUtility.unicode_to_int(basedColumns[6].data),
                                                              format_instance.hrm)
                    used.append(energy)
                else:
                    used.append(GraphingUtility.unicode_to_int(basedColumns[0].data))
                if bools[9].data:
                    signal = GraphingUtility.signal_normalized(data,
                                                               GraphingUtility.unicode_to_int(basedColumns[8].data),
                                                               GraphingUtility.unicode_to_int(basedColumns[10].data))
                    used.append(signal)
                    allLegendNames.append(basedColumns[9].id)
                else:
                    used.append(GraphingUtility.unicode_to_int(basedColumns[8].data))
                    allLegendNames.append(basedColumns[8].id)
                max, xmax, ycords = GraphingUtility.convert_Numpy(used, data, None)
                fitType = format_instance.fit_type
                inputCord = format_instance.fit_pos
                fitRange = format_instance.fit_range
                if fitType == 'AtMax' or fitType == 'Unfit':
                    xmaxHold = xmax[1]
                    xmax[1] = (ycords[0][xmax[1]] * 1000000)
                    npXcords = numpy.array(ycords[0])
                    npXcords = numpy.multiply(npXcords, 1000000)
                    center = GraphingUtility.atMax(ycords, npXcords, xmax, fitRange)
                    xmax[1] = xmaxHold
                    ycords[0] = npXcords
                    GraphingUtility.moveXcords(ycords, center)
                    format_instance.fit_type = 'AtMax'
                    format_instance.fit_pos = center
                    format_instance.fit_range = fitRange
                    db.session.commit()
                else:
                    npXcords = numpy.array(ycords[0])
                    npXcords = numpy.multiply(npXcords, 1000000)
                    ycords[0] = npXcords
                    GraphingUtility.moveXcords(ycords, inputCord)
                max[0] = ((max[0] * 1000000) - format_instance.fit_pos)
                endmax.append([format(max[0], '.6f'), format(max[1], '.6f')])
                alldata.append(data)
                allxmax.append(xmax)
                allycords.append(ycords)
                allagainstE.append(againstE)
                allFileNames.append(file_instance.name)
            if binWidth == None:
                code, sumxmax, sumymax, sumX, sumY = GraphingUtility.mergePlots(allycords, allxmax, allagainstE,
                                                                                alldata,
                                                                                allLegendNames,
                                                                                allFileNames, pltLeg)
                sumX = sumX.tolist()
                sumY = sumY.tolist()
            else:
                code, sumxmax, sumymax, sumX, sumY = GraphingUtility.mergeBin(allycords, allxmax, allagainstE, alldata,
                                                                              allLegendNames,
                                                                              allFileNames,
                                                                              pltLeg, binWidth)
            if output == 1:
                outputs = []
                outputs.append(sumX)
                outputs.append(sumY)
                outputs = json.dumps(outputs)
            endmax.append([format(sumxmax, '.6f'), format(sumymax, '.6f')])
            allFileNames.append('Summed Files')
    else:
        fig = plt.figure(figsize=(7, 6))
        code = mpld3.fig_to_html(fig)
    procEntry = db.session.query(LogBook).filter_by(name="Process Entry").first()
    if procEntry != None:
        procEntry.plot = code
        db.session.commit()
    else:
        processEntry = LogBook()
        processEntry.name = "Process Entry"
        processEntry.plot = code
        processEntry.user = user
        db.session.add(processEntry)
        db.session.commit()
    senddata.append({'max': endmax, 'filenames': allFileNames})
    return render_template("new_dp.html", user=user, ses=current_user.current_session, code=code, data=senddata,
                           outputs=outputs)


""" end of main routes for web pages """


@hrmApp.route('/generateOutput', methods=['GET', 'POST'])
@login_required
def generateOutput():
    '''
	This pulls data from a request to determine which type of file needs to be generated and redirects the file to output.

	The outType that is sent from the request data determines which type of output to compile the given data into.
	If the output is being saved to the server a copy is made in app.config['UPLOAD_DIR'].  Otherwise the file is sent to /sendOut where it is downloaded to the user's computer.
	:return:
	'''
    form = InputForm(request.form)
    id = request.form.get('idnum', type=str)
    outType = request.form.get('outType', type=int)
    print outType
    cordData = request.form.get('cordData', type=str)
    sesID = request.form.get('session', type=int)
    datFName = request.form.get('datFName', type=str)
    DBSave = request.form.get('DBSave', type=int)
    output = []
    colNames = []
    filename = ""
    if outType == 1:
        # this means the user clicked the output button on the Scans tab
        # lets the user download the output of mda and save the file
        file_instance = db.session.query(DataFile).filter_by(id=int(id)).first()
        format_instance = db.session.query(CurrentMeta).filter(and_(CurrentMeta.user_id == current_user.get_id(),
                                                                    CurrentMeta.file_id == int(id),
                                                                    CurrentMeta.session == current_user.current_session)).first()
        if str(file_instance.type) == 'mda':
            path = file_path("." + file_instance.type, file_instance.path)
            data, name, unusedpath = FileUtility.readMda(path)
        else:
            path = file_path("." + file_instance.type, file_instance.path)
            data, name, unusedpath = FileUtility.readAscii(path, file_instance.comChar)
        columns, bools = GraphingUtility.splitForm(form)
        basedColumns = GraphingUtility.zeroBaseColumns(columns)
        for i in range(len(bools)):
            if bools[i].data:
                if columns[i].data == None:
                    if i == 1:
                        energy = GraphingUtility.energy_xtal(data, GraphingUtility.unicode_to_int(basedColumns[3].data),
                                                             GraphingUtility.unicode_to_int(basedColumns[4].data),
                                                             format_instance.hrm)
                        output.append(energy)
                        colNames.append('Energy xtal')
                    elif i == 2:
                        energy = GraphingUtility.energy_xtal_temp(data,
                                                                  GraphingUtility.unicode_to_int(basedColumns[3].data),
                                                                  GraphingUtility.unicode_to_int(basedColumns[4].data),
                                                                  GraphingUtility.unicode_to_int(basedColumns[5].data),
                                                                  GraphingUtility.unicode_to_int(basedColumns[6].data),
                                                                  format_instance.hrm)
                        output.append(energy)
                        colNames.append('Energy xtal temp')
                    elif i == 7:
                        energy = GraphingUtility.temp_corr(data, GraphingUtility.unicode_to_int(basedColumns[5].data),
                                                           GraphingUtility.unicode_to_int(basedColumns[6].data),
                                                           format_instance.hrm)
                        output.append(energy)
                        colNames.append('Temp Corr')
                    elif i == 9:
                        signal = GraphingUtility.signal_normalized(data,
                                                                   GraphingUtility.unicode_to_int(basedColumns[8].data),
                                                                   GraphingUtility.unicode_to_int(
                                                                       basedColumns[10].data))
                        output.append(signal)
                        colNames.append('Signal Normalized')
                    else:
                        norm = GraphingUtility.norm_factors(data, GraphingUtility.unicode_to_int(basedColumns[10].data))
                        output.append(norm)
                        colNames.append('Norm Factors')
                    continue
                else:
                    for idx, column in enumerate(data):
                        if idx == basedColumns[i].data:
                            output.append(data[idx])
                            colNames.append(bools[i].label)
        filename = FileUtility.writeOutput(output, colNames, file_instance.name, '')
    elif outType == 2:
        # same as outType == 3 but with one file (possibly)
        file_instance = db.session.query(DataFile).filter_by(id=int(id)).first()
        cords = json.loads(cordData)
        output = []
        output.append(cords[0])
        output.append(cords[1])
        colNames = []
        colNames.append("Energy")
        colNames.append("Signal")
        if datFName is not None:
            filename = FileUtility.writeOutput(output, colNames, datFName, '')
        else:
            filename = FileUtility.writeOutput(output, colNames, file_instance.name, '')
    elif outType == 3:
        # save sum (data file) locally
        # this is for multiple files
        jidlist = json.loads(id)
        cords = json.loads(cordData)
        output = []
        output.append(cords[0])
        output.append(cords[1])
        colNames = []
        colNames.append("Energy")
        colNames.append("Signal")
        filename = FileUtility.writeOutput(output, colNames, jidlist, datFName)
    elif outType == 4:
        # same as outType == 5 but this is only with one file
        file_instance = db.session.query(DataFile).filter_by(id=int(id)).first()
        cords = json.loads(cordData)
        output = []
        output.append(cords[0])
        output.append(cords[1])
        colNames = []
        colNames.append("Energy")
        colNames.append("Signal")
        filename = FileUtility.writeOutput(output, colNames, datFName, '')
        if DBSave != 0:
            dfile = DataFile()
            dfile.name = datFName
            dfile.path = filename
            dfile.comment = ''
            dfile.authed = current_user.get_id()
            user_instance = db.session.query(User).filter_by(id=current_user.get_id()).first()
            dfile.comChar = user_instance.commentChar
            dfile.type = 'dat'
            currUser = db.session.query(User).filter(User.id == current_user.get_id()).first().username
            parentNode = db.session.query(DataFile).filter(
                and_(DataFile.name == "/" + currUser + "/", DataFile.authed == str(current_user.get_id()))).first()
            dfile.parentID = parentNode.id
            dfile.treeType = "File"
            db.session.add(dfile)
            userFile = UserFiles()
            userFile.file_id = dfile.id
            userFile.user_id = current_user.get_id()
            db.session.add(userFile)
            db.session.commit()
        path = os.path.join(current_app.root_path, 'static/saved_files', "dat", filename)
        with open(path, 'r') as DATfile:
            data = DATfile.read()
        return data
    elif outType == 5:
        # clicked on the save to server button on the sum tab
        # saves the file for the user to look at later
        jidlist = json.loads(id)
        cords = json.loads(cordData)
        output = []
        output.append(cords[0])
        output.append(cords[1])
        colNames = []
        colNames.append("Energy")
        colNames.append("Signal")
        filename = FileUtility.writeOutput(output, colNames, jidlist, datFName)
        if DBSave != 0:
            dfile = DataFile()
            dfile.name = datFName
            dfile.path = filename
            dfile.comment = ''
            dfile.authed = current_user.get_id()
            user_instance = db.session.query(User).filter_by(id=current_user.get_id()).first()
            dfile.comChar = user_instance.commentChar
            dfile.type = 'dat'
            currUser = db.session.query(User).filter(User.id == current_user.get_id()).first().username
            parentNode = db.session.query(DataFile).filter(
                and_(DataFile.name == "/" + currUser + "/", DataFile.authed == str(current_user.get_id()))).first()
            dfile.parentID = parentNode.id
            dfile.treeType = "File"
            db.session.add(dfile)
            userFile = UserFiles()
            userFile.file_id = dfile.id
            userFile.user_id = current_user.id
            db.session.add(userFile)
            db.session.commit()
        path = os.path.join(current_app.root_path, 'static/saved_files', "dat", filename)
        with open(path, 'r') as DATfile:
            data = DATfile.read()
        return data
    elif outType == 6:
        # clicks the "save locally" button the Modify DAT Page
        # outputs the current data file to the user
        DAT = db.session.query(CurrentDAT).filter(CurrentDAT.user_id == current_user.get_id()).first()
        output = []
        data = json.loads(DAT.DAT)
        output.append(data[0])
        output.append(data[1])
        colNames = []
        colNames.append("Energy")
        colNames.append("Signal")
        filename = FileUtility.writeOutput(output, colNames, datFName, '')
    elif outType == 7:
        # clicks the "save to server" button the Modify DAT Page
        # saves the current data file to the current user session table
        DAT = db.session.query(CurrentDAT).filter(CurrentDAT.user_id == current_user.get_id()).first()
        output = []
        data = json.loads(DAT.DAT)
        output.append(data[0])
        output.append(data[1])
        colNames = []
        colNames.append("Energy")
        colNames.append("Signal")
        filename = FileUtility.writeOutput(output, colNames, datFName, '')
        dfile = DataFile()
        dfile.name = datFName + ".dat"
        dfile.path = filename
        dfile.comment = ''
        dfile.authed = current_user.get_id()
        user_instance = db.session.query(User).filter_by(id=current_user.get_id()).first()
        dfile.comChar = user_instance.commentChar
        dfile.type = 'dat'
        currUser = db.session.query(User).filter(User.id == current_user.get_id()).first().username
        parentNode = db.session.query(DataFile).filter(
            and_(DataFile.name == "/" + currUser + "/", DataFile.authed == str(current_user.get_id()))).first()
        dfile.parentID = parentNode.id
        dfile.treeType = "File"
        db.session.add(dfile)
        db.session.commit()
        add_user_file(current_user)
        return datFName

    if datFName is not None:
        return sendOut(filename, datFName)
    else:
        return download_file(filename)


@hrmApp.route('/download_file/<path:filename>', methods=['GET', 'POST'])
@login_required
def download_file(filename):
    current_file = DataFile.query.filter_by(path=filename).first()
    print current_file
    path = os.path.join(current_app.root_path, 'static/saved_files/dat')
    return send_from_directory(directory=path, filename=filename, attachment_filename="data file.txt",
                               as_attachment=True)


@hrmApp.route('/<path:filename>/<displayName>', methods=['GET', 'POST'])
@login_required
def sendOut(filename, displayName):
    path = os.path.join(current_app.root_path, 'static/saved_files/dat')
    if displayName != 'None' and displayName is not None:
        print "first if"
        return send_from_directory(directory=path, filename=filename, as_attachment=True,
                                   attachment_filename=displayName + '.dat')
    else:
        print "second if"
        return send_from_directory(directory=path, filename=filename, as_attachment=True)


@hrmApp.route('/peakFit', methods=['GET', 'POST'])
@login_required
def peak_at_max():
    '''
	Peak fitting function that uses either the file defaults or what the user has done to the file on the format page.

	Currently peak fitting is done using a centroid analysis.  All files are peak fitted before being summed up on the sum page.
	:return:
	'''
    idthis = request.form.get('idnum', type=int)
    fitType = request.form.get('fitType', type=str)
    inputCord = request.form.get('inputCord', type=float)
    fitRange = request.form.get('inputRange', type=float)
    localRange = request.form.get('localRange', type=float)
    sendOut = request.form.get('sendOut', type=int)
    signalType = ' '.join(request.form.get('signal', type=str).split())
    energyType = ' '.join(request.form.get('energy', type=str).split())
    unit = request.form.get('unit', type=str)
    code, ycords, form = GraphingUtility.peakFit(idthis, energyType, signalType, unit, fitType, fitRange, inputCord,
                                                 localRange)
    if sendOut == 1:
        ycords[0] = ycords[0].tolist()
        return json.dumps(ycords)
    return render_template("new_df.html", user=current_user, ses=current_user.current_session, code=code,
                           form=form,
                           shiftVal=str(abs(ycords[0][0])))


@hrmApp.route('/setDAT', methods=['GET', 'POST'])
@login_required
def setDAT():
    '''
	Updates the current DAT file that the user is viewing with a DAT file that was selected.

	This is usually called from the /select page when choosing a DAT file.

	Sets the user's CurrentDAT.
	:return:
	'''
    DAT = request.form.get('DAT', type=str)
    DName = request.form.get('DName', type=str)
    meta = db.metadata
    for table in (meta.sorted_tables):
        if table.name == 'CurrentDAT':
            db.session.execute(table.delete())
    db.session.commit()

    cDAT = CurrentDAT()
    cDAT.user = current_user
    xs = []
    ys = []
    user = db.session.query(User).filter_by(username=current_user.username).first()
    data = DAT.split("\n")
    try:
        data = [x for x in data if not x.startswith(user.commentChar)]
    except TypeError:
        data = [x for x in data if not x.startswith('#')]
    for i in data:
        if not i:
            continue
        line = i.split()
        xs.append(float(line[0]))
        ys.append(float(line[1]))
    DAT = [xs, ys]
    DAT = json.dumps(DAT)
    cDAT.DAT = DAT
    cDAT.originDAT = DAT
    if DName is not None:
        cDAT.DATname = DName
    db.session.add(cDAT)
    db.session.commit()
    return 'Set'


@hrmApp.route('/remBackDAT', methods=['GET', 'POST'])
@login_required
def remBackDAT():
    '''
	Removes the background data from a DAT file based on user specifications.

	Either removes a flat value, a linear value, or a averaged linear value from the DAT data stored in CurrentDAT.

	Updates CurrentDAT with the data for the new line.
	:return:
	Calls /modifyDAT as that will plot the altered CurrentDAT.
	'''
    show = request.form.get('show', type=int)
    flatVal = request.form.get('flatVal', type=int)
    if flatVal != None:
        if show == 0:
            DAT = db.session.query(CurrentDAT).filter(CurrentDAT.user == current_user).first()
            data = json.loads(DAT.DAT)
            for i in range(len(data[1])):
                data[1][i] = data[1][i] - flatVal
            DAT.DAT = json.dumps(data)
            db.session.commit()
            return redirect(url_for('hrm.modifyDAT'))
        else:
            DAT = db.session.query(CurrentDAT).one()
            data = json.loads(DAT.DAT)
            code = GraphingUtility.addLines(data, flatVal)
            return code
    leftX = request.form.get('leftX', type=float)
    leftY = request.form.get('leftY', type=float)
    rightX = request.form.get('rightX', type=float)
    rightY = request.form.get('rightY', type=float)
    if leftX != None:
        if show == 0:
            DAT = db.session.query(CurrentDAT).filter(CurrentDAT.user == current_user).first()
            data = json.loads(DAT.DAT)
            xs = numpy.array([leftX, rightX])
            ys = numpy.array([leftY, rightY])
            slope, intercept = numpy.polyfit(xs, ys, 1)
            tempX = []
            tempY = []
            for i in range(len(data[0])):
                if data[0][i] > leftX and data[0][i] < rightX:
                    tempX.append(data[0][i])
                    tempY.append(data[1][i])
            data[0] = tempX
            data[1] = tempY
            for i in range(len(data[1])):
                data[1][i] = data[1][i] - abs((slope * data[0][i]) + intercept)
            DAT.DAT = json.dumps(data)
            db.session.commit()
            return redirect(url_for('modifyDAT'))
        else:
            DAT = db.session.query(CurrentDAT).filter(CurrentDAT.user == current_user).first()
            data = json.loads(DAT.DAT)
            code = GraphingUtility.addLines(data, [leftX, rightX, leftY, rightY])
            return code
    leftIn = request.form.get('leftIn', type=int)
    rightIn = request.form.get('rightIn', type=int)
    if leftIn != None:
        if show == 0:
            cords = GraphingUtility.calcAverageBack(leftIn, rightIn)
            leftSlope, leftIntercept = numpy.polyfit(numpy.array([cords[0], cords[4]]),
                                                     numpy.array([cords[1], cords[5]]), 1)
            middleSlope, middleIntercept = numpy.polyfit(numpy.array([cords[4], cords[2]]),
                                                         numpy.array([cords[5], cords[3]]), 1)
            rightSlope, rightIntercept = numpy.polyfit(numpy.array([cords[2], cords[6]]),
                                                       numpy.array([cords[3], cords[7]]), 1)
            DAT = db.session.query(CurrentDAT).filter(CurrentDAT.user == current_user).first()
            data = json.loads(DAT.DAT)
            tempX = []
            tempY = []
            for i in range(len(data[0])):
                if data[0][i] > leftIn and data[0][i] < rightIn:
                    tempX.append(data[0][i])
                    tempY.append(data[1][i])
            data[0] = tempX
            data[1] = tempY
            for i in range(len(data[1])):
                if data[0][i] <= cords[4]:
                    data[1][i] = data[1][i] - abs((leftSlope * data[0][i]) + leftIntercept)
                elif data[0][i] <= cords[2]:
                    data[1][i] = data[1][i] - abs((middleSlope * data[0][i] + middleIntercept))
                else:
                    data[1][i] = data[1][i] - abs((rightSlope * data[0][i] + rightIntercept))
            DAT.DAT = json.dumps(data)
            db.session.commit()
            return redirect(url_for('modifyDAT'))
        else:
            DAT = db.session.query(CurrentDAT).filter(CurrentDAT.user == current_user).first()
            data = json.loads(DAT.DAT)
            cords = GraphingUtility.calcAverageBack(leftIn, rightIn)
            code = GraphingUtility.addLines(data, cords)
            leftX = ("%.4f" % cords[5])
            rightX = ("%.4f" % cords[6])
            data = json.dumps([code, leftX, rightX])
            return data
    return redirect(url_for('modifyDAT'))


@hrmApp.route('/resetDAT', methods=['GET', 'POST'])
@login_required
def resetDAT():
    '''Reverts the CurrentDAT back to how it was originally'''
    DAT = db.session.query(CurrentDAT).filter(CurrentDAT.user == current_user).first()
    DAT.DAT = DAT.originDAT
    db.session.commit()
    return redirect(url_for('hrm.modifyDAT'))


@hrmApp.route('/close_plots', methods=['GET', 'POST'])
@login_required
def close_plots():
    '''
	Closes all existing plots.

	As the program is generating a large number of plots quite regularly this is a function to easily allow them to be closed.
	:return:
	'''
    if request.method == 'POST':
        plt.close("all")
    return 'Closed'


@hrmApp.route('/save_graph', methods=['GET', 'POST'])
@login_required
def save_graph():
    '''
	Updates the current session with information that the user has supplied on the data page.

	This session is stored temporarily for each file and is updated whenever a change is made on the data page.
	The data is passed in the InputForm that is defined in forms.py and saved in the CurrentMeta database table.
	:return:
	'''
    form = InputForm(request.form)
    idthis = request.form.get("idnum", type=int)
    if idthis is not None:
        againstE = request.form.get("agaE", type=str)
        file_instance = db.session.query(DataFile).filter_by(id=idthis).first()
        format_instance = db.session.query(CurrentMeta).filter(and_(CurrentMeta.user_id == current_user.get_id(),
                                                                    CurrentMeta.file_id == file_instance.id,
                                                                    CurrentMeta.session == current_user.current_session)).first()

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
