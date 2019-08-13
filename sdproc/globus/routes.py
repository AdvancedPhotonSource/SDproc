import json
from dm import ExperimentDsApi, FileCatApi
from flask import Blueprint
from flask_login import login_required, current_user


globus = Blueprint('globus', __name__)


exApi = ExperimentDsApi(username='user3id', password='j7g$MAC;kG', url='https://xraydtn01.xray.aps.anl.gov:22236')
fApi = FileCatApi(username='user3id', password='j7g$MAC;kG', url='https://s3iddm.xray.aps.anl.gov:44436')


@globus.route('/globus_tree', methods=['GET', 'POST'])
@login_required
def globus_tree():
    tree_data = []
    curr_user = current_user.id
    folder_list = []
    folder = None
    experiments = exApi.getExperimentsByStation("3ID")

    for e in experiments:
        try:
            folder = e['rootPath']
        except Exception, e:
            folder = None
        if folder is not None:
            if folder not in folder_list:
                folder_list.append(folder)

    tree_data.append({"text": "3ID", "id": 0, "parent": "#", "type": "Root"})

    x = 1
    for f in folder_list:
        tree_data.append({"text": f, "id": x, "parent": 0, "type": "Folder"})
        x += 1



    with open('static/globus_tree.json', 'w') as outfile:
        json.dump(tree_data, outfile)

    return json.dumps(tree_data)


def add_experiment_files(experiment, tree_data, xid):
    files = fApi.getExperimentFiles(experiment)

    x = 1
    for f in files:
        tree_data.append({"text": f['fileName'], "id": x, "parent": xid, "type": "File"})
        x += 1

    return tree_data
