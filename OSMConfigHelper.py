__version__ = "1.4"
'''
__author__ = "Simon Geigenberger, Lukas Bug"
__copyright__ = "Copyright 2018, Esri Deutschland GmbH"
__license__ = "Apache-2.0"
__version__ = "1.4"
__email__ = "simon@geigenberger.info, lukas.bug@aol.de"
'''

import json
import sys
import requests
from arcgis.geometry import Polygon
import arcgis.geometry


def getbBoxArea(bBox):
    bBox["y0"] = bBox["minLonInit"]
    bBox["y1"] = bBox["maxLonInit"]
    bBox["x0"] = bBox["minLatInit"]
    bBox["x1"] = bBox["maxLatInit"]
    geom = Polygon({"rings":[[(bBox["x0"],bBox["y1"]),(bBox["x0"],bBox["y0"]),(bBox["x1"],bBox["y0"]),(bBox["x1"],bBox["y1"]),(bBox["x0"],bBox["y1"])]],"spatialReference": {"wkid": 4326}})
    return abs(geom.area)


def readConfig(agolConfig):
    dictOSMConfig = {}
        
    # Try to load the OSM keys
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
        
    # Try to load the OSM tags        
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
    
    # Try to open the config file
    try:
        json_data = open("osmconfig.json").read()
    except:
        print("JSON file does not exist.")
        sys.exit()
        
    # Try to load the config file as JSON, validate the JSON syntax
    try:
        data = json.loads(json_data)
    except:
        print("JSON file cannot be read.")
        sys.exit()
        
    # Validates if categories are selected and all selected categories exist as tags.
    try:
        enabledcatlist = []
        i=0
        for cat in data["categories"]:
            if cat['isEnabled'] == 'yes':
                enabledcatlist.append(i)
            i+=1
            for val in cat["categoryValues"]:
                categorieExists = False
                categorieStr = cat["categoryName"] + ":" + val
                if categorieStr in tagList:
                    categorieExists = True
                    break
                if not categorieExists:
                    print(categorieStr + " does not exist.")
                    sys.exit()
        dictOSMConfig["categories"] = data["categories"]
        dictOSMConfig["enabledCategories"] = enabledcatlist
    except Exception as e:
        print(e)
        print("No categories chosen.")
        sys.exit()
    
    # Validates if attributes are selected and all selected attributes exist as keys
    try:
        for cat in data["categories"]:
            attributes = cat["attributeFieldsToExclude"]
            for key in attributes:
                attributeExists = False
                if key in keyList:
                    attributeExists = True
                    break
                if not attributeExists:
                    print(key + " does not exist.")
                    sys.exit()
    except Exception as e:
        print(e)
        print("No attributes chosen.")    
        sys.exit()
    
    # Validates if a bounding box and all required coordinates are selected
    try:
        boundingBox = data["boundingBox"]
    except:
        print("No bounding box chosen.")
        sys.exit()
        
    try:
        minLat = boundingBox["minLatInit"]
        minLat = float(minLat)
        dictOSMConfig["minLat"] = minLat
    except:
        print("No minimum latitude chosen.")
    
    try:
        minLon = boundingBox["minLonInit"]
        minLon = float(minLon)
        dictOSMConfig["minLon"] = minLon
    except:
        print("No minimum longitude chosen.")   
        
    try:
        maxLat = boundingBox["maxLatInit"]
        maxLat = float(maxLat)
        dictOSMConfig["maxLat"] = maxLat
    except:
        print("No maximum latitude chosen.")   
        
    try:
        maxLon = boundingBox["maxLonInit"]
        maxLon = float(maxLon)
        dictOSMConfig["maxLon"] = maxLon
    except:
        print("No maximum longitude chosen.")
      
    # Validates if the coordinates have a correct value and the maximum values are greater than the minimum values.  
    if maxLat > minLat:
        if maxLon > minLon:
            if maxLat < 90 and maxLat > -90:
                if minLat < 90 and minLat > -90:
                    if maxLon < 180 and maxLon > -180:
                        if minLon < 180 and minLon > -180:
                            print("All Coordinates in range.")
                            dictOSMConfig["boundingBox"] = '('+str(dictOSMConfig["minLat"])+','+str(dictOSMConfig["minLon"])+','+str(dictOSMConfig["maxLat"])+','+str(dictOSMConfig["maxLon"])+')'
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


    # Validates if the bounding box extent is not to large for OSM server
    try:
        bBox = {k:float(v) for (k,v) in data["boundingBox"].items()}
        area = getbBoxArea(bBox)
        if area > 1.7:
            raise Exception("Bounding box area to large for OSM server, please select a smaller extent.")
    except Exception as e:
        print(str(e))
        sys.exit()   
    
    # Validates if a value for geometryChosen is selected and the value is in the correct range.
    try:
        for key in data["categories"]:
            geometries = key["geometryType"]
            dictOSMConfig["geometries"] = geometries
    except:
        print("No geometries chosen.")
        sys.exit()
    
    return dictOSMConfig
