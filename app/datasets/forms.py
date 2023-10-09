from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms import SelectMultipleField, RadioField, SubmitField
from wtforms.validators import DataRequired

class DatasetForm(FlaskForm):
    name = StringField('Dataset Name', validators=[DataRequired()])
    description = StringField('Description')
    file = FileField('Dataset File', validators=[DataRequired()])
    submit = SubmitField('Submit')


class MergeForm(FlaskForm):
    datasets = SelectMultipleField('Select Datasets', validators=[DataRequired()])
    merge_method = RadioField('Merge Method', choices=[('horizontal', 'Horizontal'), ('vertical', 'Vertical')], validators=[DataRequired()])
    submit = SubmitField('Merge')