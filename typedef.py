SCOPES=['https://www.googleapis.com/auth/calendar']
APPCONFIG={
    'port': 8100,
    'ssl_context': 'adhoc',
    'debug': True,
    'use_reloader': False,
}

DUPLICATE_EVENT = 'Event already in calendar.'
EVENT_ADDED = 'Event added to calendar.'
EVENT_NOT_ADDED = 'Nothing was added to calendar.'

DEV = True

class Calendar_Option():
    def __init__(self, name, id, color):
        self.name = name
        self.id = id
        self.color = color
    def __repr__(self):
        return f'{{name: {self.name}, id: {self.id}, color: {self.color}}}'