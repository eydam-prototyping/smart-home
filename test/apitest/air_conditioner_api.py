from flask import Blueprint, Response, request
import random
import time
import json
import logging

logger = logging.getLogger("air-conditioner")

bp = Blueprint('ac', __name__, url_prefix='/apitest/ac')

@bp.route("/state", methods=["GET", "OPTIONS", "POST"])
def state():
    """The current state of the air conditioning unit

    GET: Returns a json object with the state of the air conditioning system

    POST: Sets a new state. Allowed keys are: powerState, temperatureSet, mode
    """

    logger.info("State-Method called, Verb: " + request.method)
    
    for header in request.headers:
        logger.debug(f"Header: {header[0]} - {header[1]}")
    
    resp = None

    # GET
    if request.method == "GET":
        resp = Response(json.dumps({
            "powerState":random.choice(["off", "on"]), 
            "temperatureSet":random.randint(2*16,2*28)/2, 
            "temperatureMeas":random.randint(2*16,2*28)/2, 
            "mode": random.choice(["cooling", "heating", "drying", "fan"]), 
            "errorState": "no error", 
            "timestamp": int(time.time())
            }))
        
        resp.headers["Content-Type"] = "application/json"
        
    # POST
    if request.method == "POST":
        req_json = request.get_json()
        for key in req_json.keys():
            if key not in ["powerState", "temperatureSet", "mode"]:
                logger.warning("Got unexpected key: " + key)
                resp = Response("Got unexpected key: " + key, status=400)
                resp.headers["Content-Type"] = "plain/text"

        if resp is None:
            resp = Response(json.dumps({
                "powerState":random.choice(["off", "on"]), 
                "temperatureSet":random.randint(2*16,2*28)/2, 
                "temperatureMeas":random.randint(2*16,2*28)/2, 
                "mode": random.choice(["cooling", "heating", "drying", "fan"]), 
                "errorState": "no error", 
                "timestamp": int(time.time())
                }))
            resp.headers["Content-Type"] = "application/json"
    
    # OPTIONS
    if request.method == "OPTIONS":
        resp = Response()
        resp.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"

    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.status_code = 200
    return resp