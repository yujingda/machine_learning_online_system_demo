from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__, template_folder='../templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:qwedsaq123@localhost/dbname'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
# db.create_all()
from app.auth import auth_bp as auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')
