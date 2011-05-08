from django.conf import settings

import httplib2
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

def get_prediction_service():

    flow = OAuth2WebServerFlow(
        client_id=settings.PREDICTION_API_CLIENT_ID,
        client_secret=settings.PREDICTION_API_CLIENT_SECRET,
        scope='https://www.googleapis.com/auth/prediction',
        user_agent='prediction-cmdline-sample/1.0')

    storage = Storage('prediction.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = run(flow, storage)

    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    return build("prediction", "v1.2", http=http)
