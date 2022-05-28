from flask import Flask, jsonify, request, make_response
import io
import json
import os
import torch

from model import DiagnosisModelHandler, Level2ModelHandler
import questions

app = Flask(__name__)
diag_model = DiagnosisModelHandler()
level2_model = Level2ModelHandler()

@app.route('/')
def index():
    return "Apzima"


@app.route('/predict/level2', methods = ['POST'])
def predict_level2():
    data = request.get_json()
    result = level2_model.handle(data)
    response = {"QuestionsDict" : questions[data['Sex']][result]}
    return make_response(jsonify(response), 200)


@app.route('/predict/diagnosis', methods = ['POST'])
def predict_diagnosis():
    data = request.get_json()
    probList, disaseList = diag_model.handle(data)
    response = {"diseasesList" : disaseList,
                "probList" : probList}
    return make_response(jsonify(response), 200)


if __name__ == '__main__':
    # app.run()
    app.run(debug = False, host = '0.0.0.0')
