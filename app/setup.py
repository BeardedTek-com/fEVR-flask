from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
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
    user = current_user
    Cameras = cameras.lst(cameras.query.all())
    menu=cookies.getCookie('menu')
    status = {'db':{'cameras':False,'frigate':False,'mqtt':False,'other':False}}
    tables = {
        'frigate':frigate,
        'cameras':cameras,
        'mqtt':apiAuth,
        'other':config
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
                resp = redirect('/setup/cameras')
            else:
                # First, let's create the database
                db.create_all()
                status = {'db':{'cameras':False,'frigate':False,'User':False,'apiAuth':False,'config':False}}
                # Sanity checks...
                admin = User.query.filter_by(group='admin').first()
                resp = render_template('setupadmin.html',passwd = randpwd.generate(),items=status,next="cameras")

        elif Item == 'cameras':
            next="/setup/frigate"
            template = "setupcameras.html"
            resp = render_template(template,Cameras=cameras.query.all(),cameras=Cameras,menu=menu,next=next,label=label,page=page,items=status,Item=Item,user=user)
        elif Item == 'frigate':
            next="/setup/mqtt"
            template = "setupfrigate.html"
            resp = render_template(template,frigate=frigate.query.all(),cameras=Cameras,menu=menu,next=next,label=label,page=page,items=status,Item=Item,user=user)
        elif Item == 'mqtt':
            label = 'MQTT Client Setup'
            next = '/setup/config'
            template = "setupapiauth.html"
            resp = render_template(template,frigate=frigate.query.all(),cameras=Cameras,menu=menu,next=next,label=label,page=page,items=status,Item=Item,user=user)
        elif Item == 'config':
            label = "Other"
            next = '/'
            template = "setupconfig.html"
            resp = render_template(template,frigate=frigate.query.all(),cameras=Cameras,menu=menu,next=next,label=label,page=page,items=status,Item=Item,user=user)
        else:
            label = "Cameras"
            next="/setup/frigate"
            template = "setupcameras.html"
            flash(f"{Item} not a valid setup paramater.  Back to the start you go.")
            resp = render_template(template,Cameras=cameras.query.all(),cameras=Cameras,menu=menu,next=next,label=label,page=page,items=status,Item=Item,user=user)
        return resp

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
        
        emailCheck = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database
        if emailCheck: # if a user is found, we want to redirect back to signup page so user can try again
            flash('Email Already Exists.')
            return redirect(url_for('setup.setupAdmin'))
        
        nameCheck = User.query.filter_by(name=name).first()
        if nameCheck: # Does this username already exist?
            flash('Username Taken')
        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), group='admin', enabled=True, resetpwd=False)

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))