#!/usr/bin/python3

import os
import subprocess
from flask import Flask, jsonify
app = Flask(__name__)
import time
    
while True:
    @app.route('/')
    def index():
        return "Hello, World!"

    '''
    @app.route("/start", methods=['GET'])
    def get_data():
        data1 = os.popen('head -1 ./values.txt').read().rstrip('\n').split(' ')

        x1 = data1[0]
        y1 = data1[1]
        ang1 = data1[2]
        dist1 = data1[3]
        Bang1 = data1[4]
        Bdist1 = data1[5]
        depth1 = data1[6]
        Tang1 = data1[7]
        Tdist1 = data1[8]
        
        coordinates1 = {'x1': x1, 'y1': y1, 'xyang1': ang1, 'xydist1': dist1, 'Bang1': Bang1, 'Bdist1': Bdist1, 'depth1': depth1, 'Tang1': Tang1, 'Tdist1': Tdist1}

        return jsonify({'coordinates1': coordinates1})

'''
    
    @app.route("/coordinates", methods=['GET'])
    def get_tasks():
        data = os.popen('tail -1 /home/achencom/values.txt').read().rstrip('\n').split(' ')

        x = data[0]
        y = data[1]
        ang = data[2]
        dist = data[3]
        Bang = data[4]
        Bdist = data[5]
        depth = data[6]
        Tang = data[7]
        Tdist = data[8]
        Gang = data[9]
        Gdist = data [10]
        #print(data)
        #print("hi")
        
        #print(coordinates)
        coordinates = {'x': x, 'y': y, 'xyang': ang, 'xydist': dist, 'Bang': Bang, 'Bdist': Bdist, 'depth': depth, 'Tang': Tang, 'Tdist': Tdist, 'Bang': Bang, 'Bdist': Bdist}
        
        return jsonify({'coordinates': coordinates})

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=8000, debug=False)

    
