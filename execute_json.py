#!/usr/bin/env python

import argparse
import ConfigParser
import httplib
import json
import time

parser = argparse.ArgumentParser()
parser.add_argument("config")
parser.add_argument("plans", nargs="*", help="query plans ")
args = parser.parse_args()

sleep_time = 1


def execute_jsons(restURL):
    for idx, plan in enumerate(args.plans):
        # submit a query
        print "submitting {}".format(plan)
        headers = {
            "Content-type": "application/JSON",
        }
        with open(plan, "r") as myfile:
            data = myfile.read().replace('\n', '')
        conn = httplib.HTTPConnection(restURL)
        conn.request("POST", "/query", data, headers)
        response = conn.getresponse()

        # raise an exception if something is going wrong
        if response.status != 202:
            raise Exception(" {}, {}, {}".format(response.status,
                            response.reason, response.read()))

        queryStatus = json.load(response)
        if queryStatus['status'] != 'ACCEPTED':
            raise Exception("Error in submitting {}".format(plan))
        queryId = queryStatus['queryId']

        # wait until this query sucess
        while idx < len(args.plans)-1:
            time.sleep(sleep_time)
            conn = httplib.HTTPConnection(restURL)
            conn.request("GET", "/query/query-{}".format(queryId), "", headers)
            res = conn.getresponse()
            queryStatus = json.load(res)
            currentStatus = queryStatus['status']
            if(currentStatus == 'SUCCESS'):
                break
            elif (currentStatus != 'RUNNING'):
                raise Exception(
                    "In submitting {}, error {}".format(plan, currentStatus))


def getRestURL(configFilename):
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read(configFilename)
    master_ip = config.items('master')[0][1].split(':')[0]
    rest_port = config.get('deployment', 'rest_port')
    return "{}:{}".format(master_ip, rest_port)


if __name__ == '__main__':
    print args.plans
    execute_jsons(getRestURL(args.config))
