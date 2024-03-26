import unittest
from app import app
from app import get_top_specialists
import pytest
#from . import __version__ as _werkzeug_version
from flask import Flask,request
from flask import json
from werkzeug.test import Client
from werkzeug.testapp import test_app as te



def test_index():
    
    response = app.test_client().get("/")
    assert b"Website is working! Now go test the endpoint." in response.data


def test_genLocations():
    # response = app.test_client().get("/genLocations")
    # assert response.status_code == 200
    # assert "Location 2:" in response.json["Location 2 Text"] 
    return


def test_submitGuess():
    #response = app.test_client().post("/submitGuess", data={
    #     "guess": "643",
    #})
    #assert result.status_code == 200                                
    #assert response.status_code == 500
    return