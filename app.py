import webbrowser
from threading import Thread
from router import app
from typedef import APPCONFIG

browser = webbrowser.get()
backend = Thread(target=app.run, kwargs=APPCONFIG, daemon=False)

if __name__ == '__main__':
    browser.open('https://127.0.0.1:8100')
    backend.join()