from flask import render_template, request, redirect, url_for, send_file, session, flash
from app import db, bcrypt
from app.models import User
from app.auth import auth_bp

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))  # redirect to login page after successful registration
    return render_template('auth/register.html')
    # return "hello world"


@auth_bp.route ('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get ('username')
        password = request.form.get ('password')

        # Query the database for the user
        user = User.query.filter_by (username=username).first ()

        # Check if the user exists and the password is correct
        if user and bcrypt.check_password_hash (user.password, password):
            session['logged_in'] = True
            session['username'] = username
            flash ('成功登录，即将跳转主页！', 'success')
            return redirect (url_for ('home'))
        else:
            flash ('用户名或密码无效！', 'danger')

    return render_template ('auth/login.html')