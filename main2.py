#import helper classes
from serviceHelper import BuildService, ExecuteBatchRequest
from labelHelper import BuildSortingLabels, BuildRemovableLabels

def main():
    sortingLabels = BuildSortingLabels()
    service = BuildService()

    if service == None:
        return
    
    UpdateGmailLabels(service, sortingLabels)
    
def UpdateGmailLabels(service, labels):
    existing_labels = service.users().labels().list(userId='me').execute()
    updated_labels = []

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
            updated_labels.append(service.users().labels().create(userId='me', body=new_label))

    ExecuteBatchRequest(updated_labels)

def SortMails(service, labels):
    pass


main()