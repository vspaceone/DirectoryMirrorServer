#!/bin/python

import os
import logging
import json
import configparser
import requests
import jsonschema
import time

from influxdb import InfluxDBClient
from multiprocessing import Process, Manager, Lock

from ApiParser import parser13

DBNAME = "SPACEAPI_STATS"
USE_INFLUX = True
USE_EXPORT_DIRECTORY = True


if USE_INFLUX:
    client = InfluxDBClient("localhost",8086,"root","root",DBNAME)
    client.create_database(DBNAME)
    client.switch_database(DBNAME)

VERSION_MAJOR = 0
VERSION_MINOR = 2
VERSION_PATCH = 1
VERSION = "v" + str(VERSION_MAJOR) + "." + str(VERSION_MINOR) + "." + str(VERSION_PATCH)

logger = logging.getLogger("collector.py")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

logger.addHandler(ch)

logger.info("Running version " + VERSION)


schema8 = json.load(open("schema-master/8.json"))
schema9 = json.load(open("schema-master/9.json","r"))
schema11 = json.load(open("schema-master/11.json","r"))
schema12 = json.load(open("schema-master/12.json","r"))
schema13 = json.load(open("schema-master/13.json","r"))
schema14 = json.load(open("schema-master/14-draft.json","r"))



def addToDir(directory, spacename, apistate, url):
    counterIdx = {
        "sum": 0,
        "0.13": 1,
        "0.12": 2,
        "0.11": 3,
        "0.10": 4,
        "0.9": 5,
        "0.8": 6,
        "invalid": 7,
        "not available": 8,
        "unknown version": 9
    }

    counterLock.acquire()
    counter[int(counterIdx[apistate])] = counter[int(counterIdx[apistate])] + 1
    counter[int(counterIdx["sum"])] = counter[int(counterIdx["sum"])] + 1
    directory.append({"name": spacename, "apistate": apistate, "url": url})
    counterLock.release()


def loadSpaceAPI(spacename, url, points, directory, counter, counterLock):
    try:
        r = json.loads(requests.get(url=url,timeout=5).text)
    except Exception as e:
        logger.error(spacename + ": " + str(e))
        addToDir(directory,spacename,"not available",url)
        return

    if "api" in r:
        if r["api"] == "0.13":
            try:
                jsonschema.validate(r,schema13)
            except Exception as e:
                logger.error("Invalid: %s" % str(spacename))
                addToDir(directory,spacename,"invalid",url)
                return

            addToDir(directory,spacename,"0.13",url)
            points.append(parser13.parse(spacename,r))

        elif r["api"] == "0.12":
            try:
                jsonschema.validate(r,schema12)
            except Exception as e:
                logger.error("Invalid: %s" % str(spacename))
                addToDir(directory,spacename,"invalid",url)
                return

            addToDir(directory,spacename,"0.12",url)

        elif r["api"] == "0.11":
            try:
                jsonschema.validate(r,schema11)
            except Exception as e:
                logger.error("Invalid: %s" % str(spacename))
                addToDir(directory,spacename,"invalid",url)
                return

            addToDir(directory,spacename,"0.11",url)

        elif r["api"] == "0.10":
            try:
                jsonschema.validate(r, schema9)
            except Exception as e:
                logger.error("Invalid")
                addToDir(directory,spacename,"invalid",url)
                return

            addToDir(directory,spacename,"0.10",url)

        elif r["api"] == "0.9":
            try:
                jsonschema.validate(r,schema9)
            except Exception as e:
                logger.error("Invalid")
                addToDir(directory,spacename,"invalid",url)
                return

            addToDir(directory,spacename,"0.9",url)

        elif r["api"] == "0.8":
            try:
                jsonschema.validate(r,schema8)
            except Exception as e:
                logger.error("Invalid: %s" % str(spacename))
                addToDir(directory,spacename,"invalid",url)
                return

            addToDir(directory,spacename,"0.8",url)
        else:
            logger.error("UNKNOWN VERSION: "+spacename + ": " + str(spacename))
            addToDir(directory,spacename,"unknown version",url)

    else:
        logger.error("Invalid: %s" % str(spacename))
        addToDir(directory,spacename,"invalid",url)


if __name__ == '__main__':


    try:
        logger.info("Downloading directory from fixme.ch...")
        fixmeDirectory = requests.get(url="https://spaceapi.fixme.ch/directory.json", timeout=5).text
        with open("directory.json","w") as f:
            f.write(fixmeDirectory)
            f.close()

        dir = json.loads(fixmeDirectory)
        logger.info("Successfully loaded.")
    except Exception as e:
        logger.warn(e)
        logger.warn("Downloading from fixme.ch failed. Use cached directory.")
        try:
            dir = json.load(open('directory.json',encoding='utf-8'))
            logger.warn("Succesfully loaded cached version.")
        except Exception as e:
            logger.error(e)
            logger.error("Cached directory failed. EXIT!")
            exit(-1)

    manager = Manager()
    points = manager.list()
    directory = manager.list()
    counter = manager.list(range(10))
    processes = []
    counterLock = Lock()

    for i in range(10):
        counter[i] = 0

    counterIdx = {
        "sum": 0,
        "0.13": 1,
        "0.12": 2,
        "0.11": 3,
        "0.10": 4,
        "0.9": 5,
        "0.8": 6,
        "invalid": 7,
        "not available": 8,
        "unknown version": 9
    }

    for spacename in dir:
        p = Process(target=loadSpaceAPI, args=(spacename, dir[spacename], points, directory, counter, counterLock))
        processes.append(p)
        p.start()


    for p in processes:
        p.join()

    logger.info("JOINED")

    general = {
        "measurement": "GeneralInformation",
        "fields": {
            "sum": counter[int(counterIdx["sum"])],
            "0.13": counter[int(counterIdx["0.13"])],
            "0.12": counter[int(counterIdx["0.12"])],
            "0.11": counter[int(counterIdx["0.11"])],
            "0.10": counter[int(counterIdx["0.10"])],
            "0.9": counter[int(counterIdx["0.9"])],
            "0.8": counter[int(counterIdx["0.8"])],
            "invalid": counter[int(counterIdx["invalid"])],
            "not available": counter[int(counterIdx["not available"])],
            "unknown version": counter[int(counterIdx["unknown version"])]
        }
    }

    if USE_EXPORT_DIRECTORY:
        with open('directory_crawled.json', "w", encoding='utf-8') as f:
            d = [ x for x in directory]
            f.write(json.dumps(d))
            f.close()

    if USE_INFLUX:
        logger.info("Write to INFLUX" + str(points))

        points.append(general)

        client.write_points(points)


