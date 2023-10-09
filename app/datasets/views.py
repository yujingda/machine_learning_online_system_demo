import os

import pandas as pd
from flask import redirect, url_for, flash, render_template, jsonify, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
# from sqlalchemy.orm import a

from app import db
from app.datasets import datasets_blueprint
from app.datasets import models, forms
from app.datasets.forms import DatasetForm, MergeForm
from app.datasets.models import Dataset
from app.logger_config import logger


@datasets_blueprint.route('/home')
@login_required
def homepage():
    if current_user.is_admin:
        datasets = models.Dataset.query.all()
    else:
        datasets = models.Dataset.query.filter_by(uploader_id=current_user.id).all()
    return render_template('datasets/homepage.html', datasets=datasets)


@datasets_blueprint.route('/upload', methods=['POST'])
@login_required
def upload_dataset():
    form = forms.DatasetForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file_path = os.path.join('path/to/datasets', filename)
        file.save(file_path)

        dataset = models.Dataset(
            name=form.name.data,
            description=form.description.data,
            uploader_id=current_user.id,
            file_path=file_path
        )
        db.session.add(dataset)
        db.session.commit()
        logger.info(f'User {current_user.username} uploaded dataset: {form.name.data}')
        return jsonify(status='success', msg='Dataset uploaded successfully')
    else:
        logger.error(f'Upload failed for user {current_user.username}, errors: {form.errors}')
    return jsonify(status='error', msg='Validation failed')


@datasets_blueprint.route('/delete/<int:dataset_id>', methods=['POST'])
@login_required
def delete_dataset(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)

    # Check if the current user is the uploader or an admin
    if current_user.id != dataset.uploader_id and not current_user.is_admin:
        flash('You do not have permission to delete this dataset.', 'danger')
        return redirect(url_for('datasets.homepage'))

    file_path = dataset.file_path

    # Check if the file exists
    if not os.path.exists(file_path):
        return jsonify(status='error', msg='File does not exist')

    # Delete the file
    try:
        os.remove(file_path)
        db.session.delete(dataset)
        db.session.commit()
        flash('Dataset deleted successfully.', 'success')
        logger.info(f'User {current_user.username} deleted dataset {dataset.name} (ID: {dataset.id})')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting dataset {dataset.name} (ID: {dataset.id}) by user {current_user.username}, Error: {str(e)}')
    return redirect(url_for('datasets.homepage'))


@datasets_blueprint.route('/update/<int:dataset_id>', methods=['POST'])
@login_required
def update_dataset(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)

    # Check if the current user is the uploader or an admin
    if current_user.id != dataset.uploader_id and not current_user.is_admin:
        return jsonify(status='error', msg='You do not have permission to update this dataset.')

    form = DatasetForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file_path = os.path.join('path/to/datasets', filename)
        file.save(file_path)  # Overwrite the existing file

        # Update dataset metadata in the database
        try:
            dataset.name = form.name.data
            dataset.description = form.description.data
            dataset.file_path = file_path  # Update the file path if the filename has changed
            db.session.commit()
            logger.info(f'User {current_user.username} updated dataset {dataset.name} (ID: {dataset.id})')
            return jsonify(status='success', msg='Dataset updated successfully.')
        except Exception as e:
            db.session.rollback()
            logger.error(
            f'Error updating dataset {dataset.name} (ID: {dataset.id}) by user {current_user.username}, Error: {str (e)}')
    return jsonify(status='error', msg='Validation failed')


@datasets_blueprint.route('/download/<int:dataset_id>', methods=['GET'])
@login_required
def download_dataset(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)

    # Check if the current user is the uploader or an admin
    if current_user.id != dataset.uploader_id and not current_user.is_admin:
        flash('You do not have permission to download this dataset.', 'danger')
        return redirect(url_for('datasets.homepage'))

    file_path = dataset.file_path

    # Check if the file exists
    if not os.path.exists(file_path):
        flash('File does not exist.', 'danger')
        logger.error(
            f'Error downloading dataset {dataset.name} (ID: {dataset.id}) by user {current_user.username}, Error: File does not exist.')
        return redirect(url_for('datasets.homepage'))
    logger.info(f'User {current_user.username} downloaded dataset {dataset.name} (ID: {dataset.id})')
    return send_file(file_path, as_attachment=True)


