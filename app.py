from flask import Flask, jsonify, request, make_response
import io
import json
import os
import torch


import preprocess
import model

app = Flask(__name__)


@app.route('/')
def index():
    return "Apzima"


@app.route('/predict/level2', methods = ['POST'])
def predict_level2():
    data = request.get_json()
    sent = data['Chief complaint']
    sent = sent + ". " + str(data['Age'])
    sent = sent + ". " + data['Sex']
    sent = sent + ". " + str(data['Height']) #실제로는 Obestiy 계산하여 처리
    sent = sent + ". " + str(data['Weight']) #실제로는 Obestiy 계산하여 처리
    # level2 = predict_level2(sent)
    level2 = "급성 복통"
    response = {"level2" : level2}
    return make_response(jsonify(response), 200)




@app.route('/predict/diagnosis', methods = ['POST'])
def predict_diagnosis():
    data = request.get_json()
    if preprocess.checkData(data) == 400:
        return make_response(("Bad Request", 400))

    sentence = preprocess.makeSentence(data)
    disaseList = model.predict(sentence)
    response = {"diseasesList" : disaseList}
    return make_response(jsonify(response), 200)




def process(sentece):
    #processing
    return "질문에 대한 답변입니다.";


@app.route('/counseling', methods = ['POST'])
def counseling():
    # sent -> bert -> gpt -> result
    data = request.get_json()
    answer = process(data['question'])
    response = {"answer" : answer}
    return make_response(jsonify(response), 200)


if __name__ == '__main__':
    # app.run()
    app.run(debug = True)
    model.init()
