import json, requests
from flask import Flask, render_template, redirect, url_for
import paramiko
import sqlite3
from flask_cors import CORS
from flask import request
import zoopla
import time, json
import threading
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

job_status = False
@app.route("/")
def home():
    return render_template("search_property.html", data=job_status)





@app.route("/formData", methods=['POST','GET'])
def add_criteria():
    global job_status
    job_status =True
    criteria = request.get_json()
    print(criteria)
    socketio.emit("update","Starting Process..")
    time.sleep(1)
    for x in zoopla.DataCrawler().main(criteria):
        print('from flask app',x)
        socketio.emit("update", x)
        if'done' in x:
            job_status=False
            socketio.emit("update",'done')

    return 'done'



if __name__ =="__main__":
    # app.run(host= "0.0.0.0", debug=True ,port=80, threaded=True)
    socketio.run(app, host= "0.0.0.0", port=80, debug=True)


