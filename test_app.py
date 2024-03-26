import unittest
from app import app
from app import get_top_specialists,get_coord
import pytest
#from . import __version__ as _werkzeug_version
from flask import Flask,request
from flask import json
from werkzeug.test import Client
from werkzeug.testapp import test_app as te



def test_index():
    
    response = app.test_client().get("/")
    assert b"Website is working! Now go test the endpoint." in response.data


def test_get_top_specialists():

    response = app.test_client().get("/top_specialists")
    print(response)
    assert response.status_code == 400
    response = app.test_client().get("/top_specialists?address='1600 Amphitheatre Parkway, Mountain View, CA 94043'")
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data["Closest Match"] == "This is the address used: Google Headquarters, 1600, Amphitheatre Parkway, Mountain View, Santa Clara County, California, 94043, United States. If it is incorrect, please provide a more exact address."
    assert response_data["top_specialists"]["0"]["1811475528"]["Coordinates"]["longitude"] == -121.9202344     


def test_get_geo_distance():
    
    return

def test_get_coord():
    coords = get_coord("350 5th Ave, New York, NY")
    assert coords is not None
    assert type(coords['latitude']) == float
    coords = get_coord("America Nueve Yorka")
    assert coords is None