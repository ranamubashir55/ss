import json, requests
from flask import Flask, render_template
import paramiko
import sqlite3
from flask_cors import CORS
from flask import request
import zoopla
import threading
app = Flask(__name__)

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
    zoopla.DataCrawler().main(criteria)
    job_status=False




if __name__ =="__main__":
    # app.run(host= "0.0.0.0", debug=True ,port=80, threaded=True)
    app.run(host= "0.0.0.0", port=80, debug=True, threaded=True)


