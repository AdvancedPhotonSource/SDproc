__author__ = 'caschmitz'
import os
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['UPLOAD_DIR'] = app.root_path + '/static/dataFiles'
app.secret_key = os.urandom(24)

