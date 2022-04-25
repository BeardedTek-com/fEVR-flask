from flask import Blueprint, render_template, redirect, url_for, make_response, flash, request
from flask_login import login_required
from sqlalchemy import desc
from .models.models import frigate, cameras, events, User, apiAuth, config
from . import api
from .helpers.cookies import cookies
from .logit import logit
main = Blueprint('main',__name__)


# Main Routes
@main.route('/')
@login_required
def index():
    Cameras = cameras.lst(cameras.query.all())
    menu = request.cookies.get('menu')
    print(f"#################################################")
    page = '/'
    title = 'Latest Events'
    events = api.apiShowLatest()
    return render_template('events.html',Menu=menu,page=page,title=title,events=events,cameras=Cameras)

@main.route('/latest')
@login_required
def latest():
    return redirect("/")

@main.route('/all')
@login_required
def viewAll():
    Cameras = Cameras = cameras.lst(cameras.query.all())
    menu = request.cookies.get('menu')
    page = '/all'
    title = 'All Events'
    events = api.apiShowAllEvents()
    return render_template('events.html',Menu=menu,page=page,title=title,events=events,cameras=Cameras)

@main.route('/events/camera/<Camera>')        
@login_required
def viewEventsbyCamera(Camera):
    Cameras = Cameras = cameras.lst(cameras.query.all())
    menu = request.cookies.get('menu')
    page = cookies.getCookie('page')
    cookiejar = {'page':page,'cameras':str(Cameras)}
    title=f"{Camera.title()} Events"
    query = events.query.filter(events.camera==Camera)
    resp = make_response(render_template('events.html',Menu=menu,page=cookiejar['page'],title=title,events=events.dict(query),cameras=Cameras))
    for cookie in cookiejar:
            resp.set_cookie(cookie,cookiejar[cookie])
    return resp

@main.route('/events/camera/<Camera>/<filter>/<value>')
@login_required
def viewEventsbyCameraFiltered(Camera,filter,value):
    Cameras = Cameras = cameras.lst(cameras.query.all())
    validFilter = False
    validValue = False
    validFilters = {'object':
                        ['car','animal','person'],
                    'score':
                        [60,100],
                    'ack':
                        ['true','false']
                    }
    for fil in validFilters:
        if filter == fil:
            validFilter = True
            if filter == 'score':
                if validFilters[fil][0] <= int(value) <= validFilters[fil][0]:
                    validValue = True
            else:
                for val in validFilters[fil]:
                    if val == value:
                        validValue = True
    if validFilter and validValue:
        menu = request.cookies.get('menu')
        page = cookies.getCookie('page')
        cookiejar={'page':page}
        title=f"{Camera.title()} Events by {filter.title()}"
        if filter == 'object':
            query = events.query.filter(events.camera==Camera,events.object==value)
        if filter == 'score':
            query = events.query.filter(events.camera==Camera,events.score==int(value))
        if filter == 'ack':
            query = events.query.filter(events.camera==Camera,events.ack==value)
    else:
        flashMessage = f"Invalid filter selected. Valid filters are:"
        for fil in validFilters:
            flashMessage += f" {fil}"
        flashMessage+= "."
        flash(flashMessage)
    resp = make_response(render_template('events.html',Menu=menu,page=cookiejar['page'],title=title,events=events.dict(query),cameras=Cameras))
    return cookies.setCookies(cookiejar,resp)

@main.route('/event/<eventid>/<view>')
@login_required
def viewSingle(eventid,view):
    Cameras = Cameras = cameras.lst(cameras.query.all())
    menu = request.cookies.get('menu')
    page = f"/event/{eventid}/{view}"
    Frigate = api.apiFrigate()
    frigateURL = Frigate['external']
    if view == 'ack':
        api.apiAckEvent(eventid)
    elif view == 'unack':
        api.apiUnackEvent(eventid)
    elif view == 'delOK':
        api.apiDelEvent(eventid)
        return redirect(url_for('main.index'))
    query = events.query.filter_by(eventid=eventid).order_by()
    query = events.dict(query)
    for item in query:
        event = query[item]
    if 'event' in locals():
        if event['ack'] == "" and view != 'unack':
            api.apiAckEvent(eventid)
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
        return render_template('event.html',Menu=menu,page=page,title=title,event=event,view=view,frigateURL=frigateURL,cameras=Cameras)
    else:
        return redirect(url_for('main.index'))
    

    
