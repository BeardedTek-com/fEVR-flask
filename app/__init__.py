from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy, inspect
import json
import subprocess
from datetime import datetime
import os
from PIL import Image
import requests
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fEVR.sqlite'
app.config['debug'] = True
app.config['host'] = "0.0.0.0"
app.debug = True
db = SQLAlchemy(app)

class Fetch:
    def __init__(self,path,eventid,frigate,thumbsize=180):
        self.path = path
        self.event = eventid
        self.frigate = frigate
        self.thumbSize = thumbsize
        self.thumbPATH = f"{self.path}thumb.jpg"
        self.clipPATH = f"{self.path}clip.mp4"
        self.snapPATH = f"{self.path}snapshot.jpg"
        self.snap = f"{self.frigate}api/events/{eventid}/snapshot.jpg"
        self.clip = f"{self.frigate}api/events/{eventid}/clip.mp4"
        print(self.frigate)
        print(self.event)
        print(self.thumbPATH)
        print(self.snapPATH)
        print(self.clipPATH)
        print(self.snap)
        print(self.clip)
        return self.getEvent()
    def getEvent(self):
        if not os.path.exists(self.thumbPATH):
            if not os.path.exists(self.path):
                os.makedirs(self.path)
            open(self.snapPATH,'wb').write(requests.get(self.snap, allow_redirects=True).content)
            self.resizeImg(self.snapPATH,self.thumbSize)
            open(self.clipPATH,'wb').write(requests.get(self.clip, allow_redirects=True).content)
            return f"Got {self.event} from frigate at {self.frigate}"

    def resizeImg(self,img,height=180,ratio=1.777777778):
        if os.path.exists(img):
            # Resizes an image from the filesystem
            Image.open(img).resize((int(height*ratio),height), Image.ANTIALIAS).save(self.thumbPATH,"JPEG", quality=75,optimize=True)

