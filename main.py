import os.path
import json

from serviceHelper import BuildService

from dotenv import load_dotenv, dotenv_values
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def Main():
    service = BuildService()

    if service == None:
        return

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

    test = None
    return test

if __name__ == '__main__':
    Main()