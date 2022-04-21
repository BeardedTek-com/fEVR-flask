from flask import Blueprint, render_template, escape, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import desc
import subprocess
from datetime import datetime
import os

from .models import events,frigate,cameras,User,apiAuth
from . import db
from .logit import logit
from .fetch import Fetch
from .auth import apiAuth

main = Blueprint('main',__name__)

# Main Routes
@main.route('/')
@login_required
def index():
    page = '/'
    title = 'Latest Events'
    events = apiShowLatest()
    return render_template('events.html',page=page,title=title,events=events)

@main.route('/all')
@login_required
def viewAll():
    page = '/all'
    title = 'All Events'
    events = apiShowAllEvents()
    return render_template('events.html',page=page,title=title,events=events)

@main.route('/event/<eventid>/<view>')
@login_required
def viewSingle(eventid,view):
    page = f"/event/{eventid}/{view}"
    Frigate = apiFrigate()
    frigateURL = Frigate['external']
    if view == 'ack':
        apiAckEvent(eventid)
    elif view == 'unack':
        apiUnackEvent(eventid)
    elif view == 'delOK':
        apiDelEvent(eventid)
        return redirect(url_for('main.index'))
    query = events.query.filter_by(eventid=eventid).order_by()
    query = events.dict(query)
    for item in query:
        event = query[item]
    if 'event' in locals():
        if event['ack'] == "" and view != 'unack':
            apiAckEvent(eventid)
            event['ack'] = "true"
        title = f"<div class='back'><a href='/'><img src='/static/img/back.svg'></a></div><div class='objcam'>{event['object'].title()} in {event['camera'].title()}</div>"
        xx = 0
        for X in ['live','clip','snap']:
            if view == X:
                xx += 1
        if xx > 0:
            if view == 'clip' or view == 'snap':
                title += f"<div class='view20'>Event {view.title()}</div>"
            else:
                title += f"<div class='view20'>{view.title()}</div>"
        else:
            title += "<div class='view20'> </div>"
        return render_template('event.html',page=page,title=title,event=event,view=view,frigateURL=frigateURL)
    else:
        return redirect(url_for('main.index'))
    
# API Routes
api = Blueprint('api',__name__)

@api.route('/api')
@login_required
def apiHome():
    page = '/api'
    title = "fEVR API Documentation"
    contents = subprocess.Popen("flask routes", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode("utf-8")
    return render_template('api.html',page=page,title=title, contents=contents)

@api.route('/api/frigate/add/<name>/<http>/<ip>/<port>')
def apiAddFrigate(name,http,ip,port):
    db.create_all()
    url = f"{http}://{ip}:{port}/"
    Frigate = frigate(name=name,url=url)
    db.session.add(Frigate)
    db.session.commit()
    return {"name":escape(name),"url":escape(url)}

@api.route('/api/frigate')
def apiFrigate():
    if frigate.exists():
        db.create_all()
    query = frigate.query.all()
    frigates = frigate.dict(query)

    if frigates['frigate']:
        internal = frigates['frigate']
    else:
        internal = "http://192.168.2.240:5000"
    if frigates['external']:
        external = frigates['external']
    else:
        external = internal
    return {"frigate":internal,"external":external}

@api.route('/api/events/add/<eventid>/<camera>/<object>/<score>')
@login_required
def apiAddEvent(eventid,camera,score,object):
    def addEvent(eventid,camera,score,object):
        db.create_all()
        time = datetime.fromtimestamp(int(eventid.split('.')[0]))
        event = events(eventid=eventid,camera=camera,object=object,score=int(score),ack='',time=time)
        db.session.add(event)
        db.session.commit()
        fetchPath = f"{os.getcwd()}/app/static/events/{eventid}/"
        frigateConfig = apiFrigate()
        frigateURL = frigateConfig['frigate']
        
        print(f"######################################################################################### \n \
                # Fetching {eventid} for {object} in {camera} from {frigateConfig['frigate']} \n \
                ######################################################################################### ")
        Fetch(fetchPath,eventid,frigateURL)
        
    # Check if eventid already exists
    if events.query.filter_by(eventid=eventid).first():
        return jsonify({"msg":"Event Already Exists"})
    # Are they authorized?
#    elif apiAuth.exe():
    else:
        addEvent(eventid,camera,score,object)
        return 'Success', 200
#    else:
#        return 'Not Authorized', 200
@api.route('/api/admin/events/add/<eventid>/<camera>/<object>/<score>')
@login_required
def apiAdminAddEvent(eventid,camera,score,object):
    def addEvent(eventid,camera,score,object):
        db.create_all()
        time = datetime.fromtimestamp(int(eventid.split('.')[0]))
        event = events(eventid=eventid,camera=camera,object=object,score=int(score),ack='',time=time)
        db.session.add(event)
        db.session.commit()
        fetchPath = f"{os.getcwd()}/app/static/events/{eventid}/"
        frigateConfig = apiFrigate()
        frigateURL = frigateConfig['frigate']
        
        print(f"######################################################################################### \n \
                # Fetching {eventid} for {object} in {camera} from {frigateConfig['frigate']} \n \
                ######################################################################################### ")
        Fetch(fetchPath,eventid,frigateURL)
    if current_user.group == 'admin':
        addEvent(eventid,camera,score,object)
        return 'Success', 200
    else:
        return 'Not Authorized', 200

@api.route('/api/events/ack/<eventid>')
@login_required
def apiAckEvent(eventid):
    query = events.query.filter_by(eventid=eventid).first()
    query.ack = "true"
    db.session.commit()

@api.route('/api/events/unack/<eventid>')
@login_required
def apiUnackEvent(eventid):
    query = events.query.filter_by(eventid=eventid).first()
    query.ack = ""
    db.session.commit()

@api.route('/api/events/del/<eventid>')
@login_required
def apiDelEvent(eventid):
    events.query.filter_by(eventid=eventid).delete()
    db.session.commit()
    return redirect(url_for('main.index'))

@api.route('/api/events/latest')
@login_required
def apiShowLatest():
    if not events.exists():
        db.create_all()
    query = events.query.order_by(desc(events.time)).limit(12).all()
    return events.dict(query)

@api.route('/api/events/all')
@login_required
def apiShowAllEvents():
    if not events.exists():
        db.create_all()
    query = events.query.order_by(desc(events.time)).all()
    return events.dict(query)

@api.route('/api/event/<eventid>/<view>')
@login_required
def apiSingleEvent(eventid):
    query = events.query.filter_by(eventid=eventid)
    return events.dict(query)

@api.route('/api/events/camera/<camera>')
@login_required
def apiEventsByCamera(camera):
    query = events.query.filter_by(camera=camera)
    return events.dict(query)

@api.route('/api/cameras/add/<camera>/<server>')
@login_required
def apiAddCamera(camera,server):
    db.create_all()
    hls = f"http://{server}:5084/{camera}"
    rtsp = f"rtsp://{server}:5082/{camera}"
    camera = cameras(camera=camera,hls=hls,rtsp=rtsp)
    db.session.add(camera)
    db.session.commit()
    return "OK"

@api.route('/api/cameras/<camera>')
@login_required
def apiCameras(camera):
    if not cameras.exists():
        db.create_all()
    if camera == "all":
        query = cameras.query.all()
    else:
        query = cameras.query.filter_by(camera=camera)
    return cameras.dict(query)
    
