import json, requests
from flask import Flask, render_template, redirect, url_for
from flask_cors import CORS
from flask import request
import zoopla
import time, json
import sqlite3
app = Flask(__name__)

job_status = False
@app.route("/")
def home():
    try:
        conn = sqlite3.connect('job_logs.db')
        records = conn.execute("select * from job_status")
        records = records.fetchall()
    except:
        records= ''

    return render_template("search_property.html", data=records)





@app.route("/formData", methods=['POST','GET'])
def add_criteria():
    
    global job_status
    job_status =True
    criteria = request.get_json()
    print(criteria)
    time.sleep(1)
    for x in zoopla.DataCrawler().main(criteria):
        print('from flask app',x)
        
    return 'done'



if __name__ =="__main__":
    app.run(host= "0.0.0.0", debug=True ,port=80, threaded=True)


