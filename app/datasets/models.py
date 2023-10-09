from app import db
from flask_login import UserMixin

class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500))
    upload_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_path = db.Column(db.String(300), nullable=False)

    def __repr__(self):
        return f'<Dataset {self.name}>'
