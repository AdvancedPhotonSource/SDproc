
import uuid
from flask import Blueprint, redirect, url_for, render_template, request, flash
from flask_login import login_required, current_user
from sdproc.sessions.forms import SessionForm, UpdateSessionForm
from sdproc.files.utils import file_path
from db.db_model import db, SessionFiles, DataFile, HRM, CurrentMeta, CurrentDAT

from sdproc.hrms.forms import InputForm
from utilities.graphing_utility import GraphingUtility
from utilities.sdproc_mpld3.hide_legend import HideLegend
from utilities.file_utility import FileUtility
from utilities.sdproc_mpld3.interactive_legend import InteractiveLegend
import mpld3
from sqlalchemy import and_
import numpy
import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

scans = Blueprint('scans', __name__)


@scans.route('/scans', methods=['POST'])
@login_required
def dataFormat():
    """
    Template generator for the data page. Has a multitude of options that allow the user to display file information
    in the form of a plot. Options are saved to a live-updated session for each respective file that persists through
    temporarily leaving the page. Defaults are assigned to all files within this method.
    :return:
    """
    form = SessionForm()
    if form.validate_on_submit():
        session = SessionFiles(name=form.session_name.data, user_id=current_user.id, user=current_user,
                               comment=form.comments.data)
        current_user.current_session = session.name
        db.session.add(session)
        db.session.commit()
        flash("Your session has been saved!", "success")
        return redirect(url_for("scans.dataFormat"))
    elif request.method == 'GET':
        pass
    user = current_user
    thisSession = current_user.current_session
    if thisSession != 'None':
        comments = SessionFiles.query.filter_by(name=thisSession).first().comment
    else:
        comments = "No comments"
    findPlot = request.form.get('plot', type=int)
    unit = request.form.get('unit', type=str)
    nameID = str(uuid.uuid4())

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
        file_instance = DataFile.query.filter_by(id=idthis).first()
        format_instance = db.session.query(CurrentMeta).filter(and_(CurrentMeta.user_id == current_user.get_id(),
                                                                    CurrentMeta.file_id == file_instance.id,
                                                                    CurrentMeta.session ==
                                                                    current_user.current_session)).first()
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
            if file_instance.type == 'mda':
                path = file_path("." + file_instance.type, file_instance.path)
                data, name, unusedpath = FileUtility.readMda(path)
            else:
                path = file_path("." + file_instance.type, file_instance.path)
                data, name, unusedpath = FileUtility.readAscii(path, file_instance.comChar)

            etype = data[1]
            print "etype: " + etype
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
                           ses=thisSession,
                           comments=comments)
