#!/bin/python

import os
import logging
import json
import configparser
import requests
import jsonschema

from influxdb import InfluxDBClient
from multiprocessing import Process, Manager





def parse(spacename,r):

    lat = r["location"]["lat"]
    lon = r["location"]["lon"]

    if r["state"]["open"] is True:
        door = 1
    else:
        door = 0

    p = {
        "measurement": spacename,
        "fields": {
            "doorstate": door
        },
        "tags": {
            "lon": lon,
            "lat": lat
        }
    }

    if "sensors" in r:
        if "temperature" in r["sensors"]:
            for temp in r["sensors"]["temperature"]:
                print(temp)
                p["fields"]["temperature/"+temp["location"]+temp["unit"]] = temp["value"]

    print(p)
    return p

