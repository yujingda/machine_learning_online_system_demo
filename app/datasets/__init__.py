from flask import Blueprint

datasets_blueprint = Blueprint('datasets', __name__)

from app.datasets import views