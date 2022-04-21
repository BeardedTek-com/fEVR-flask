from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required
from werkzeug.security import generate_password_hash
from .models import User,frigate,cameras,events,apiAuth,config
import sqlalchemy
from . import db
from .rndpwd import randpwd
setup = Blueprint('setup', __name__)

@setup.route('/setup/<Item>')
@login_required
def setupfEVR(Item):
    status = {'db':{'frigate':False,'cameras':False,'User':False,'apiAuth':False,'config':False}}
    tables = {
        'frigate':frigate,
        'cameras':cameras,
        'User':User,
        'apiAuth':apiAuth,
        'config':config
    }
    for table in tables:
        try:
            tables[table].query.first()
            status['db'][table] = True
        except sqlalchemy.exc.OperationalError:
            status['db'][table] = False
    if Item == status:
        return status
    else:
        page=f"/setup/{Item}"
        label = Item.title()
        if Item == 'start' or Item == 'fevr' or Item == 'admin':
            next='frigate'
            label = 'fEVR'
            admin = User.query.filter_by(group='admin').first()
            if admin:
                adname = admin.name
                admail = admin.email
                admin = [adname,admail]
            return render_template('setupadmin.html',next=next,admin=admin,label=label,page=page,items=status,Item=Item)
        elif Item == 'frigate':
            next="/setup/cameras"
        elif Item == 'cameras':
            next="/setup/User"
        elif Item == 'User':
            next="/setup/apiAuth"
        elif Item == 'apiAuth':
            label = 'apiAuth'
            next = '/setup/config'
        elif Item == 'config':
            next = '/'
        else:
            next = "/"
        return render_template('setup.html',next=next,label=label,page=page,items=status,Item=Item)


@setup.route('/setup/admin')
@login_required
def setupAdmin():
    # Sanity checks...
    admin = User.query.filter_by(group='admin').first()
    if admin: # If an admin already exists, then go to signup page instead.
        flash(f"An admin account already exists.<br/>Please sign up for a regular user account.")
        return redirect(url_for('auth.signup'))
    else:
        return render_template('setupadmin.html',passwd = randpwd.generate())

@setup.route('/setup/admin', methods=['POST'])
@login_required
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