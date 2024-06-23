import os.path
import json

from dotenv import load_dotenv, dotenv_values
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def Main():
    categorylabels = BuildLabels()
    sortingLabels = BuildSortingLabels()
    thrashables = BuildThrashables()
    service = BuildCredentials()

    if service == None:
        return
    
    UpdateGmailLabels(service, categorylabels)
    SortAllMails(service, sortingLabels)  

def BuildScopes():
    load_dotenv()

    config = dotenv_values()
    scopes = json.loads(config['SCOPES'])
    return scopes
def BuildLabelFile():
    file = open('labels.json')
    categories = json.load(file)
    return categories
def BuildCredentials():
    # not my code (straight from the official gmail api docs)
    # more info about how this works should be gotten from the api docs.
    creds = None
    scopes = BuildScopes()

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", scopes
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    service = build('gmail', 'v1', credentials=creds)
    return service
def BuildLabels():
    categories = BuildLabelFile()
    labels = []

    for categorie in categories['Categories']:
        labels.append(categorie)
        for label in categories['Categories'][categorie]:
            labels.append(f'{categorie}/{label}')
    return labels
def BuildSortingLabels():
    categories = BuildLabelFile()
    labels = []
    counter = 0

    for categorie in categories['Categories']:
        counter += 1
        for label in categories['Categories'][categorie]:
            counter += 1
            labels.append(label)
    return labels
def BuildThrashables():
    categories = BuildLabelFile()
    thrashables = []

    for thrashable in categories['To be Thrashed']:
        thrashables.append(thrashable)
    return thrashables

def GetAllMailIds(service):
    results = []
    next_page_token = None
    while next_page_token is not None or results == []:
        mails = service.users().messages().list(userId='me', pageToken=next_page_token).execute()
        if 'nextPageToken' in mails:
            next_page_token = mails['nextPageToken']
        else:
            next_page_token = None
        results.extend(mails['messages'])

    return results
def GetMailInfoById(service, id):
    mail = service.users().messages().get(userId='me', id=id).execute()
    return mail
def GetAllMailInfo(service):
    all_mail_ids = GetAllMailIds(service)
    mails = []

    for mail in all_mail_ids:
        mail_id = mail['id']
        mail_info = GetMailInfoById(service, mail_id)
        mails.append(mail_info)

    return mails

def UpdateGmailLabels(service, labels):
    #this is for if another label gets added to the json file
    existing_labels = service.users().labels().list(userId='me').execute()
    
    for label in labels:
        exists = False
        for existing_label in existing_labels['labels']:
            if label == existing_label['name']:
                exists = True
                break
        
        if not exists:
            new_label = {
                'name': label,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            label_info = service.users().labels().create(userId='me', body=new_label).execute()
def SortAllMails(service, labels):
    mails = GetAllMailInfo(service)
    all_labels = service.users().labels().list(userId='me').execute()

    for mail in mails:
        sorting_label = None
        sorting_label_id = None
        mail_id = mail['id']
        mail_headers = mail['payload']['headers']
        mail_labels = mail['labelIds']

        if 'INBOX' in mail_labels:
            for header in mail_headers:
                if header['name'] == 'From':
                    for label in labels:
                        if header['value'].lower().__contains__(label.lower()):
                            sorting_label = label

            if sorting_label is not None:
                for label in all_labels['labels']:
                    if label['name'].__contains__(sorting_label):
                        sorting_label_id = label['id']

                new_label_body = {
                    'removeLabelIds': 'INBOX',
                    'addLabelIds': sorting_label_id
                }
                service.users().messages().modify(userId='me', id=mail_id, body=new_label_body).execute()


def deleteAllThrashableMails(service, thrashables):
    return

def ConvertToReadableSender(sender):
    test = None
    return test

if __name__ == '__main__':
    Main()