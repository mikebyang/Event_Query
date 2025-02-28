from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, request, session
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import credentials
from googleapiclient.discovery import build

import os

from event import Event
from typedef import SCOPES, DEV, Calendar_Option, DUPLICATE_EVENT, EVENT_ADDED, EVENT_NOT_ADDED

app = Flask(__name__)
app.secret_key = os.urandom(24)
calendar_options = []

# site routes

@app.route('/')
def index():
    print(f'\t> present question...')

    if DEV:
        return render_template('addcalevnt.html')
        # return redirect(url_for("form"))
    return render_template('question.html')

@app.route('/add_to_calendar')
def add_to_calendar():
    print(f'\t> add to calendar...')

    # user authentication
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json', SCOPES
    )
    flow.redirect_uri = url_for('callback', _external = True)
    auth_url, state = flow.authorization_url()
    session['state'] = state

    return redirect(auth_url)

@app.route('/callback')
def callback():
    print(f'\t> callback function...')
    print(f'\t> request from server method... {request.method}')
    if request.args.get('state') != session['state']:
        print('ERROR')
        session_state = session['state']
        request_state = request.args.get('state')
        print(f'\t> mismatch state values. expected: {session_state}, got: {request_state}')
        raise Exception('Invalid state')
    
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json', SCOPES, state=session['state']
    )
    flow.redirect_uri = url_for('callback', _external = True)

    auth_response = request.url
    flow.fetch_token(authorization_response = auth_response)
    creds = flow.credentials

    session['credentials'] = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

    print(f'\t> creating service instance...')
    creds = credentials.Credentials(**session['credentials'])

    try:
        global service
        service = build('calendar', 'v3', credentials=creds)
        calendar_list = service.calendarList().list(pageToken=None).execute()
    except Exception as e:
        print(f'\t> error getting calendars...')
        print(f'\t> {e}')
        return

    for item in calendar_list['items']:
        print(item)
        calendar_options.append(Calendar_Option(item['summary'], item['id'], item['backgroundColor']))

    print(calendar_options)

    global single_calendar
    single_calendar = None

    if len(calendar_options) > 1:
        return redirect(url_for('form'))
    
    single_calendar = calendar_options[0].id

    return redirect(url_for('form_submit'))
    
@app.route('/form')
def form():
    return render_template('form.html', dropdown = calendar_options)

@app.route('/form_submit', methods = ['POST'])
def form_submit():
    print(f'\t> adding to calendar...')
    
    global single_calendar
    
    if request.method != 'POST' and single_calendar != None:
        return redirect(url_for('finale', param=EVENT_NOT_ADDED))
    
    if single_calendar != None:
        selection = single_calendar
    else:
        selection = request.form['calendar_selection']
    
    print(f'\t> ID for calendar: {selection}')

    #create event details
    print(f'\t> creating event...')
    this_year = datetime.now().year
    start = datetime(this_year, 2, 14, 22, 45)
    end = start + timedelta(hours=1, minutes=30)
    day = Event('Valentines Day Test', selection, 'COTE Korean Steakhouse, 16 W 22nd St, New York, NY 10010', 'America/New_York', start.isoformat(), end.isoformat())
    print(day)

    try:
        global service

        search_time_start = start.isoformat() + 'Z'
        search_time_end = (end + timedelta(days=1)).isoformat() + 'Z'

        events = service.events().list(calendarId=selection, timeMax = search_time_end, timeMin = search_time_start).execute()

        for event in events['items']:
            event_name = event['summary']
            if event_name == day.name:
                return redirect(url_for('finale', param=DUPLICATE_EVENT))

        print(f'\t> adding event to calendar...')
        day.schedule(service)
    except Exception as e:
        print(f'\t> error scheduling event...')
        print(f'\t> {e}')
        return redirect(url_for('finale', param=EVENT_NOT_ADDED))
    return redirect(url_for('finale', param=EVENT_ADDED))

@app.route('/finale/<string:param>')
def finale(param):
    print(f'\t> initiate finale...')
    session.clear()

    global service
    service.close()

    if param.lower() == 'no':
        param = EVENT_NOT_ADDED

    return render_template('finale.html', msg=param)