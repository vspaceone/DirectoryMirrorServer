#!/usr/bin/python3


import json
import sys
import logging
import signal
import flask
from werkzeug.routing import PathConverter
from influxdb import InfluxDBClient

DBNAME = "MAXSENSE_STATS"
USE_INFLUX = True

if USE_INFLUX:
    client = InfluxDBClient("localhost",8086,"root","root",DBNAME)
    client.create_database(DBNAME)
    client.switch_database(DBNAME)

class EverythingConverter(PathConverter):
	regex = '.*?'



app = flask.Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300
app.url_map.converters['everything'] = EverythingConverter

# Constants
VERSION_MAJOR = 0
VERSION_MINOR = 1
VERSION_PATCH = 0
VERSION = "v"+str(VERSION_MAJOR)+"."+str(VERSION_MINOR)+"."+str(VERSION_PATCH)


# Setting up logger
logger = logging.getLogger('MaxSense')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

logger.addHandler(ch)

@app.after_request
def add_header(response):
	response.headers['Cache-Control'] = 'must-validate'
	return response

def sigterm_handler(_signo,_stack_frame):
	logger.info("SIGTERM received. Cleaning up...")
	sys.exit(0)

def sigint_handler(_signo, _stack_frame):
	logger.info("SIGINT received. Cleaning up...")
	sys.exit(0)

logger.info("Running version "+VERSION)
logger.info("Starting MaxSense...")
signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGINT, sigint_handler)



def printUsage():
	print("Usage: MaxSense")

@app.route("/add",methods = ['POST'])
def addSense():
	try:
		dat = json.loads(flask.request.data)

		measurement = {
			"measurement": dat["node"],
			"fields": {
				"temperature": float(dat["temperature"]),
				"humidity": float(dat["humidity"])
			}
		}

		if USE_INFLUX:
			logger.info("Write to INFLUX" + str(measurement))
			client.write_point(measurement)

		resp = flask.make_response("<html><h1>OK</h1></html>", 200)
		resp.headers["Content-type"] = "text/html; charset=utf-8"
	except Exception as e:
		resp = flask.make_response("<html><h1>FAILED</h1><p>"+str(e)+"</p></html>", 403)
		resp.headers["Content-type"] = "text/html; charset=utf-8"
	return resp




app.run(port=5001)
