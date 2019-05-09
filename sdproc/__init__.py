from flask_bcrypt import Bcrypt
from flask_app import app

bcrypt = Bcrypt()
bcrypt.init_app(app)
