from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import json
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
    score = db.Column(db.Integer)
    ack = db.Column(db.String(10))
    def __repr__(self):
        return str({"id": self.id,"eventid":self.eventid,"camera":self.camera,"score":self.score,"ack":self.ack})

    def eventToDict(query):
        result = {}
        for event in query:
            result[str(event.eventid)] = {
                "camera"    : event.camera,
                "score"     : event.score,
                "ack"       : event.ack
            }
        return result

@app.route('/')
def home():
    return 'Welcome.'

@app.route('/event/add/<eventid>/<camera>/<score>')
def addEvent(eventid,camera,score):
    db.create_all()
    event = events(eventid=eventid,camera=camera,score=int(score),ack='')
    db.session.add(event)
    db.session.commit()
    return "OK"

@app.route('/events/all')
def allEvents():
    query = events.query.all()
    return events.eventToDict(query)

@app.route('/event/<eventid>')
def byEventId(eventid):
    query = events.query.filter_by(eventid=eventid)
    return events.eventToDict(query)

@app.route('/events/camera/<camera>')
def byCamera(camera):
    query = events.query.filter_by(camera=camera)
    return events.eventToDict(query)

@app.route('/cameras/add/<camera>/<server>')
def addCamera(camera,server):
    db.create_all()
    hls = f"http://{server}:5084/{camera}"
    rtsp = f"rtsp://{server}:5082/{camera}"
    camera = cameras(camera=camera,hls=hls,rtsp=rtsp)
    db.session.add(camera)
    db.session.commit()
    return "OK"

@app.route('/cameras/<camera>')
def getCamera(camera):
    if camera == "all":
        query = cameras.query.all()
    else:
        query = cameras.query.filter_by(camera=camera)
    return cameras.cameraToDict(query)
 
