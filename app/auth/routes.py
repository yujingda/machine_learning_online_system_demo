from flask import render_template, request, redirect, url_for, send_file, session, flash
from app import db, bcrypt
from app.models import User
from app.auth import auth_bp

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get ('username')
        email = request.form.get ('email')
        password = request.form.get ('password')
        user_identity = request.form.get ('user_identity')
        invitation_code = request.form.get ('invitation_code')

        existing_user = User.query.filter_by (username=username).first ()
        if existing_user:
            flash ('用户名已被使用!', 'danger')
            return redirect (url_for ('auth.register'))
        # Check if the user is registering as an administrator
        if user_identity == 'administrator':
            if invitation_code != '11111111aaa':
                flash ('请输入有效的邀请码!', 'danger')
                return redirect (url_for (
                    'auth.register'))  # Assuming you have a route named 'register_page' for the registration form

        # hashed_password = bcrypt.generate_password_hash (password).decode ('utf-8')
        # Save the user data to the database (pseudo-code)
        user = User(username=username, email=email, password='0', identity=user_identity)
        user.set_password (password)
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