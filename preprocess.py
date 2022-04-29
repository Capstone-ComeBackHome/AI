

def checkData(data):
    required = ['Chief complaint', 'Age', 'Sex', 'Height', 'Weight']
    for c in required:
        if c not in data:
            return 400
    return 1


def makeSentence(data):
    cols = ['Chief complaint', 'Age', 'Sex', 'Onset', 'Location',
            'Duration', 'Course', 'Experience', 'Character', 'Associated Sx.',
            'Factor', 'Event', '약물 투약력', '사회력',
            '가족력', '외상력', '과거력', '여성력',  'Height', 'Weight']
    data['Age'] = str(data['Age'])
    data['Height'] = str(data['Height'])
    data['Weight'] = str(data['Weight'])

    sent = ""
    for c in cols:
        if c in data:
            sent = sent + data[c] + ". "
        else:
            sent = sent + ". "

    return sent
