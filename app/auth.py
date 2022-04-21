import ipaddress
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from IPy import IP

from .models import User, apiAuth
from . import db
from .logit import logit
from .rndpwd import randpwd

log=logit()  

auth = Blueprint('auth', __name__)

@auth.route('/auth/add/key/<name>/<ip>/<limit>')
@login_required
def apiAuthKeyAdd(name,ip,limit):
    def validIP(ip):
        try:
            IP(ip)
            return True
        except:
            return False
    if current_user.group == "admin":
        if validIP(ip):
            db.create_all()
            key = randpwd.generate(key=True)
            auth = apiAuth(name=name,authIP=ip,key=key,limit=int(limit))
            db.session.add(auth)
            db.session.commit()
            value = {"Authorized":True,"name":name,"ip":ip,"limit":limit,"key":key,"expired":False}
        else:
            value = {"Authorized":False,"Reason":"Invalid IP"}
    else:
        value = {"Authorized":False,"Reason":"Admin Only"}
    return jsonify(value)

@auth.route('/auth/add/key',methods=['POST'])
@login_required
def apiAuthKeyAddPost():
    def validIP(ip):
        try:
            IP(ip)
            return True
        except:
            return False
    ip = request.form.get('ip')
    name = request.form.get('name')
    limit = request.form.get('limit')
    if current_user.group == "admin":
        if validIP(ip):
            db.create_all()
            key = randpwd.generate(key=True)
            auth = apiAuth(name=name,authIP=ip,key=key,limit=int(limit))
            db.session.add(auth)
            db.session.commit()
            value = {"Authorized":True,"name":name,"ip":ip,"limit":limit,"key":key,"expired":False}
        else:
            value = {"Authorized":False,"Reason":"Invalid IP"}
    else:
        value = {"Authorized":False,"Reason":"Admin Only"}
    return jsonify(value)

@auth.route('/apiAuth',methods=['POST'])
def apiAuthenticate():
    ip = request.remote_addr
    auth = {"auth":False,"name":None,"authIP":ip,"changed":False,"remember":False}
    requestData = request.get_json()
    log.execute(f"apiAuth Post Data:{requestData}")
    key = None
    if 'key' in requestData:
        key = requestData['key']
        log.execute(f"  [ apiAuth Received API KEY ]: {key}",src=__name__)
        entries = apiAuth.query.filter_by(key=key).first()
        if entries:
            for entry in entries:
                if entry.key == key:
                    log.execute(f"  [ apiAuth Expected Key ]: {entry.key}")
                    log.execute(f"  [ apiAuth Received Key ]: {key}")
                    # Check if all of the following match:
                    #   - ip address
                    #   - key
                    #   - key expiry
                    if entry.key==key and not entry.expired:
                        auth['auth'] = True
                        auth['name'] = entry.name
                        auth['authIP'] = ip
                        log.execute(f"  [ auth ]: {auth}",__name__)
                        login_user(entry,remember=True)
                        log.execute(f"  [ apiAuth AUTHORIZED ]: {auth}",src=__name__)
                        # Check the key limits
                        # Keys can be use limited.
                        # A user that has just a limited key can only log into the site X number of times before key expires
                        if entry.limit != 0:
                            if entry.limit > 1:
                                entry.limit -= 1
                                auth['changed'] = True
                            # If this is the key's last use, make sure to expire it.
                            elif entry.limit == 1:
                                entry.limit = 0
                                entry.expired = True
                                auth['changed'] = True
                        # If we changed they key limit or set it to expired, commit it to the database.
                        if auth['changed']:
                            db.session.commit()
    log.execute(f"  [ apiAuth Returned Value ]: {auth}",src=__name__)
    return jsonify(auth)

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

@auth.route('/profile')
@login_required
def profile():
    user = current_user
    keys = apiAuth.query.all()
    return render_template('user.html',user=user,keys=keys)