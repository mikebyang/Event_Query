from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, request, session
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import credentials
from googleapiclient.discovery import build

import os

from event import Event
from typedef import SCOPES

app = Flask(__name__)
app.secret_key = os.urandom(24)

# site routes
@app.route('/')
def index():
    print("present question...")
    return render_template('question.html')

@app.route('/cal_option')
def cal_option():
    print("present option to add to calendar...")
    return render_template('addcalevnt.html')

@app.route('/add_to_calendar')
def add_to_calendar():
    print("add to calendar...")

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
    print("callback function...")
    if request.args.get('state') != session['state']:
        print("ERROR")
        print(f"\t> mismatch state values. expected: {session['state']}, got: {request.args.get('state')}")
        raise Exception("Invalid state")
    
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

    print("\t> adding to calendar...")

    #create event details
    print(f"\t> creating event...")
    this_year = datetime.now().year
    start = datetime(this_year, 2, 14, 21, 30)
    end = start + timedelta(hours=1, minutes=30)
    day = Event('Valentines Day Dinner Test', '334 8th Ave, New York City, NY 10001-6947', 'America/New_York', start.isoformat(), end.isoformat())

    #TODO check to make sure that event is not already on calendar

    try:
        print(f"\t> creating service instance...")
        creds = credentials.Credentials(**session['credentials'])
        service = build('calendar', 'v3', credentials=creds)

        print(f"\t> adding event to calendar...")
        day.schedule(service)
    except Exception as e:
        print("error scheduling event...")
        print(f"\t> {e}")
        return render_template('addcalevnt.html')

    return redirect(url_for('finale', param='yes'))

@app.route('/finale/<string:param>')
def finale(param):
    print("initiate finale...")
    session.clear()

    msg = "Done. Event has been added to your Google Calendar!"
    if param.lower() == "no":
        msg = "Nothing else to do then."
    return render_template('finale.html', msg=msg)