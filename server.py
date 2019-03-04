#!/bin/python

import os
import json
import configparser
import sys
import logging
import signal
import requests
import urllib.parse
import flask
from werkzeug.routing import PathConverter

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


PORT = 8080
IP = "0.0.0.0"

# Setting up logger
logger = logging.getLogger('DirectoryMirrorServer.py')
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
logger.info("Starting DirectoryMirrorServer...")
signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGINT, sigint_handler)

#def do_GET(s):
#	s.send_response(200)
#	s.send_header("Content-type","application/json; charset=utf-8")
#	s.end_headers()
#	s.wfile.write(generateDirectory("internal"))

def printUsage():
	print("Usage: server.py")

@app.route("/")
def showHome():
	resp = flask.make_response(flask.render_template('home.html', version="v"+str(VERSION_MAJOR)), 200)
	resp.headers["Content-type"] = "text/html; charset=utf-8"
	return resp

@app.route("/directory.json")
def showDirectory():
	return flask.send_from_directory('', "directory.json")

@app.route("/spaces/<everything:spacename>.json")
def showSpace(spacename):
	(r,code) = getSpaceJSON(spacename)
	resp = flask.make_response(r,code)
	resp.headers["Content-type"] = "application/json; charset=utf-8"
	return resp

@app.route("/stats/<spacename>.html")
def showSpaceStats(spacename):
	resp = flask.make_response(flask.render_template('overview.html', showname=showname), 200)
	resp.headers["Content-type"] = "text/html; charset=utf-8"
	return resp

def getSpaceJSON(spacename):
    with open('directory.json') as f:
        data = json.load(f)
        spacename = urllib.parse.unquote(spacename)
        logger.info("Looking up: "+spacename)
        try:
            URL = data[spacename]
        except:
            return ('{"error":"Space not in directory!", "errorcode":-1}',404)

        try:
            return (requests.get(url=URL).text,200)
        except:
            return ('{"error":"Could not load json!", "errorcode":-2}',404)
