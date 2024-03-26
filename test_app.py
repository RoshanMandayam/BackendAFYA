import unittest
from app import app
from app import get_top_specialists,get_coord,get_geo_distance
import pytest
#from . import __version__ as _werkzeug_version
from flask import Flask,request
from flask import json
from werkzeug.test import Client
from werkzeug.testapp import test_app as te


#check if main page works
def test_index():
    
    response = app.test_client().get("/")
    assert b"Website is working! Now go test the endpoint." in response.data

#testing ability to get the specialists
def test_get_top_specialists():

    response = app.test_client().get("/top_specialists")
    print(response)
    assert response.status_code == 400
    response = app.test_client().get("/top_specialists?address='1600 Amphitheatre Parkway, Mountain View, CA 94043'")
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data["Closest Match"] == "This is the address used: Google Headquarters, 1600, Amphitheatre Parkway, Mountain View, Santa Clara County, California, 94043, United States. If it is incorrect, please provide a more exact address."
    assert response_data["top_specialists"]["0"]["1811475528"]["Coordinates"]["longitude"] == -121.9202344     

#testing the ability to calculate distances
def test_get_geo_distance():
    loc1lat = None
    loc1long = 30
    loc2lat = 30
    loc2long = 67
    response = get_geo_distance(loc1lat,loc1long,loc2lat,loc2long)
    assert response is None
    loc1lat = 30
    loc1long = 30
    loc2lat = None
    loc2long = 67
    response = get_geo_distance(loc1lat,loc1long,loc2lat,loc2long)
    assert response is None
    loc1lat = 33
    loc1long = 30
    loc2lat = 44
    loc2long = 67
    response = get_geo_distance(loc1lat,loc1long,loc2lat,loc2long)
    assert response > 3300 and response < 3500


#testing ability to get specifc lat and long from string addresses
def test_get_coord():
    coords = get_coord("350 5th Ave, New York, NY")
    assert coords is not None
    assert type(coords['latitude']) == float
    coords = get_coord("America Nueve Yorka")
    assert coords is None