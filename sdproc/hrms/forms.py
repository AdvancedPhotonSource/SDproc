from flask_wtf import FlaskForm
from flask import session
from wtforms import BooleanField, IntegerField, StringField, FloatField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from db.db_model import HRM


class AddHRMForm(FlaskForm):
    hrm_name = StringField(label='HRM Name', validators=[DataRequired()])
    hrm_e0 = FloatField(label='HRM e0', validators=[DataRequired()])
    hrm_bragg1 = FloatField(label='HRM bragg1', validators=[DataRequired()])
    hrm_bragg2 = FloatField(label='HRM bragg2', validators=[DataRequired()])
    hrm_geo = StringField(label='HRM geo', validators=[DataRequired()])
    hrm_alpha1 = FloatField(label='HRM alpha1', validators=[DataRequired()])
    hrm_alpha2 = FloatField(label='HRM alpha2', validators=[DataRequired()])
    hrm_theta1_sign = IntegerField(label='HRM theta1 sign', validators=[DataRequired()])
    hrm_theta2_sign = IntegerField(label='HRM theta2 sign', validators=[DataRequired()])
    submit = SubmitField(label='Add HRM')

    @staticmethod
    def validate_hrm_name(self, hrm_name):
        hrm = HRM.query.filter_by(name=hrm_name.data).first()
        if hrm:
            raise ValidationError('That hrm name is already taken. Please choose a different one.')


class UpdateHRMForm(FlaskForm):
    hrm_name = StringField(label='HRM Name', validators=[DataRequired()])
    hrm_e0 = FloatField(label='HRM e0', validators=[DataRequired()])
    hrm_bragg1 = FloatField(label='HRM bragg1', validators=[DataRequired()])
    hrm_bragg2 = FloatField(label='HRM bragg2', validators=[DataRequired()])
    hrm_geo = StringField(label='HRM geo', validators=[DataRequired()])
    hrm_alpha1 = FloatField(label='HRM alpha1', validators=[DataRequired()])
    hrm_alpha2 = FloatField(label='HRM alpha2', validators=[DataRequired()])
    hrm_theta1_sign = IntegerField(label='HRM theta1 sign', validators=[DataRequired()])
    hrm_theta2_sign = IntegerField(label='HRM theta2 sign', validators=[DataRequired()])
    submit = SubmitField(label='Update HRM')

    @staticmethod
    def validate_hrm_name(self, hrm_name):
        if 'admin_hrm' in session:
            currHrmName = session['admin_hrm']
            if hrm_name.data != currHrmName:
                hrm = HRM.query.filter_by(name=hrm_name.data).first()
                if hrm:
                    raise ValidationError('That hrm name is taken. Please choose a different one.')


class InputForm(FlaskForm):
    # Fields
    energy = IntegerField(label='Energy: ', default=1, validators=[DataRequired()])
    energyCalc = IntegerField(label='Energy calculated')
    energyTempCalc = IntegerField(label='Energy calculated w/T')
    xtal1A = IntegerField(label='Xtal 1 angle: ', default=2, validators=[DataRequired()])
    xtal2A = IntegerField(label='Xtal 2 angle: ', default=3, validators=[DataRequired()])
    xtal1T = IntegerField(label='Xtal 1 temp: ', default=12, validators=[DataRequired()])
    xtal2T = IntegerField(label='Xtal 2 temp: ', default=15, validators=[DataRequired()])
    tempCorr = IntegerField(label='Temp. corr')
    signal = IntegerField(label='Signal: ', default=11, validators=[DataRequired()])
    signalNorm = IntegerField(label='Signal normalized')
    norm = IntegerField(label='Norm.: ', default=7, validators=[DataRequired()])
    normFac = IntegerField(label='Norm. factors')
    extra = IntegerField(label='Extra: ', default=1, validators=[DataRequired()])

    # columns = [energy, energyCalc, xtal1A, xtal2A, xtal1T, xtal2T, tempCorr, signal, signalNorm, norm, normFac, extra]

    # Assign labels so that an equality check can still be used between columns and bools
    ebool = BooleanField(label='energy', default=False)
    ecbool = BooleanField(label='energyCalc', default=False)
    etcbool = BooleanField(label='energyTempCalc', default=False)
    a1bool = BooleanField(label='xtal1A', default=False)
    a2bool = BooleanField(label='xtal2A', default=False)
    t1bool = BooleanField(label='xtal1T', default=False)
    t2bool = BooleanField(label='xtal2T', default=False)
    tcbool = BooleanField(label='tempCorr', default=False)
    sbool = BooleanField(label='signal', default=True)
    snbool = BooleanField(label='signalNorm', default=False)
    nbool = BooleanField(label='norm', default=False)
    nfbool = BooleanField(label='normFac', default=False)
    xbool = BooleanField(label='extra', default=False)

    # bools = [ebool, ecbool, a1bool, a2bool, t1bool, t2bool, tcbool, sbool, snbool, nbool, nfbool, xbool]
