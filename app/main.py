from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
import sqlalchemy
from .models import frigate, cameras, events, User, apiAuth, config
from . import api
from .helpers.menu import menuState
main = Blueprint('main',__name__)


# Main Routes
@main.route('/')
@login_required
def index():
    menu = menuState.get()
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
    menu = menuState.get()
    page = '/all'
    title = 'All Events'
    events = api.apiShowAllEvents()
    return render_template('events.html',menu=menu,page=page,title=title,events=events)

@main.route('/event/<eventid>/<view>')
@login_required
def viewSingle(eventid,view):
    menu = menuState.get()
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
    

    
