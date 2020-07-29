import json
from dm import ExperimentDsApi, FileCatApi
from flask import Blueprint, request
from flask_login import login_required, current_user
from sdproc.dm.utils import get_download, add_exp_to_root, lazy_load

dm = Blueprint('dm', __name__)


exApi = ExperimentDsApi(username='user3id', password='j7g$MAC;kG', url='https://xraydtn01.xray.aps.anl.gov:22236')
fApi = FileCatApi(username='user3id', password='j7g$MAC;kG', url='https://s3iddm.xray.aps.anl.gov:44436')


@dm.route('/get_dm_file', methods=['GET', 'POST'])
@login_required
def dm_file():
    path = request.form.get("path")
    exp = request.form.get('exp')
    type = request.form.get('type')
    station = request.form.get('station')

    get_download(station, path, exp, type)

    return "Done"


@dm.route('/3id_tree', methods=['GET', 'POST'])
@login_required
def station_3id():
    exp_nm = request.args.get('id')
    parent = exp_nm

    new_data = []

    if exp_nm == '#':
        new_data = [{"text": "3ID", "id": "3ID", "parent": "#", "type": "Root",
                     "state": {"opened": "true", "disabled": "true"}}]

        new_data = add_exp_to_root("3ID", new_data)
    else:
        lazy_load("3ID", exp_nm, current_user.badge_number, parent, new_data)

    return json.dumps(new_data)


@dm.route('/30id_tree', methods=['GET', 'POST'])
@login_required
def station_30id():
    exp_nm = request.args.get('id')
    parent = exp_nm

    new_data = []

    if exp_nm == '#':
        new_data = [{"text": "30ID", "id": "30ID", "parent": "#", "type": "Root",
                     "state": {"opened": "true", "disabled": "true"}}]

        new_data = add_exp_to_root("30ID", new_data)
    else:
        lazy_load("30ID", exp_nm, current_user.badge_number, parent, new_data)

    return json.dumps(new_data)
