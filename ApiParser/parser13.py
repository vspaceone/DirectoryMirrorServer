#!/bin/python


def getName(t, i):
    if "location" in i:
        t = t + "_"
        t = t + i["location"]
    if "name" in i:
        t = t + "_"
        t = t + i["name"]
    if "unit" in i:
        t = t + "_"
        t = t + i["unit"]
    return t



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
            for i in r["sensors"]["temperature"]:
                p["fields"][getName("temperature",i)] = float(i["value"])

    if "sensors" in r:
        if "humidity" in r["sensors"]:
            for i in r["sensors"]["humidity"]:
                p["fields"][getName("humidity",i)] = float(i["value"])

    if "sensors" in r:
        if "barometer" in r["sensors"]:
            for i in r["sensors"]["barometer"]:
                p["fields"][getName("barometer",i)] = float(i["value"])

    if "sensors" in r:
        if "beverage_supply" in r["sensors"]:
            for i in r["sensors"]["beverage_supply"]:
                p["fields"][getName("beverage_supply",i)] = float(i["value"])

    if "sensors" in r:
        if "power_comsumption" in r["sensors"]:
            for i in r["sensors"]["power_comsumption"]:
                p["fields"][getName("power_comsumption",i)] = float(i["value"])

    if "sensors" in r:
        if "wind" in r["sensors"]:

            for i in r["sensors"]["wind"]:
                if "properties" in i:
                    if "speed" in i["properties"]:
                        if "unit" in i["properties"]["speed"] and "value" in i["properties"]["speed"]:
                            p["fields"][getName("wind_speed",i) + i["properties"]["speed"]["unit"]] = float(i["properties"]["speed"]["value"])
                        elif "value" in i["properties"]["speed"]:
                            p["fields"][getName("wind_speed",i)] = float(i["properties"]["speed"]["value"])
                        else:
                            pass
                    if "gust" in i["properties"]:
                        if "unit" in i["properties"]["gust"] and "value" in i["properties"]["gust"]:
                            p["fields"][getName("wind_gust",i) + i["properties"]["gust"]["unit"]] = float(i["properties"]["gust"]["value"])
                        elif "value" in i["properties"]["gust"]:
                            p["fields"][getName("wind_gust",i)] = float(i["properties"]["gust"]["value"])
                        else:
                            pass
                    if "direction" in i["properties"]:
                        if "unit" in i["properties"]["direction"] and "value" in i["properties"]["direction"]:
                            p["fields"][getName("wind_direction",i) + i["properties"]["direction"]["unit"]] = float(i["properties"]["direction"]["value"])
                        elif "value" in i["properties"]["direction"]:
                            p["fields"][getName("wind_direction",i)] = float(i["properties"]["direction"]["value"])
                        else:
                            pass
                    if "elevation" in i["properties"]:
                        if "unit" in i["properties"]["elevation"] and "value" in i["properties"]["elevation"]:
                            p["fields"][getName("wind_elevation",i) + i["properties"]["elevation"]["unit"]] = float(i["properties"]["elevation"]["value"])
                        elif "value" in i["properties"]["elevation"]:
                            p["fields"][getName("wind_elevation",i)] = float(i["properties"]["elevation"]["value"])
                        else:
                            pass

    if "sensors" in r:
        if "network_connections" in r["sensors"]:
            for i in r["sensors"]["network_connections"]:
                p["fields"][getName("network_connections",i)] = float(i["value"])

    if "sensors" in r:
        if "account_balance" in r["sensors"]:
            for i in r["sensors"]["account_balance"]:
                p["fields"][getName("account_balance",i)] = float(i["value"])

    if "sensors" in r:
        if "total_member_count" in r["sensors"]:
            for i in r["sensors"]["total_member_count"]:
                p["fields"][getName("total_member_count",i)] = float(i["value"])

    if "sensors" in r:
        if "people_now_present" in r["sensors"]:
            for i in r["sensors"]["people_now_present"]:
                p["fields"][getName("people_now_present",i)] = float(i["value"])

    if "sensors" in r:
        if "radiation" in r["sensors"]:
            print("RADIATION" + spacename)
            if "alpha" in r["sensors"]["radiation"]:
                for i in r["sensors"]["radiation"]["alpha"]:
                    p["fields"][getName("radiation_alpha",i)] = float(i["value"])
            if "beta" in r["sensors"]["radiation"]:
                for i in r["sensors"]["radiation"]["beta"]:
                    p["fields"][getName("radiation_beta",i)] = float(i["value"])
            if "gamma" in r["sensors"]["radiation"]:
                for i in r["sensors"]["radiation"]["gamma"]:
                    p["fields"][getName("radiation_gamma",i)] = float(i["value"])
            if "beta_gamma" in r["sensors"]["radiation"]:
                for i in r["sensors"]["radiation"]["beta_gamma"]:
                    p["fields"][getName("radiation_beta_gamma",i)] = float(i["value"])

    print(p)
    return p

