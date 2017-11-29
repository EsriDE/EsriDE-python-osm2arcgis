'''
__author__ = "Simon Geigenberger"
__copyright__ = "Copyright 2017, Esri Deutschland GmbH"
__license__ = "Apache-2.0"
__version__ = "1.0"
__email__ = "s.geigenberger@esri.de"

This python module is used to generate a data frame out of OpenStreetMap data. Point and way information can be loaded as point data. For this the user can define
different categories where the data should come from. Also required attributes can be set. The spatial filter for the data is a bounding box defined by the minimum
and maximum latitude and longitude coordinates. The Overpass API is used to load the data as JSON. The Osm API is used to load the nodes by id. The data frames are
built with the pandas module.
'''

import overpass
from osmapi import OsmApi
from arcgis import geometry
import pandas as pd
import DataToAGO
from copy import deepcopy

oApi = OsmApi()

api = overpass.API()
api = overpass.API(timeout=86400)

dictData = []
title = ""

def run(osmConfig, agolConfig):
    """
    Initial function of the module. The functions to load and parse point or way geometries are called. A data frame is built out of the data and is returned. 
    @param categories: dictionary with all categories the data should come from
    @param attributes: list of attributes which should be included in the data frame
    @param minLat: minimum latitude of the bounding box
    @param minLon: minimum longitude of the bounding box 
    @param maxLat: maximum latitude of the bounding box
    @param maxLon: maximum longitude of the bounding box
    @param geometryChosen: 0-->only point geometries, 1-->only way geometries, 2-->both    
    @return: data frame with all data and attributes
    """
    categories = osmConfig["categories"]
    attributes = osmConfig["attributes"]
    minLat = str(osmConfig["minLat"])
    minLon = str(osmConfig["minLon"])
    maxLat = str(osmConfig["maxLat"])
    maxLon = str(osmConfig["maxLon"])
    geometryChosen = osmConfig["geometryChosen"]
    
    agolConfig = agolConfig
    
    if geometryChosen == 0:
        getPoints(categories, attributes, minLat, minLon, maxLat, maxLon, agolConfig)
    elif geometryChosen == 1:
        getWays(categories, attributes, minLat, minLon, maxLat, maxLon, agolConfig)
    else:
        getPoints(categories, attributes, minLat, minLon, maxLat, maxLon, agolConfig)
        getWays(categories, attributes, minLat, minLon, maxLat, maxLon, agolConfig)
    
    df = pd.DataFrame.from_dict(dictData)
    #df.to_csv("nodes_canada.csv")
    return dictData
    
        
def getPoints(categories, attributes, minLat, minLon, maxLat, maxLon, agolConfig):
    """
    Function to load point data that are within the set bounding box. Coordinates, id, category and requested attributes are parsed from the response into a dictionary.
    @param categories: dictionary with all categories the data should come from
    @param attributes: list of attributes which should be included in the data frame
    @param minLat: minimum latitude of the bounding box
    @param minLon: minimum longitude of the bounding box 
    @param maxLat: maximum latitude of the bounding box
    @param maxLon: maximum longitude of the bounding box
    """
    for key_cat in categories:
        for val_cat in categories[key_cat]:
            category = ('"' + key_cat + '"="' + val_cat + '"')
            title = category
            i=0
            response = api.Get('node[' + category + '](' + minLat + ',' + minLon + ',' + maxLat + ',' + maxLon + ')', responseformat="json")
            elements = response["elements"]
            for element in elements:
                dictElement = {}
#                print (element)
                tags = [element["tags"]]
                tags = tags[0]
                for key_att in attributes:
                    val_att = attributes[key_att]
                    if val_att in tags:
                        dictElement[key_att] = tags[val_att]
                id = element["id"]
                id = float(id)
                dictElement["id"] = id
                dictElement["lon"] = element["lon"]
                dictElement["lat"] = element["lat"]
                try:
                    node = oApi.NodeGet(element["id"])
                    if "user" in node.keys():
                        dictElement["user_"] = node["user"]
                    else:
                        dictElement["user_"] = ""
                    if "timestamp" in node.keys():
                        dictElement["timestamp"] = node["timestamp"]
                    else:
                        dictElement["timestamp"] = ""
                except:
                    print("Node for this element not available")
                dictElement["attribute"] = key_cat + "-" + val_cat
                dictData.append(dictElement)

def getWays(categories, attributes, minLat, minLon, maxLat, maxLon, agolConfig):
    """
    Function to load way data that are within the set bounding box. Coordinates, id, category and requested attributes are parsed from the response into a dictionary.
    Also the first point of every way is chosen as geometry.
    @param categories: dictionary with all categories the data should come from
    @param attributes: list of attributes which should be included in the data frame
    @param minLat: minimum latitude of the bounding box
    @param minLon: minimum longitude of the bounding box 
    @param maxLat: maximum latitude of the bounding box
    @param maxLon: maximum longitude of the bounding box
    """
    for key_cat in categories:
        for val_cat in categories[key_cat]:
            category = ('"' + key_cat + '"="' + val_cat + '"')
            title = category+"_ways"
            i=0
            response = api.Get('way[' + category + '](' + minLat + ',' + minLon + ',' + maxLat + ',' + maxLon + ')', responseformat="json")
            elements = response["elements"]
            for element in elements:
                dictElement = {}
                tags = [element["tags"]]
                tags = tags[0]
                for key_att in attributes:
                    val_att = attributes[key_att]
                    if val_att in tags:
                        dictElement[key_att] = tags[val_att]
                id = element["id"]
                id = float(id)
                dictElement["id"] = id
                
                nodes = element["nodes"]
                
                try:
                    node = oApi.NodeGet(nodes[0])
                    if "user" in node.keys():
                        dictElement["user_"] = node["user"]
                    else:
                        dictElement["user_"] = ""
                    if "timestamp" in node.keys():
                        dictElement["timestamp"] = node["timestamp"]
                    else:
                        dictElement["timestamp"] = ""
                        
                    dictElement["lon"] = node["lon"]
                    dictElement["lat"] = node["lat"]
                except:
                    print("Node for this element not available")

                dictElement["attribute"] = key_cat + "-" + val_cat
                dictData.append(dictElement)
