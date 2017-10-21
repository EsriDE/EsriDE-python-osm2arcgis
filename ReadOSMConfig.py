'''
__author__ = "Simon Geigenberger"
__copyright__ = "Copyright 2017, Esri Deutschland GmbH"
__license__ = "Apache-2.0"
__version__ = "1.0"
__email__ = "s.geigenberger@esri.de"
'''

import json
import sys
import requests
from ctypes.wintypes import DOUBLE

def readOSMConfig():
    dictOSMConfig = {}
    
    #Try to import the overpass module
    try:
        import overpass
    except:
        print("Cannot import Overpass API.")
        sys.exit()
    
    #Try to import the module for the OSM API
    try:
        from osmapi import OsmApi
    except:
        print("Cannot import OSM API.")
        sys.exit()
    
    #Try to import the pandas module
    try:
        import pandas as pd
    except:
        print("Cannot import Pandas module.")
        sys.exit()
        
    #Try to load the OSM keys
    try:
        keys = requests.get("https://taginfo.openstreetmap.org/api/4/projects/keys")
        keys = json.loads(keys.text)
        data = keys["data"]
        keyList = []
        for element in data:
            keyList.append(element["key"])
    except:
        print("Cannot load OSM key list.")
        sys.exit()
        
    #Try to load the OSM tags        
    try:
        tags = requests.get("https://taginfo.openstreetmap.org/api/4/projects/tags")
        tags = json.loads(tags.text)
        data = tags["data"]
        tagList = []
        for element in data:
            tagString = element["key"] + ":" + element["value"]
            tagList.append(tagString)
    except:
        print("Cannot load OSM tag list.")
        sys.exit()
    
    #Try to open the config file
    try:
        json_data = open("osmconfig.json").read()
    except:
        print("JSON file does not exist.")
        sys.exit()
        
    #Try to load the config file as JSON, validate the JSON syntax
    try:
        data = json.loads(json_data)
    except:
        print("JSON file cannot be red.")
        sys.exit()
        
    #Validates if categories are selected and all selected categories exist as tags.
    try:
        categories = data["categories"]
        for key in categories:
            for val in categories[key]:
                categorieExists = False
                categorieStr = key + ":" + val
                for tag in tagList:
                    if categorieStr == tag:
                        categorieExists = True
                        break
                if not categorieExists:
                    print(categorieStr + " does not exist.")
                    sys.exit()
        dictOSMConfig["categories"]=categories
    except:
        print("No categories chosen.")
        sys.exit()
    
    #Validates if attributes are selected and all selected attributes exist as keys
    try:
        attributes = data["attributes"]
        for key in attributes:
            attributeExists = False
            for keyL in keyList:
                if attributes[key] == keyL:
                    attributeExists = True
                    break
            if not attributeExists:
                print(attributes[key] + " does not exist.")
                sys.exit()
        dictOSMConfig["attributes"]=attributes
    except:
        print("No attributes chosen.")    
        sys.exit()
    
    #Validates if a bounding box and all required coordinates are selected
    try:
        boundingBox = data["boundingBox"]
    except:
        print("No bounding box chosen.")
        sys.exit()
        
    try:
        minLat = boundingBox["minLatInit"]
        minLat = float(minLat)
        dictOSMConfig["minLat"]=minLat
    except:
        print("No minimum latitude chosen.")
    
    try:
        minLon = boundingBox["minLonInit"]
        minLon = float(minLon)
        dictOSMConfig["minLon"]=minLon
    except:
        print("No minimum longitude chosen.")   
        
    try:
        maxLat = boundingBox["maxLatInit"]
        maxLat = float(maxLat)
        dictOSMConfig["maxLat"]=maxLat
    except:
        print("No maximum latitude chosen.")   
        
    try:
        maxLon = boundingBox["maxLonInit"]
        maxLon = float(maxLon)
        dictOSMConfig["maxLon"]=maxLon
    except:
        print("No maximum longitude chosen.")
      
    #Validates if the coordinates have a correct value and the maximum values are greater than the minimum values.  
    if maxLat>minLat:
        if maxLon>minLon:
            if maxLat < 90 or maxLat > -90:
                if minLat < 90 or minLat > -90:
                    if maxLon < 180 or maxLon > -180:
                        if minLon < 180 or minLon > -180:
                            print("All Coordinates in range.")
                        else:
                            print("Minimum longitude is out of range.")
                    else:
                        print("Maximum longitude is out of range.")
                else:
                    print("Minimum latitude is out of range.")
            else:
                print("Maximum latitude is out of range.")
        else:
            print("Maximum longitude is not greater than minimum longitude.")
    else:
        print("Maximum latitude is not greater than minimum latitude.")       
    
    #Validates if a value for geometryChosen is selected and the value is in the correct range.
    try:
        geometryChosen = data["geometryChosen"]
        if geometryChosen<0 or geometryChosen>2:
            print("Value for geometryChosen is out of range.")
            sys.exit()
        dictOSMConfig["geometryChosen"]=geometryChosen
    except:
        print("No geometrytype chosen.")
        sys.exit()
    
    return dictOSMConfig