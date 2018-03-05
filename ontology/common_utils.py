def clean_skill_label(label):
    if label is None:
        return label
    # Clean 1 : remove parenthesis content
    start = label.find('(')
    end = label.find(')')
    if start != -1 and end != -1:
        cleaned_label = label[:start]
        if end+1 < len(label):
            cleaned_label += label[end+1:]
    else:
        cleaned_label = label

    cleaned_label = cleaned_label.replace("'",'').replace('-', '_').strip().replace(' ', '_')
    return cleaned_label


def filter_dict(dic, _filter):
    result = dict()
    for k,v in dic.items():
        if k in _filter:
            result[k] = v
    return result