from  .. import db
from flask_sqlalchemy import inspect
from flask_login import UserMixin
from datetime import datetime

class frigate(db.Model):
# Table     : frigate
# Columns   : - id      (auto incrementing primary key)
#           : - url     (URL of frigate instance ex: http://192.168.101.10:5000)
#           : - name    (MQTT name of frigate instance)
    id = db.Column(db.Integer,primary_key = True)
    url = db.Column(db.String(200), unique = True)
    name = db.Column(db.String(100), unique = True)

    def __repr__(self):
    # Returns string representation of dict
        return str({"id":self.id,"url":self.url,"name":self.name})

    def exists():
    # Returns True if table exists
        inspector = inspect(db.engine)
        return inspector.has_table("frigate")

    def dict(query):
    # Returns dict of query
        result = {}
        for frigate in query:
            result[frigate.name] = frigate.url
        print(result)
        return result



class cameras(db.Model):
# Table     : cameras
# Columns   : - id      (auto incrementing primary key)
#           : - camera  (Camera Name)
#           : - hls     (HLS stream URL)
#           : - rtsp    (RTSP stream URL)
    id = db.Column(db.Integer,primary_key = True)
    camera = db.Column(db.String(20), unique = True)
    hls = db.Column(db.String(200))
    rtsp = db.Column(db.String(200))

    def __repr__(self):
    # Returns string representation of dict
        return str({"id":self.id,"camera":self.camera,"hls":self.hls,"rtsp":self.rtsp})

    def exists():
    # Returns True if table exists
        inspector = inspect(db.engine)
        return inspector.has_table("events")

    def dict(query):
    # Returns dict of query
        result = {}
        for camera in query:
            result[camera.camera] = {
                "hls"   : camera.hls,
                "rtsp"  : camera.rtsp
            }
        return result
    def lst(query):
        result =[]
        for row in query:
            result.append(row.camera)
        return result
    
class events(db.Model):
# Table     : events
# Columns   : - id      (auto incrementing primary key)
#           : - eventid (Event ID from Frigate)
#           : - time    (DateTime generated from eventid timestamp)
#           : - camera  (Camera which generated event)
#           : - object  (Type of object detected)
#           : - score   (Score generated by frigate (math.floor(frigate_score*100)))
#           : - ack     (blank if unacknowledged, 'true' if acknowledged This is a string so that it can be set to "","ack","seen","delete")
    id = db.Column(db.Integer,primary_key = True)
    eventid = db.Column(db.String(25), unique = True)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    camera = db.Column(db.String(50))
    object = db.Column(db.String(25))
    score = db.Column(db.Integer)
    ack = db.Column(db.String(10))


    def exists():
    # Returns True if table exists
        inspector = inspect(db.engine)
        if inspector:
            return inspector.has_table("events")
        
    def dict(query):
    # Returns dict of query
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
    
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    group = db.Column(db.String(35))
    enabled = db.Column(db.Boolean)
    resetpwd = db.Column(db.Boolean)

class apiAuth(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50),unique=True)
    key = db.Column(db.String(150),unique=True)
    authIP = db.Column(db.String(20))
    limit = db.Column(db.Integer)
    expired = db.Column(db.Boolean)

class config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    param = db.Column(db.String(50),unique=True)
    description = db.Column(db.String(500))
    value = db.Column(db.String(100))