class frigate(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    url = db.Column(db.String(200), unique = True)
    name = db.Column(db.String(100), unique = True)

    def __repr__(self):
        return str({"id":self.id,"url":self.url,"name":self.name})

    def exists():
        inspector = inspect(db.engine)
        return inspector.has_table("frigate")

    def toDict(query):
        result = {}
        for frigate in query:
            result[frigate.name] = frigate.url
        return result

class cameras(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    camera = db.Column(db.String(20), unique = True)
    hls = db.Column(db.String(200))
    rtsp = db.Column(db.String(200))

    def __repr__(self):
        return str({"id":self.id,"camera":self.camera,"src":self.src})

    def exists():
        inspector = inspect(db.engine)
        return inspector.has_table("events")

    def cameraToDict(query):
        result = {}
        for camera in query:
            result[camera.camera] = {
                "hls"   : camera.hls,
                "rtsp"  : camera.rtsp
            }
        return result

class events(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    eventid = db.Column(db.String(25), unique = True)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    camera = db.Column(db.String(50))
    object = db.Column(db.String(25))
    score = db.Column(db.Integer)
    ack = db.Column(db.String(10))

    def __repr__(self):
        return str({"id": self.id,"eventid":self.eventid,"time":self.time,"camera":self.camera,"object":self.object,"score":self.score,"ack":self.ack})

    def exists():
        inspector = inspect(db.engine)
        if inspector:
            return inspector.has_table("events")

    def eventToDict(query):
        result = {}
        for event in query:
            result[event.id] = {
                "eventid"   : event.eventid,
                "time"      : event.time,
                "camera"    : event.camera,
                "object"    : event.object,
                "score"     : event.score,
                "ack"       : event.ack
            }
        return result

# Main Routes
@app.route('/')
def viewAll():
    page = 'events'
    title = 'frigate Event Video Recorder'
    events = apiShowAllEvents()
    return render_template('home.html',page=page,title=title,events=events)

@app.route('/event/<eventid>/<view>')
def viewSingle(eventid,view):
    if view == 'ack':
        apiAckEvent(eventid)
    elif view == 'unack':
        apiUnackEvent(eventid)
    elif view == 'del':
        query = events.query.filter_by(eventid=eventid).first()
    elif view == 'delOK':
        apiDelEvent(eventid)
        apiHome()
    query = events.query.filter_by(eventid=eventid)
    query = events.eventToDict(query)
    page= 'event'
    print(f"QUERY: {query}")
    for item in query:
        event = query[item]
        print(f"EVENT: {event}")
    title = f"<div class='back'><a href='/'><img src='/static/img/back.svg'></a></div><div>{event['object'].title()} in {event['camera'].title()}</div><div>{view.title()}</div>"
    return render_template('home.html',page=page,title=title,event=event,view=view)

# API Routes
@app.route('/api')
def apiHome():
    page = 'apidocs'
    title = "fEVR API Documentation"
    import subprocess
    contents = subprocess.Popen("flask routes", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode("utf-8")
    return render_template('home.html',page=page,title=title, contents=contents)

@app.route('/api/frigate/add/<name>/<http>/<ip>/<port>')
def apiAddFrigate(name,http,ip,port):
    db.create_all()
    url = f"{http}://{ip}:{port}/"
    Frigate = frigate(name=name,url=url)
    db.session.add(Frigate)
    db.session.commit()
    return {"name":name,"url":url}

@app.route('/api/frigate')
def apiFrigate():
    if frigate.exists():
        db.create_all()
    query = frigate.query.all()
    if frigate.toDict(query):
        return frigate.toDict(query)
    else:
        ### ADD SETUP ROUTINE ###
        return {"frigate":"http://192.168.2.240:5000/"}

@app.route('/api/events/add/<eventid>/<camera>/<object>/<score>')
def apiAddEvent(eventid,camera,score,object):
    db.create_all()
    time = datetime.fromtimestamp(int(eventid.split('.')[0]))
    event = events(eventid=eventid,camera=camera,object=object,score=int(score),ack='',time=time)
    db.session.add(event)
    db.session.commit()
    fetchPath = f"{os.getcwd()}/app/static/events/{eventid}/"
    print(fetchPath)
    frigateConfig = apiFrigate()
    frigateURL = frigateConfig['frigate']
    fetchEvent = Fetch(fetchPath,eventid,frigateURL)
    return fetchEvent

@app.route('/api/events/ack/<eventid>')
def apiAckEvent(eventid):
    query = events.query.filter_by(eventid=eventid).first()
    query.ack = "true"
    db.session.commit()

@app.route('/api/events/unack/<eventid>')
def apiUnackEvent(eventid):
    query = events.query.filter_by(eventid=eventid).first()
    query.ack = ""
    db.session.commit()

@app.route('/api/events/del/<eventid>')
def apiDelEvent(eventid):
    query = events.query.filter_by(eventid=eventid)
    db.session.delete(query)
    db.session.commit()


@app.route('/api/events/all')
def apiShowAllEvents():
    if not events.exists():
        db.create_all()
    query = events.query.all()
    return events.eventToDict(query)

@app.route('/api/event/<eventid>/<view>')
def apiSingleEvent(eventid):
    query = events.query.filter_by(eventid=eventid)
    return events.eventToDict(query)

@app.route('/api/events/camera/<camera>')
def apiEventsByCamera(camera):
    query = events.query.filter_by(camera=camera)
    return events.eventToDict(query)

@app.route('/api/cameras/add/<camera>/<server>')
def apiAddCamera(camera,server):
    db.create_all()
    hls = f"http://{server}:5084/{camera}"
    rtsp = f"rtsp://{server}:5082/{camera}"
    camera = cameras(camera=camera,hls=hls,rtsp=rtsp)
    db.session.add(camera)
    db.session.commit()
    return "OK"

@app.route('/api/cameras/<camera>')
def apiCameras(camera):
    if not cameras.exists():
        db.create_all()
    if camera == "all":
        query = cameras.query.all()
    else:
        query = cameras.query.filter_by(camera=camera)
    return cameras.cameraToDict(query)
 
