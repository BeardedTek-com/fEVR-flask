from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash
from .models import User,frigate,cameras,events
from . import db
from .rndpwd import randpwd
setup = Blueprint('setup', __name__)

@setup.route('/setup/users')
def setupUsers():
    db.create_all()
    
    
    
    if User.query.first() == None:
        return 'No Users'
    else:
        return 'Users Present'
@setup.route('/setup/admin')
def setupAdmin():
    # Sanity checks...
    admin = User.query.filter_by(group='admin').first()
    if admin: # If an admin already exists, then go to signup page instead.
        flash(f"An admin account already exists.<br/>Please sign up for a regular user account.")
        return redirect(url_for('auth.signup'))
    else:
        return render_template('setupadmin.html',passwd = randpwd.generate())

@setup.route('/setup/admin', methods=['POST'])
def setupAdminProcessForm():
    # Sanity checks...
    admin = User.query.filter_by(group='admin').first()
    if admin: # If an admin already exists, then go to signup page instead.
        flash('There can be only one!')
        return redirect(url_for('auth.signup'))
    else:
        # code to validate and add user to database goes here
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        retypePassword = request.form.get('retypePassword')

        if password != retypePassword: # Do passwords match?
            flash('Passwords do not match.')
            return redirect(url_for('setup.setupAdmin'))
        
        email = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database
        if email: # if a user is found, we want to redirect back to signup page so user can try again
            flash('Email Already Exists.')
            return redirect(url_for('setup.setupAdmin'))
        
        username = User.query.filter_by(name=name).first()
        if username: # Does this username already exist?
            flash('Username Taken')
        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), group='admin', enabled=True, resetpwd=False)

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))