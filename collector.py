#!/bin/python

import os
import logging
import json
import configparser
import requests
import jsonschema

from influxdb import InfluxDBClient
from multiprocessing import Process, Manager

DBNAME = "SPACEAPI_STATS"
USE_INFLUX = False
USE_EXPORT_DIRECTORY = True


if USE_INFLUX:
    client = InfluxDBClient("localhost",8086,"root","root",DBNAME)
    client.create_database(DBNAME)
    client.switch_database(DBNAME)

VERSION_MAJOR = 0
VERSION_MINOR = 2
VERSION_PATCH = 0
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





def loadSpaceAPI(spacename,url,points,directory):


    try:
        r = json.loads(requests.get(url=url,timeout=5).text)
    except Exception as e:
        directory.append({"name":spacename,"apistate":"not available","url":url})
        logger.error(spacename + ": " + str(e))
        return

    try:
        if r["api"] == "0.13":
            try:
                jsonschema.validate(r,schema13)
            except Exception as e:
                logger.error("Invalid: %s" % str(spacename))
                directory.append({"name": spacename, "apistate": "invalid", "url": url})
                return

            directory.append({"name":spacename,"apistate":"0.13","url":url})
            if r["state"]["open"] is True:
                door = 1
            else:
                door = 0
            p = {
                "measurement": spacename,
                    "fields": {
                        "doorstate": door
                    }
                }
            print(p)
            points.append(p)

        if r["api"] == "0.12":
            try:
                jsonschema.validate(r,schema12)
            except Exception as e:
                logger.error("Invalid: %s" % str(spacename))
                directory.append({"name": spacename, "apistate": "invalid", "url": url})
                return

            directory.append({"name":spacename,"apistate":"0.12","url":url})
        if r["api"] == "0.11":
            try:
                jsonschema.validate(r,schema11)
            except Exception as e:
                logger.error("Invalid: %s" % str(spacename))
                directory.append({"name": spacename, "apistate": "invalid", "url": url})
                return

            directory.append({"name":spacename,"apistate":"0.11","url":url})
        if r["api"] == "0.10":
            directory.append({"name":spacename,"apistate":"0.10","url":url})
        if r["api"] == "0.9":
            try:
                jsonschema.validate(r,schema9)
            except Exception as e:
                logger.error("Invalid")
                directory.append({"name": spacename, "apistate": "invalid", "url": url})
                return

            directory.append({"name":spacename,"apistate":"0.9","url":url})
        if r["api"] == "0.8":
            try:
                jsonschema.validate(r,schema8)
            except Exception as e:
                logger.error("Invalid: %s" % str(spacename))
                directory.append({"name": spacename, "apistate": "invalid", "url": url})
                return

            directory.append({"name":spacename,"apistate":"0.8","url":url})
    except Exception as e:
        logger.error(spacename + ": " + str(spacename))
        directory.append({"name":spacename,"apistate":"unknown version","url":url})


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
    processes = []

    for spacename in dir:
        p = Process(target=loadSpaceAPI, args=(spacename,dir[spacename],points,directory))
        processes.append(p)
        p.start()


    for p in processes:
        p.join()

    logger.info("JOINED")

    if USE_EXPORT_DIRECTORY:
        with open('directory_crawled.json', "w", encoding='utf-8') as f:
            d = [ x for x in directory]
            f.write(json.dumps(d))
            f.close()

    if USE_INFLUX:
        logger.info("Write to INFLUX" + str(points))
        client.write_points(points)
