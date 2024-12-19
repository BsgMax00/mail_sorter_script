import json

def BuildLabelFile():
    file = open('files/labels.json')
    categories = json.load(file)
    return categories

def BuildSortingLabels():
    all_labels = BuildLabelFile()
    labels = []

    for label in all_labels['Sort']:
        labels.append(label)
        for sub_label in all_labels['Sort'][label]:
            labels.append(f'{label}/{sub_label}')

    print("Sorting labels have been build.")
    return labels

def BuildRemovableLabels():
    all_labels = BuildLabelFile()
    labels = []

    for label in all_labels['Remove']:
        labels.append(label)

    print("Removable labels have been build.")
    return labels