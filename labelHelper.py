import json

def BuildLabelFile():
    file = open('files/labels.json')
    categories = json.load(file)
    return categories

def BuildSortingLabels():
    all_labels = BuildLabelFile()
    labels = []

    for label in all_labels['To be sorted']:
        labels.append(label)
        for sub_label in all_labels['To be sorted'][label]:
            labels.append(f'{label}/{sub_label}')

    return labels

def BuildRemovableLabels():
    all_labels = BuildLabelFile()
    labels = []

    for label in all_labels['To be removed']:
        labels.append(label)

    return labels