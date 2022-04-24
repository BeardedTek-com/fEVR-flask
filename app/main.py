from flask import Blueprint, render_template, redirect, url_for, make_response, flash
from flask_login import login_required
from sqlalchemy import desc
from .models.models import frigate, cameras, events, User, apiAuth, config
from . import api
from .helpers.cookies import cookies
main = Blueprint('main',__name__)


# Main Routes
@main.route('/')
@login_required
def index():
    menu = cookies.getCookie('menu')
    page = '/'
    title = 'Latest Events'
    events = api.apiShowLatest()
    return render_template('events.html',menu=menu,page=page,title=title,events=events)

@main.route('/latest')
@login_required
def latest():
    return redirect("/")

@main.route('/all')
@login_required
def viewAll():
    menu = cookies.getCookie('menu')
    page = '/all'
    title = 'All Events'
    events = api.apiShowAllEvents()
    return render_template('events.html',menu=menu,page=page,title=title,events=events)

@main.route('/filter/<filter>/<value>')
@login_required
def filterEvents(filter,value):
    cookiejar = {}
    menu = cookies.getCookie('menu')
    page = cookies.getCookie('page')
    title="Filtered Events"
    time = cookies.getCookie('time')
    camera = cookies.getCookie('cameras')
    object = cookies.getCookie('object')
    score = cookies.getCookie('score')
    ack = cookies.getCookie('ack')
    if filter == 'time':
        time = value
    elif filter == 'camera':
        camera = value
    elif filter == 'object':
        object = value
    elif filter == 'score':
        score = value
    elif filter == 'ack':
        ack = value
    else:
        flash('Filtering of this type not available')
    cookiejar = {'menu':menu,'page':page,'title':title,'time':time,'camera':camera,'object':object,'score':score,'ack':ack}
    query = events.query
    if camera:
        query = query.filter(events.camera==camera)
    if object:
        query = query.filter(events.object==object)
    if score:
        query = query.filter(events.score==score)
    if ack:
        query = query.filter_by(events.ack==ack)
    query = events.dict(query.order_by(desc(events.time)))
    resp = make_response(render_template('events.html',menu=cookiejar['menu'],page=cookiejar['page'],title=title,events=query))
    return cookies.setCookies(cookiejar,resp)
        
            
        

        
                    
                
                
@main.route('/event/<eventid>/<view>')
@login_required
def viewSingle(eventid,view):
    menu = cookies.getCookie('menu')
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
        return render_template('event.html',menu=menu,page=page,title=title,event=event,view=view,frigateURL=frigateURL)
    else:
        return redirect(url_for('main.index'))
    

    
