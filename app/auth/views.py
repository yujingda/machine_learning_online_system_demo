from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from . import auth_bp
from .forms import LoginForm, RegistrationForm
from .models import User



@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        if form.is_admin.data:
            user.is_admin = True
        else:
            user.is_admin = False
        db.session.add(user)
        db.session.commit()
        flash('Your registration is complete. You can now login.', 'success')
        return redirect(url_for('auth.login'))
    else:
        # Here, the form has some validation errors.
        # We will flash each error.
        for field, errors in form.errors.items ():
            for error in errors:
                flash (error, 'danger')

    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('datasets.homepage'))

        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth/login.html'))