@datasets_blueprint.route('/info/<int:dataset_id>', methods=['GET'])
@login_required
def dataset_info(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)

    # Check if the current user is the uploader or an admin
    if current_user.id != dataset.uploader_id and not current_user.is_admin:
        return jsonify(status='error', msg='You do not have permission to view this dataset.')

    # Serialize dataset information to JSON
    dataset_info_send = {
        'name': dataset.name,
        'description': dataset.description,
        'upload_date': dataset.upload_date.strftime('%Y-%m-%d %H:%M:%S'),
        'uploader': dataset.uploader.username
        # ... add any other necessary fields
    }

    return jsonify(status='success', dataset_info=dataset_info_send)


@datasets_blueprint.route('/preview/<int:dataset_id>', methods=['GET'])
@login_required
def dataset_preview(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)

    # Check if the current user is the uploader or an admin
    if current_user.id != dataset.uploader_id and not current_user.is_admin:
        flash('You do not have permission to view this dataset.', 'danger')
        return redirect(url_for('datasets.homepage'))

    file_path = dataset.file_path

    # Check if the file exists
    if not os.path.exists(file_path):
        flash('File does not exist.', 'danger')
        return redirect(url_for('datasets.homepage'))

    # Read the dataset using pandas
    df = pd.read_csv(file_path)

    # Gather the required statistical information
    stats = {
        'total_rows': len(df),
        'rows_with_null': df.isnull().any(axis=1).sum(),
        'nulls_per_column': df.isnull().sum().to_dict(),
        'num_feature_columns': df.shape[1],
        'unique_values_per_column': df.nunique().to_dict(),
        'rows_after_deduplication': len(df.drop_duplicates()),
        'total_categories': df['category_column'].nunique() if 'category_column' in df.columns else None,
        'rows_per_category': df['category_column'].value_counts().to_dict() if 'category_column' in df.columns else None,
        'preview_lines': df.head(10).to_string(index=False)
    }
    logger.info(f'User {current_user.username} viewed dataset {dataset.name} (ID: {dataset.id})')
    return render_template('datasets/preview.html', stats=stats)


@datasets_blueprint.route('/merge', methods=['GET', 'POST'])
@login_required
def merge_datasets():
    form = MergeForm()
    if form.validate_on_submit():
        dataset_ids = form.datasets.data  # Assumes dataset IDs are submitted as a list of strings
        merge_method = form.merge_method.data

        datasets = Dataset.query.filter(Dataset.id.in_(dataset_ids)).all()
        df_list = [pd.read_csv(dataset.file_path) for dataset in datasets]

        if merge_method == 'horizontal':
            merged_df = pd.concat(df_list, axis=1)
        else:
            # Check for equal number of columns and matching column names
            col_counts = {len(df.columns) for df in df_list}
            col_names = {tuple(df.columns) for df in df_list}

            if len(col_counts) > 1:
                flash('Datasets have different numbers of columns. Vertical merge is not possible.', 'danger')
                return redirect(url_for('datasets.merge_datasets'))
            elif len(col_names) > 1:
                flash('Datasets have mismatched column names. Confirm merge?', 'warning')
                # Add logic to re-render form with a confirmation prompt or handle confirmation response
                return redirect(url_for('datasets.merge_datasets'))

            merged_df = pd.concat(df_list, axis=0)

        # Save merged dataset to a new file
        merged_file_path = os.path.join('path/to/datasets', 'merged_dataset.csv')
        merged_df.to_csv(merged_file_path, index=False)

        # Add new merged dataset record to the database
        new_dataset = Dataset(
            name='Merged Dataset',
            description='Merged dataset created from datasets: ' + ', '.join([dataset.name for dataset in datasets]),
            uploader_id=current_user.id,
            file_path=merged_file_path
        )
        db.session.add(new_dataset)
        db.session.commit()
        logger.info(f'User {current_user.username} merged datasets with IDs: {dataset_ids}, Result: {new_dataset.id}')
        flash('Datasets merged successfully.', 'success')
        return redirect(url_for('datasets.homepage'))

    return render_template('datasets/merge.html', form=form)






