from flask import Blueprint, render_template, escape, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import desc
import subprocess
from datetime import datetime
import os


from .models import events,frigate,cameras
from . import db
from .logit import logit
from .fetch import Fetch

api = Blueprint('api',__name__)

@api.route('/api')
def apiHome():
    page = 'apidocs'
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
def apiAddEvent(eventid,camera,score,object):
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
    fetchEvent = Fetch(fetchPath,eventid,frigateURL)
    return redirect(url_for('main.index'))

@api.route('/api/events/ack/<eventid>')
def apiAckEvent(eventid):
    query = events.query.filter_by(eventid=eventid).first()
    query.ack = "true"
    db.session.commit()

@api.route('/api/events/unack/<eventid>')
def apiUnackEvent(eventid):
    query = events.query.filter_by(eventid=eventid).first()
    query.ack = ""
    db.session.commit()

@api.route('/api/events/del/<eventid>')
def apiDelEvent(eventid):
    events.query.filter_by(eventid=eventid).delete()
    db.session.commit()
    return redirect(url_for('main.index'))

@api.route('/api/events/latest')
def apiShowLatest():
    if not events.exists():
        db.create_all()
    query = events.query.order_by(desc(events.time)).limit(12).all()
    return events.dict(query)

@api.route('/api/events/all')
def apiShowAllEvents():
    if not events.exists():
        db.create_all()
    query = events.query.order_by(desc(events.time)).all()
    return events.dict(query)

@api.route('/api/event/<eventid>/<view>')
def apiSingleEvent(eventid):
    query = events.query.filter_by(eventid=eventid)
    return events.dict(query)

@api.route('/api/events/camera/<camera>')
def apiEventsByCamera(camera):
    query = events.query.filter_by(camera=camera)
    return events.dict(query)

@api.route('/api/cameras/add/<camera>/<server>')
def apiAddCamera(camera,server):
    db.create_all()
    hls = f"http://{server}:5084/{camera}"
    rtsp = f"rtsp://{server}:5082/{camera}"
    camera = cameras(camera=camera,hls=hls,rtsp=rtsp)
    db.session.add(camera)
    db.session.commit()
    return "OK"

@api.route('/api/cameras/<camera>')
def apiCameras(camera):
    if not cameras.exists():
        db.create_all()
    if camera == "all":
        query = cameras.query.all()
    else:
        query = cameras.query.filter_by(camera=camera)
    return cameras.dict(query)