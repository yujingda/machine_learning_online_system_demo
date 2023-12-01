from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
import os

app = Flask(__name__, template_folder='../templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ml_flask:qwedsaq123!@localhost/ml_online'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
csrf = CSRFProtect()
csrf.init_app(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)

from app.logger_config import setup_logging
setup_logging()
from app.auth import auth_bp as auth_bp
# from app.datasets.models import *
# with app.app_context():
#     db.create_all()
app.register_blueprint(auth_bp)
from app.datasets.views import datasets_blueprint as datasets_bp
app.register_blueprint(datasets_bp, url_prefix='/datasets')
