from types import MethodType
from flask import Flask, request, Response, jsonify, render_template, request, flash
from datetime import datetime
from mysql.connector import Error, errorcode, pooling
from mysql.connector.connection import MySQLConnection
from typing import Dict, List
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
import urllib
import mysql.connector
import logging
import logging.handlers
import re
from thread import Update_thread

my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.INFO)
loghandler = logging.handlers.TimedRotatingFileHandler('./log/logfile.log', when='midnight')
loghandler.setFormatter(logging.Formatter("%(asctime)s — %(levelname)s — %(message)s"))
my_logger.addHandler(loghandler)

#params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};SERVER=mtksqlconsdbt1.mediatek.inc;DATABASE=CPPM;UID=srv_cppm2;PWD=srv_cppm20@20")
params = urllib.parse.quote_plus("DRIVER={SQL Server};SERVER=127.0.0.1:3306;DATABASE=cppm;UID=root;PWD=jerrys0653016")

engine = create_engine("mysql+mysqlconnector://root:jerrys0653016@localhost/cppm")

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

app = Flask(__name__)

@app.route("/")
def home():
#    return "Hello, Flask"
    return render_template("index.html")

@app.route("/database")
def database():
    conn = mysql.connector.connect(host='localhost', port=3306, database='cppm', user='root', password='jerrys0653016')
    cur = conn.cursor()
    search = "SELECT * FROM `mtk` AS `TableA` LEFT JOIN  `postman` AS `TableB` ON `TableB`.`mac_address`=`TableA`.`mac_address`"
    cur.execute(search)
    result = cur.fetchall()
    conn.close()
    return render_template("database.html",result=result)

@app.route("/log", methods=['GET', 'POST'])
def log():
    with open ("log/logfile.log", "r") as f:
        content = f.readlines()
    return render_template('log.html', content=content)

@app.route('/', methods=['POST'])
def authority():
    my_logger.info("Request Data: %s", request.json)
    t = Update_thread(0, request.json, Session, engine)
    t.start()
    return Response(status=200)   

def get_pool_info() -> Dict:
    """Get information about the current connections and pool"""
    return {
        "pool id": id(engine.pool),
        "connections in current pool": (
            engine.pool.checkedin() + engine.pool.checkedout()
        ),
    }

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=80,debug=True) # need fixed PORT 80