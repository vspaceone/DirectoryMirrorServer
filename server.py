#!/usr/bin/python3

import os, time
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
VERSION_MINOR = 3
VERSION_PATCH = 1
VERSION = "v"+str(VERSION_MAJOR)+"."+str(VERSION_MINOR)+"."+str(VERSION_PATCH)


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


from markupsafe import Markup
@app.template_filter('urlencode')
def urlencode_filter(s):
    if type(s) == 'Markup':
        s = s.unescape()
    s = s.encode('utf8')
    s = urllib.parse.quote(s)
    return Markup(s)

def printUsage():
    print("Usage: server.py")

@app.route("/")
def showHome():
    f =  open('directory_crawled.json')
    data = json.load(f)
    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat('directory_crawled.json')
    resp = flask.make_response(flask.render_template('home.html', version=VERSION, directory=data, lastupdate=time.ctime(mtime)), 200)
    resp.headers["Content-type"] = "text/html; charset=utf-8"
    return resp

@app.route("/doc.html")
def showDoc():
    resp = flask.make_response(flask.render_template('doc.html', version=VERSION), 200)
    resp.headers["Content-type"] = "text/html; charset=utf-8"
    return resp

@app.route("/spaces")
def showDirectory():
	return flask.send_from_directory('', "directory.json")

@app.route("/spaces_crawled")
def showDirectoryCrawled():
	return flask.send_from_directory('', "directory_crawled.json")

@app.route("/spaces/<everything:spacename>")
def showSpace(spacename):
	(r,code) = getSpaceJSON(spacename)
	resp = flask.make_response(r,code)
	resp.headers["Content-type"] = "application/json; charset=utf-8"
	return resp

@app.route("/stats/<everything:spacename>.html")
def showSpaceStats(spacename):
	(template, api, code) = getStatsPage(spacename)
	resp = flask.make_response(flask.render_template(template, version=VERSION, api=api, spacename=spacename), code)
	resp.headers["Content-type"] = "text/html; charset=utf-8"
	return resp

def getStatsPage(spacename):
    with open('directory.json',encoding='utf-8') as f:
        data = json.load(f)
        spacename = urllib.parse.unquote(spacename)
        logger.info("Looking up: "+spacename)
        try:
            URL = data[spacename]
        except:
            logger.warn("Space not in directory!")
            return ("spacestatsError.html",json.loads('{"error":"Space not in directory!", "errorcode":-4}'),404)

        try:
            r = json.loads(requests.get(url=URL).text)
            if r["api"] == "0.13":
                if r["state"] and r["location"] and r["contact"]:
                    return ("spacestatsv0.13.html", r, 200)
                else:
                    logger.warn("No valid SpaceAPI found!")
                    return ("spacestatsError.html", json.loads('{"error":"No valid SpaceAPI found!", "errorcode":-7}'),404)
            elif r["api"] == "0.12" or r["api"] == "0.11" or ["api"] == "0.10" or ["api"] == "0.9":
                if r["contact"]:
                    return ("spacestatsv0.12.html", r, 200)
                else:
                    logger.warn("No valid SpaceAPI found!")
                    return ("spacestatsError.html", json.loads('{"error":"No valid SpaceAPI found!", "errorcode":-7}'),404)
            elif r["api"] == "0.8":
                return ("spacestatsv0.8.html", r, 200)
            else:
                logger.warn("No template for this api version!")
                return ("spacestatsError.html",json.loads('{"error":"No template for this api version! '+r["api"]+'", "errorcode":-5}'),404)
        except:
            logger.warn("Could not load json!")
            return ("spacestatsError.html",json.loads('{"error":"Could not load json!", "errorcode":-6}'),404)

def getSpaceJSON(spacename):
    with open('directory.json',encoding='utf-8') as f:
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


app.run(port=5001)
