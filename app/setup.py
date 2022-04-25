from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required
from werkzeug.security import generate_password_hash
from .models.models import User,frigate,cameras,events,apiAuth,config
import sqlalchemy
from .helpers.drawSVG import drawSVG
from . import db
from .rndpwd import randpwd
from .helpers.cookies import cookies
setup = Blueprint('setup', __name__)


@setup.route('/setup')
def setupFwd():
    return redirect("/setup/admin")
@setup.route('/setup/<Item>')
@login_required
def setupfEVR(Item):
    menu=cookies.getCookie('menu')
    status = {'db':{'cameras':False,'frigate':False,'User':False,'apiAuth':False,'config':False}}
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
        label = f"{Item.title()} Setup"
        if Item == 'start' or Item == 'fevr' or Item == 'admin':
            next='frigate'
            label = 'fEVR Setup'
            admin = User.query.filter_by(group='admin').first()
            if admin:
                adname = admin.name
                admail = admin.email
                admin = [adname,admail]
            return render_template('setupadmin.html',menu=menu,next=next,admin=admin,label=label,page=page,items=status,Item=Item)

        elif Item == 'frigate':
            next="/setup/cameras"
        elif Item == 'cameras':
            next="/setup/User"
        elif Item == 'User':
            next="/setup/apiAuth"
        elif Item == 'apiAuth':
            label = 'apiAuth Setup'
            next = '/setup/config'
        elif Item == 'config':
            next = '/'
        else:
            next = "/"
        return render_template('setup.html',menu=menu,next=next,label=label,page=page,items=status,Item=Item)


@setup.route('/setup/admin')
def setupAdmin():
    status = {'db':{'cameras':False,'frigate':False,'User':False,'apiAuth':False,'config':False}}
    # Sanity checks...
    admin = User.query.filter_by(group='admin').first()
    if admin: # If an admin already exists, then go to signup page instead.
        flash(f"An admin account already exists.<br/>Please sign up for a regular user account.")
        return redirect(url_for('auth.signup'))
    else:
        return render_template('setupadmin.html',passwd = randpwd.generate(),items=status)

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