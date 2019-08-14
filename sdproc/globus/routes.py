import json
from dm import ExperimentDsApi, FileCatApi
from flask import Blueprint
from flask_login import login_required
from db.db_model import db, GlobusTree


globus = Blueprint('globus', __name__)


exApi = ExperimentDsApi(username='user3id', password='j7g$MAC;kG', url='https://xraydtn01.xray.aps.anl.gov:22236')
fApi = FileCatApi(username='user3id', password='j7g$MAC;kG', url='https://s3iddm.xray.aps.anl.gov:44436')


@globus.route('/globus_tree', methods=['GET', 'POST'])
@login_required
def globus_tree():
    tree_data = [{"text": "3ID", "id": 0, "parent": "#", "type": "Root"}]
    # folder_list = []
    # # user_id = "d65218"
    # experiments = exApi.getExperimentsByStation("3ID")
    #
    # # nodes = GlobusTree.query.all()
    # # if nodes is not None:
    # #     for n in nodes:
    # #         db.session.delete(n)
    # #     db.session.commit()
    # #
    # # print("done deleting db")
    #
    # """ Getting Experiments and finding their parent folders"""
    # for e in experiments:
    #     ex = exApi.getExperimentByName(e['name'])
    #     try:
    #         folder = e['rootPath']
    #     except Exception, e:
    #         folder = None
    #     if folder is not None:
    #         if folder not in folder_list:
    #             folder_list.append(folder + "-new")
    #
    # # adding parent folders of experiments to the db
    # for f in folder_list:
    #     node = GlobusTree(name=f, parent=0, type="Folder")
    #     db.session.add(node)
    #     db.session.commit()
    # print("added parent folders of experiments")
    #
    # # adding experiments to the db
    # for e in experiments:
    #     f_name = e['name'] + "-new"
    #     try:
    #         folder = e['rootPath'] + "-new"
    #     except Exception, e:
    #         folder = None
    #     if folder is not None:
    #         parent = GlobusTree.query.filter_by(name=folder).first()
    #         node = GlobusTree(name=f_name, parent=parent.id, type="Folder")
    #     else:
    #         node = GlobusTree(name=f_name, parent=0, type="Folder")
    #     db.session.add(node)
    #     db.session.commit()
    # print("added experiments to db")
    #
    # # adding files to db
    # # parent = GlobusTree.query.filter_by(name="DeBeer-201812").first()
    # # files = fApi.getExperimentFiles("DeBeer-201812")
    # # for f in files:
    # #     if f['fileName'][-3:] == 'dat' or f['fileName'][-3:] == 'mda':
    # #         node = GlobusTree(name=f['fileName'], parent=parent.id, type="File")
    # #         db.session.add(node)
    # #         db.session.commit()
    # for e in experiments:
    #     name = e['name']
    #     files = fApi.getExperimentFiles(name)
    #     parent = GlobusTree.query.filter_by(name=(name + "-new")).first()
    #     print parent
    #     for f in files:
    #         if f['fileName'][-3:] == 'dat' or f['fileName'][-3:] == 'mda':
    #             node = GlobusTree(name=f['fileName'] + "-new", parent=parent.id, type="File")
    #             db.session.add(node)
    #             db.session.commit()
    # print("added files to db")

    nodes = GlobusTree.query.all()
    for n in nodes:
        tree_data.append({"text": n.name, "id": n.id, "parent": n.parent, "type": n.type})
    print("added nodes to list")

    # with open('static/globus_tree.json', 'w') as outfile:
    #     json.dump(tree_data, outfile)

    return json.dumps(tree_data)


def add_experiment_files(experiment, tree_data, xid):
    files = fApi.getExperimentFiles(experiment)

    x = 1
    for f in files:
        tree_data.append({"text": f['fileName'], "id": x, "parent": xid, "type": "File"})
        x += 1

    return tree_data
