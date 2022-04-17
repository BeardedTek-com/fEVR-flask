from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import json
import subprocess
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/fEVR.sqlite'
app.config['debug'] = True
app.config['host'] = "0.0.0.0"
app.debug = True
db = SQLAlchemy(app)

class cameras(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    camera = db.Column(db.String(20), unique = True)
    hls = db.Column(db.String(200))
    rtsp = db.Column(db.String(200))
    def __repr__(self):
        return str({"id":self.id,"camera":self.camera,"src":self.src})

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
    camera = db.Column(db.String(50))
    object = db.Column(db.String(25))
    score = db.Column(db.Integer)
    ack = db.Column(db.String(10))
    def __repr__(self):
        return str({"id": self.id,"eventid":self.eventid,"camera":self.camera,"score":self.score,"ack":self.ack})

    def eventToDict(query):
        result = {}
        for event in query:
            result[str(event.id)] = {
                "eventid"   : event.eventid,
                "camera"    : event.camera,
                "object"    : event.object,
                "score"     : event.score,
                "ack"       : event.ack
            }
        return result

# Main Routes
@app.route('/')
def home():
    page = 'events'
    title = 'Events'
    events = allEvents()
    print(events)
    return render_template('home.html',page=page,title=title,events=events)

@app.route('/event/<eventid>')
def showEvent(eventid):
    events = byEventId(eventid)
    page= 'event'
    print(events)
    for i in events:
        event = events[i]
    title = f"{event['camera']} - {event['object']}"
    return render_template('home.html',page=page,title=title,events=events)

# API Routes
@app.route('/api')
def apihome():
    page = 'apidocs'
    title = "fEVR API Documentation"
    import subprocess
    contents = subprocess.Popen("flask routes", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode("utf-8").replace(' ','&nbsp;').split("\n")
    #contents = subprocess.Popen("flask routes", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].split()
    #contents = subprocess.check_output(['flask', 'routes'])
    #contents =  [
    #            "/api/events/all: returns json with all events in database",
    #            "/api/events/<eventid>: returns json with specific event by frigate's event id",
    #            "/api/events/camera/<camera>: returns json with specific event by camera name",
    #            "/api/events/add/<eventid>/<camera>/<score>: adds event with provided details",
    #            "",
    #            "/api/cameras/add/<camera>/<server>: adds camera using rtsp-simple-server server address",
    #            "/api/cameras/<camera>: returns json with specific camera information"
    #            ]
    return render_template('home.html',page=page,title=title, contents=contents)

@app.route('/api/events/add/<eventid>/<camera>/<score>')
def addEvent(eventid,camera,score):
    db.create_all()
    event = events(eventid=eventid,camera=camera,score=int(score),ack='')
    db.session.add(event)
    db.session.commit()
    return "OK"

@app.route('/api/events/all')
def allEvents():
    query = events.query.all()
    return events.eventToDict(query)

@app.route('/api/event/<eventid>')
def byEventId(eventid):
    query = events.query.filter_by(eventid=eventid)
    return events.eventToDict(query)

@app.route('/api/events/camera/<camera>')
def byCamera(camera):
    query = events.query.filter_by(camera=camera)
    return events.eventToDict(query)

@app.route('/api/cameras/add/<camera>/<server>')
def addCamera(camera,server):
    db.create_all()
    hls = f"http://{server}:5084/{camera}"
    rtsp = f"rtsp://{server}:5082/{camera}"
    camera = cameras(camera=camera,hls=hls,rtsp=rtsp)
    db.session.add(camera)
    db.session.commit()
    return "OK"

@app.route('/api/cameras/<camera>')
def getCamera(camera):
    if camera == "all":
        query = cameras.query.all()
    else:
        query = cameras.query.filter_by(camera=camera)
    return cameras.cameraToDict(query)
 
