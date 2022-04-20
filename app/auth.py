from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import User
from . import db

class apiAuth:
    def exe():
        user_agent = request.headers.get('User-Agent')
        if 'python-requests' in user_agent and request.remote_addr == '192.168.101.2' or request.remote_addr == '127.0.0.1':
            return True
        else:
            return False


auth = Blueprint('auth', __name__)

@auth.route('/login',methods=['GET'])
def login():
    fwd = "/"
    fwdName = "access fEVR"
    fwd = request.args.get('next')
    if fwd != None:
        fwd.replace('%2F','/')
        values = {"/": "access fEVR", "/event":"view this event","/events":"view events"}
        for val in values:
            if fwd == val:
                fwdName = values[val]
    return render_template('login.html',fwd=fwd,fwdName=fwdName)
    
@auth.route('/login', methods=['POST'])
def loginProcessForm():
    
    # login code goes here
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    fwd = request.form.get('fwd')

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page
    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(fwd)

@auth.route('/signup')
def signup():
    db.create_all()
    if User.query.first() == None:
        return render_template('setupadmin.html',type='admin')
    else:
        return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signupProcessForm():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address exists.  Did you forget your password?')
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/logout',methods=['GET'])
@login_required
def logout():
    fwd = "/"
    fwd = request.args.get('page')
    if fwd != None:
        fwd.replace('%2F','/')
    logout_user()
    return redirect(fwd)