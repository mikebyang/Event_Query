from datetime import datetime

class Event():
    def __init__(self, name: str, id: str, location: str, timezone: str, start: str, end: str):
        self.name = name
        self.id = id
        self.location = location
        self.timezone = timezone
        self.start = start
        self.end = end

    def schedule(self, service: any) -> Exception:
        try:
            print('\t> insert...')
            response = service.events().insert(
                calendarId = self.id,
                body = {
                    'summary': self.name,
                    'location': self.location,
                    'start':{'dateTime': self.start, 'timeZone': self.timezone},
                    'end':{'dateTime': self.end, 'timeZone': self.timezone}
                }
            ).execute()

            print(f'\t> reponse: {response}')
        except Exception as error:
            raise error
        
        return None
    
    def __str__(self):
        return f'{{name: {self.name}, id: {self.id}, location: {self.location}, timezone: {self.timezone}, start: {self.start}, end: {self.end}}}'
    def __repr__(self):
        return str(self)