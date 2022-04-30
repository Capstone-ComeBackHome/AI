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
    if preprocess.check_data(data) == 400:
        return make_response(("Bad Request", 400))

    sentence = preprocess.make_sentence_l2(data)
    # level2 = l2_model.predict(sentence)
    level2 = "급성 복통"
    response = {"level2" : level2}
    return make_response(jsonify(response), 200)




@app.route('/predict/diagnosis', methods = ['POST'])
def predict_diagnosis():
    data = request.get_json()
    if preprocess.check_data(data) == 400:
        return make_response(("Bad Request", 400))

    sentence = preprocess.make_sentence_diag(data)
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
    app.run(debug = False, host = '0.0.0.0')
