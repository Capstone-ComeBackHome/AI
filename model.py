# -*- coding: utf-8 -*-
"""model

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PGlK6IvTZ69o5pXGxHo-F161fyLJVKQO
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

import torch
from torch import nn
import torch.nn.functional as F
from torch.utils.data import DataLoader

from kobert import get_pytorch_kobert_model
from kobert import get_tokenizer
import gluonnlp as nlp

from konlpy.tag import Okt

from joblib import dump, load
import pickle

from flask import Flask, jsonify, request, make_response

import preprocessor

class BERTClassifier(nn.Module):
    def __init__(self,
                 bert,
                 hidden_size = 768,
                 num_classes = 0,
                 dr_rate=None,
                 params=None):
        super(BERTClassifier, self).__init__()
        self.bert = bert
        self.dr_rate = dr_rate
        self.classifier = nn.Linear(hidden_size , num_classes)

        if dr_rate:
            self.dropout = nn.Dropout(p=dr_rate)

    def gen_attention_mask(self, token_ids, valid_length):
        attention_mask = torch.zeros_like(token_ids)
        for i, v in enumerate(valid_length):
            attention_mask[i][:v] = 1
        return attention_mask.float()

    def forward(self, token_ids, valid_length, segment_ids):
        attention_mask = self.gen_attention_mask(token_ids, valid_length)

        _, pooler = self.bert(input_ids = token_ids, token_type_ids = segment_ids.long(), attention_mask = attention_mask.float().to(token_ids.device))
        if self.dr_rate:
            out = self.dropout(pooler)
        else:
            out = pooler
        return self.classifier(out)

class DiagnosisModelHandler():
    """
    A custom model handler implementation.
    """

    def __init__(self):
        self.initialized = False
        self.le = LabelEncoder()
        self.target = 0
        self.model = None
        self.transform = None
        self.filter_male = None
        self.filter_female = None
        self.initialize()

    def initialize(self):
        #label encoder
        self.le.classes_ = np.load('classes.npy', allow_pickle = True)
        self.target = len(self.le.classes_)
        self.load_bert()
        self.load_filter()
        self.initialized = True

    def load_bert(self):
        kobert_model, vocab = get_pytorch_kobert_model()
        self.model = BERTClassifier(kobert_model, num_classes = self.target)
        self.model.load_state_dict(torch.load('../saved_model/kobert1_state_dict.pth',  map_location=torch.device('cpu')))
        self.model.eval()
        tokenizer = get_tokenizer()
        tok = nlp.data.BERTSPTokenizer(tokenizer, vocab, lower=False)
        self.transform = nlp.data.BERTSentenceTransform(tok, max_seq_length=128, pad=True, pair=False)

    def load_filter(self):
        with open('diagnosis_male_only.pkl', 'rb') as f:
            diagnosis_male_only = pickle.load(f)
        with open('diagnosis_female_only.pkl', 'rb') as f:
            diagnosis_female_only = pickle.load(f)
        self.filter_male = torch.FloatTensor([0 if c in diagnosis_female_only else 1 for c in self.le.classes_ ])
        self.filter_female = torch.FloatTensor([0 if c in diagnosis_male_only else 1 for c in self.le.classes_ ])

    def preprocess(self, data):
        if preprocessor.check_data(data) == 400:
            return 400
        return preprocessor.make_sentence_diag(data)


    def inference(self, model_input):
        with torch.no_grad():
            input = self.transform([model_input])
            dataloader = torch.utils.data.DataLoader(input, batch_size=1)
            token_ids, valid_length, segment_ids = dataloader
            token_ids = token_ids.long()
            valid_length = valid_length
            segment_ids = segment_ids.long()
            model_output = self.model(token_ids, valid_length, segment_ids)
        return model_output


    def postprocess(self, sex, inference_output):
        inference_output = nn.functional.softmax(inference_output, dim = 1)
        if sex == "남성":
            inference_output = torch.mul(inference_output, self.filter_male)
        elif sex == "여성":
            inference_output = torch.mul(inference_output, self.filter_female)
        top3 = torch.topk(inference_output, k = 3, dim = 1, sorted = True)
        prob_list = [int(i*100)/100 for i in top3.values[0]]
        disease_list = self.le.inverse_transform(top3.indices[0].numpy()).tolist()
        return prob_list, disease_list

    def handle(self, data):
        model_input = self.preprocess(data)
        if model_input == 400 :
            raise Exception("Bad Request")
        model_output = self.inference(model_input)
        return self.postprocess(data['Sex'], model_output)

# data = {
#     "Chief complaint" : "배가 아파요",
#     "Age" : 24,
#     "Sex" : "남성",
#     "Height" : 165,
#     "Weight" : 100,
#     "Onset" : "이틀 전",
#     "Location" : "없음",
#     "Course" : "점점 심해짐",
#     "Character" : "속 쓰림",
#     "Associated Sx." : "구토, 두통",
#     "Factor" : "누으면 괜찮아짐",
#     "약물 투약력" : "없음",
#     "사회력" : "술 3회/주",
#     "과거력" : "당뇨"
# }

# model = DiagnosisModelHandler()
# model.handle(data)

"""-------"""

class DNN(nn.Module):

    def __init__(self, in_features, out_features):
        super(DNN, self).__init__()
        self.l1 = nn.Linear(in_features, 512)
        self.l2 = nn.Linear(512, 64)
        self.l3 = nn.Linear(64, out_features)
        self.dropout = nn.Dropout(p = 0.2)
        torch.nn.init.xavier_normal_(self.l1.weight)
        torch.nn.init.xavier_normal_(self.l2.weight)
        torch.nn.init.xavier_normal_(self.l3.weight)

    def forward(self, x):
        x = F.relu(self.l1(x))
        x = self.dropout(x)
        x = F.relu(self.l2(x))
        x = self.dropout(x)
        x = self.l3(x)
        return x

class Level2ModelHandler():
    def __init__(self):
        self.initialized = False
        self.le = LabelEncoder()
        self.target = 0
        self.stopwords = ['이', '가', '을', '를', '요', '너무', '진짜', '부터', '나', '저', '제', '랑', '에', '할', '해', '해요', '했', '했어요', '돼요', '됐어요', '되어']
        self.okt = Okt()
        self.complaint_vectorizer = None
        self.onset_vectorizer = None
        self.model = None
        self.filter_male = None
        self.filter_female = None
        self.initialize()

    def initialize(self):
        #label encoder
        self.le.classes_ = np.load('level2_classes.npy', allow_pickle = True)
        self.target = len(self.le.classes_)
        self.load_model()
        self.load_filter()
        self.load_vectorizer()
        self.initialized = True

    def load_model(self):
        state_dict = torch.load('../saved_model/dnn_state_dict.pth', map_location = torch.device('cpu'))
        self.model = DNN(state_dict['l1.weight'].size()[1], state_dict['l3.weight'].size()[0])
        self.model.load_state_dict(state_dict)
        self.model.eval()

    def load_filter(self):
        with open('level2_male_only.pkl', 'rb') as f:
            level2_male_only = pickle.load(f)
        with open('level2_female_only.pkl', 'rb') as f:
            level2_female_only = pickle.load(f)
        self.filter_male = torch.FloatTensor([0 if c in level2_female_only else 1 for c in self.le.classes_ ])
        self.filter_female = torch.FloatTensor([0 if c in level2_male_only else 1 for c in self.le.classes_ ])

    def load_vectorizer(self):
        self.complaint_vectorizer = load('complaint_vectorizer.pkl')
        self.onset_vectorizer = load('onset_vectorizer.pkl')

    def remove_stopwords(self, text):
        clean_words = []
        for word in self.okt.morphs(text):
            if word not in self.stopwords:
                clean_words.append(word)
        return ' '.join(clean_words)

    def preprocess(self, data):
        if preprocessor.check_data(data) == 400:
            raise Exception("Bad Request")
        data['Chief complaint'] = self.remove_stopwords(data['Chief complaint'])
        data['Onset'] = self.remove_stopwords(data['Onset'])
        complaint_tfidf =  self.complaint_vectorizer.transform([data['Chief complaint']]).toarray()[0].tolist()
        onset_tfidf =  self.onset_vectorizer.transform([data['Onset']]).toarray()[0].tolist()
        return torch.FloatTensor([[0 if data['Sex'] == "남성" else 1, data['Age']] +  complaint_tfidf + onset_tfidf])

    def inference(self, model_input):
        return self.model(model_input)

    def postprocess(self, sex, inference_output):
        inference_output = nn.functional.softmax(inference_output, dim = 1)
        if sex == "남성":
            inference_output = torch.mul(inference_output, self.filter_male)
        elif sex == "여성":
            inference_output = torch.mul(inference_output, self.filter_female)
        output = torch.argmax(inference_output, dim = 1).detach().numpy()
        return self.le.inverse_transform(output)[0]

    def handle(self, data):
        model_input = self.preprocess(data)
        model_output = self.inference(model_input)
        return self.postprocess(data['Sex'], model_output)

# data = {
#     "Chief complaint" : "생리를 안해요",
#     "Age" : 24,
#     "Sex" : "남성",
#     "Onset" : "이틀 전",
#     "Weight" : 0,
#     "Height" : 0
# }
# model = Level2ModelHandler()
# model.handle(data)
