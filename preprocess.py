

def check_data(data):
    required = ['Chief complaint', 'Age', 'Sex', 'Height', 'Weight']
    for c in required:
        if c not in data:
            return 400
    return 1

def obesity(Weight, Height):
    if Height <= 0 :
        return "알 수 없음"
    BMI = Weight / (Height/100)**2
    if BMI < 0:
        return '알 수 없음'
    elif BMI < 20.0:
        return '저체중'
    elif BMI <= 24.0:
        return '정상'
    elif BMI <= 29.0:
        return '과체중'
    return '비만'

def ageband(age):
    return str(age//10*10) + "대"

def make_sentence_l2(data):
    sent = data['Chief complaint']
    sent = sent + ". " + ageband(data['Age'])
    sent = sent + ". " + data['Sex']
    sent = sent + ". " + Obesity(data[Weight], data[Height])

def make_sentence_diag(data):
    cols = ['Sex', 'Onset', 'Location',
            'Duration', 'Course', 'Experience', 'Character', 'Associated Sx.',
            'Factor', 'Event', '약물 투약력', '사회력',
            '가족력', '외상력', '과거력', '여성력']

    sent = data['Chief complaint'] + ". " + ageband(data['Age']) + ". "
    for c in cols:
        if c in data:
            sent = sent + data[c] + ". "
        else:
            sent = sent + ". "
    sent = sent + obesity(data['Weight'], data['Height'])
    return sent
