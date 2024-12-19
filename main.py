#import helper classes
from serviceHelper import BuildService
from labelHelper import BuildSortingLabels, BuildRemovableLabels

def main():
    print("Program has started.")

    sortingLabels = BuildSortingLabels()
    removableLabels = BuildRemovableLabels()
    service = BuildService()

    if service == None:
        print("service was unable to be made.")
        return
    
    UpdateGmailLabels(service, sortingLabels)
    mails = CollectAllMails(service)
    SortMails(service, mails, sortingLabels)
    DeleteMails(service, mails, removableLabels)
    print("Program has succesfully finished.")
    
def UpdateGmailLabels(service, labels):
    print("Started updating labels.")
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
            service.users().labels().create(userId='me', body=new_label).execute()
    print("Finished updating labels.")

def SortMails(service, mails, labels):
    print("Started sorting all mails in inbox.")
    for mail in mails:
        sortingLabel = FindSortingLabel(mail, labels)

        if sortingLabel is not None:
            sortingLabelId = FindSortingLabelId(service, sortingLabel)
            new_label_body = {
                'addLabelIds': sortingLabelId,
                'removeLabelIds': 'INBOX'
            }
            service.users().messages().modify(userId='me', id=mail['id'], body=new_label_body).execute()
            mails.remove(mail)
    print("Finished sorting all mails in inbox")

def DeleteMails(service, mails, labels):
    print("Started deleting all mails that have to be removed.")
    for mail in mails:
        sortingLabel = FindSortingLabel(mail, labels)

        if sortingLabel is not None:
            service.users().messages().delete(userId='me', id=mail['id']).execute()
            mails.remove(mail)
    print("Finished deleting all mails that had to be removed.")

def CollectAllMails(service):
    print("Started Collecting all mails.")
    messageIds = []
    containsNextPageToken = True
    nextPageToken = ''

    while(containsNextPageToken):
        messages = service.users().messages().list(userId='me', pageToken=nextPageToken).execute()
        messageIds += messages['messages']

        if 'nextPageToken' in messages:
            nextPageToken = messages['nextPageToken']
        else:
            containsNextPageToken = False

    print(f"Program has collected {len(messageIds)} amount of email ID's.")

    mails = []

    batchMessageIds = [messageIds[i:i + 50] for i in range(0, len(messageIds), 50)]

    for index, messageId in enumerate(batchMessageIds):
        print(f'{index + 1} / {len(batchMessageIds)}')
        for id in messageId:
            mail = service.users().messages().get(userId='me', id=id['id']).execute()
            if 'labelIds' not in mail or 'INBOX' in mail['labelIds']:
                mails.append(mail)

    print("All mails have been collected.")
    return mails

def FindSortingLabel(mail, labels):
        sortingLabel = None

        for header in mail['payload']['headers']:
            if header['name'] == 'From':
                for label in labels:
                    if header['value'].lower().__contains__(label.lower().split('/')[-1]):
                        sortingLabel = label

        return sortingLabel

def FindSortingLabelId(service, label):
    existingLabels = service.users().labels().list(userId='me').execute()

    for existingLabel in existingLabels['labels']:
        if label in existingLabel['name'] :
            return existingLabel['id']

main()