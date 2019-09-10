import json
from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from db.db_model import db, HRM, CurrentMeta
from sqlalchemy import and_


hrms = Blueprint('hrms', __name__)

@hrms.route('/hrmInfo', methods=['GET', 'POST'])
@login_required
def hrmInfo():
    '''
	Supplementary template generator method for admin.

	Provides additional information about a HRM.

	This is done by querying the sqlite database 'HRM' based on the ID given.
	:return:
	'''
    hrmID = request.form.get('id', type=int)
    hrmInfo = db.session.query(HRM).filter_by(id=hrmID).first()
    hrmData = {'name': hrmInfo.name, 'hrm_e0': hrmInfo.hrm_e0, 'hrm_bragg1': hrmInfo.hrm_bragg1,
               'hrm_bragg2': hrmInfo.hrm_bragg2, 'hrm_geo': hrmInfo.hrm_geo,
               'hrm_alpha1': hrmInfo.hrm_alpha1, 'hrm_alpha2': hrmInfo.hrm_alpha2,
               'hrm_theta1_sign': hrmInfo.hrm_theta1_sign, 'hrm_theta2_sign': hrmInfo.hrm_theta2_sign}
    return render_template('admin.html', user=current_user, hrmData=hrmData)


@hrms.route('/addHRM', methods=['GET', 'POST'])
@login_required
def addHRM():
    '''
	Supplementary template updater method for admin.

	Adds a HRM with the details provided by the user.

	This is done by adding a new entry in the sqlite database 'HRM'.
	:return:
	'''
    id = request.form.get('id', type=int)
    hrm = db.session.query(HRM).filter_by(id=id).first()
    if hrm is None:
        hrm = HRM()
        hrm.id = request.form.get('id', type=int)
        hrm.name = request.form.get('name', type=str)
        hrm.hrm_e0 = request.form.get('hrm_e0', type=float)
        hrm.hrm_bragg1 = request.form.get('hrm_bragg1', type=float)
        hrm.hrm_bragg2 = request.form.get('hrm_bragg2', type=float)
        hrm.hrm_geo = request.form.get('hrm_geo', type=str)
        hrm.hrm_alpha1 = request.form.get('hrm_alpha1', type=float)
        hrm.hrm_alpha2 = request.form.get('hrm_alpha2', type=float)
        hrm.hrm_theta1_sign = request.form.get('hrm_theta1_sign', type=int)
        hrm.hrm_theta2_sign = request.form.get('hrm_theta2_sign', type=int)
        db.session.add(hrm)
        db.session.commit()
    else:
        hrm.id = request.form.get('id', type=int)
        hrm.name = request.form.get('name', type=str)
        hrm.hrm_e0 = request.form.get('hrm_e0', type=float)
        hrm.hrm_bragg1 = request.form.get('hrm_bragg1', type=float)
        hrm.hrm_bragg2 = request.form.get('hrm_bragg2', type=float)
        hrm.hrm_geo = request.form.get('hrm_geo', type=str)
        hrm.hrm_alpha1 = request.form.get('hrm_alpha1', type=float)
        hrm.hrm_alpha2 = request.form.get('hrm_alpha2', type=float)
        hrm.hrm_theta1_sign = request.form.get('hrm_theta1_sign', type=int)
        hrm.hrm_theta2_sign = request.form.get('hrm_theta2_sign', type=int)
        db.session.commit()
        return 'Updated'
    return 'Added'


@hrms.route('/updateHRM', methods=['GET', 'POST'])
@login_required
def updateHRM():
    '''
	Sets the HRM to one of the static parameter sets in the HRM database

	HRM is used primarily with energy_xtal, energy_xtal_temp, and temp_corr on the /format page.
	:return:
	'''
    idthis = request.form.get('idnum', type=int)
    hrm = request.form.get('hrm', type=str)
    format_instance = db.session.query(CurrentMeta).filter(and_(CurrentMeta.user_id == current_user.get_id(),
                                                                CurrentMeta.file_id == idthis,
                                                                CurrentMeta.session == current_user.current_session)).first()
    hrmInstance = db.session.query(HRM).filter_by(name=hrm).first()
    hrm = {'name': hrmInstance.name, 'hrm_e0': hrmInstance.hrm_e0, 'hrm_bragg1': hrmInstance.hrm_bragg1,
           'hrm_bragg2': hrmInstance.hrm_bragg2, 'hrm_geo': hrmInstance.hrm_geo, 'hrm_alpha1': hrmInstance.hrm_alpha1,
           'hrm_alpha2': hrmInstance.hrm_alpha2, 'hrm_theta1_sign': hrmInstance.hrm_theta1_sign,
           'hrm_theta2_sign': hrmInstance.hrm_theta2_sign}
    hrm = json.dumps(hrm)
    format_instance.hrm = hrm
    db.session.commit()
    return hrmInstance.name
