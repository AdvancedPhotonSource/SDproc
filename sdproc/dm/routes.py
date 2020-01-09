import json
from dm import ExperimentDsApi, FileCatApi
from flask import Blueprint, request
from flask_login import login_required, current_user
from sdproc.dm.utils import save_file, do_fold

dm = Blueprint('dm', __name__)


exApi = ExperimentDsApi(username='user3id', password='j7g$MAC;kG', url='https://xraydtn01.xray.aps.anl.gov:22236')
fApi = FileCatApi(username='user3id', password='j7g$MAC;kG', url='https://s3iddm.xray.aps.anl.gov:44436')


@dm.route('/get_dm_file', methods=['GET', 'POST'])
@login_required
def dm_file():
    path = request.form.get("path")
    exp = request.form.get('exp')
    type = request.form.get('type')

    download = exApi.downloadFile(path, exp, "./static/uploaded_files/" + type + "/")
    save_file(download)

    return "Done"


@dm.route('/dm_tree', methods=['GET', 'POST'])
@login_required
def dm_tree():
    exp_nm = request.args.get('id')
    parent = exp_nm

    new_data = []

    if exp_nm == '#':
        new_data = [{"text": "3ID", "id": "3ID", "parent": "#", "type": "Root",
                     "state": {"opened": "true", "disabled": "true"}}]

        experiments = exApi.getExperimentsByStation("3ID")

        for e in experiments:
            exp = e['name']
            try:
                root = e['rootPath']
            except KeyError:
                root = None

            if root is not None:
                if not any(obj['text'] == root for obj in new_data):
                    new_data.append({"text": root, "id": root, "parent": "3ID", "type": "Folder"})
                new_data.append({"text": exp, "id": exp, "parent": root, "type": "Folder", "children": True})
            else:
                new_data.append({"text": exp, "id": exp, "parent": "3ID", "type": "Folder", "children": True})
    else:
        e = exApi.getExperimentByName(exp_nm)
        if 'd' + str(current_user.badge_number) in e['experimentUsernameList'] or current_user.badge_number == 300123:
            files = fApi.getExperimentFiles(exp_nm)
            for f in files:
                filePath = f['experimentFilePath']
                folders = filePath.split("/")
                fID = f['id']
                do_fold(folders, parent, new_data, fID, exp_nm, filePath)

    return json.dumps(new_data)
