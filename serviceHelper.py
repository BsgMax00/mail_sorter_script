import os.path
import json

from dotenv import load_dotenv, dotenv_values

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import BatchHttpRequest, BatchError

def BuildService():
    # not my code (straight from the official gmail api docs)
    # more info about how this works should be gotten from the api docs.
    # url: https://developers.google.com/gmail/api/quickstart/python
    creds = None
    scopes = BuildScopes()

    if os.path.exists("files/token.json"):
        creds = Credentials.from_authorized_user_file("files/token.json", scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "files/credentials.json", scopes
            )
            creds = flow.run_local_server(port=0)
        with open("files/token.json", "w") as token:
            token.write(creds.to_json())
    
    service = build('gmail', 'v1', credentials=creds)
    return service

def BuildScopes():
    load_dotenv()

    config = dotenv_values()
    scopes = json.loads(config['SCOPES'])
    return scopes



def ExecuteBatchRequest(requests):
    batch = BatchHttpRequest(batch_uri = 'https://gmail.googleapis.com/batch')

    for request in requests:
        batch.add(request)
    
    batch.execute()