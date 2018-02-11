'''
__author__ = "Simon Geigenberger"
__copyright__ = "Copyright 2018, Esri Deutschland GmbH"
__license__ = "Apache-2.0"
__version__ = "1.3"
__email__ = "s.geigenberger@esri.de"

This python module is used to generate a data frame out of OpenStreetMap data. Point and way information can be loaded as point data. For this the user can define
different categories where the data should come from. Also required attributes can be set. The spatial filter for the data is a bounding box defined by the minimum
and maximum latitude and longitude coordinates. The Overpass API is used to load the data as JSON. The Osm API is used to load the nodes by id. The data frames are
built with the pandas module.
'''

import overpass
from osmapi import OsmApi
from arcgis import features as fs
import arcgis
import pandas as pd
import DataConvertionHelper

oApi = OsmApi()

api = overpass.API()
api = overpass.API(timeout=86400)

title = ""

listOSMData = []

listPolygons = []

def run(osmConfig):
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
    categoriesPoint = osmConfig["geometries"]["point"]
    categoriesLine = osmConfig["geometries"]["line"]
    categoriesPolygon = osmConfig["geometries"]["polygon"]
    categoriesLineAndPolygon = osmConfig["geometries"]["lineAndPolygon"]
    categories = osmConfig["categories"]
    minLat = str(osmConfig["minLat"])
    minLon = str(osmConfig["minLon"])
    maxLat = str(osmConfig["maxLat"])
    maxLon = str(osmConfig["maxLon"])
            

    getPoints(categories, categoriesPoint, osmConfig, minLat, minLon, maxLat, maxLon)
    getRelations(categories, categoriesLineAndPolygon, osmConfig, minLat, minLon, maxLat, maxLon)
    getRelations(categories, categoriesPolygon, osmConfig, minLat, minLon, maxLat, maxLon)
    getWays(categories, categoriesLineAndPolygon, osmConfig, minLat, minLon, maxLat, maxLon, True, True)
    getWays(categories, categoriesLine, osmConfig, minLat, minLon, maxLat, maxLon, True, False)
    getWays(categories, categoriesPolygon, osmConfig, minLat, minLon, maxLat, maxLon, False, True)
    
    return listOSMData
    
        
def getPoints(categories, categoriesGeometry, osmConfig, minLat, minLon, maxLat, maxLon):
    """
    Function to load point data that are within the set bounding box. Coordinates, id, category and requested attributes are parsed from the response into a dictionary.
    @param categories: dictionary with all categories the data should come from
    @param attributes: list of attributes which should be included in the data frame
    @param minLat: minimum latitude of the bounding box
    @param minLon: minimum longitude of the bounding box 
    @param maxLat: maximum latitude of the bounding box
    @param maxLon: maximum longitude of the bounding box
    """
    for keyCategory in categoriesGeometry:
        dictData = []
        listGeometries = []
        attributes = osmConfig["attributes_"+keyCategory]
        for valCategory in categories[keyCategory]:
            category = ('"' + keyCategory + '"="' + valCategory + '"')
            title = category
            i=0
            response = api.Get('node[' + category + '](' + minLat + ',' + minLon + ',' 
                               + maxLat + ',' + maxLon + ')', responseformat="json")
            elements = response["elements"]
            for element in elements:
                dictElement = {}
#                print (element)
                tags = [element["tags"]]
                tags = tags[0]
                for keyAttribute in attributes:
                    valAttribute = attributes[keyAttribute]
                    if valAttribute in tags:
                        dictElement[keyAttribute] = tags[valAttribute]
                    else:
                        dictElement[keyAttribute] = ""
                id = element["id"]
                #id = float(id)
                dictElement["osm_id"] = id
                if "user" in attributes or "timestamp" in attributes:
                    try:
                        node = oApi.NodeGet(element["id"])
                        if "user" in attributes:
                            if "user" in node.keys():
                                dictElement["user_"] = node["user"]
                        if "timestamp" in attributes:
                            if "timestamp" in node.keys():
                                dictElement["timestamp"] = node["timestamp"]
                    except:
                        print("Node for this element not available")
                dictElement["category"] = keyCategory + "-" + valCategory
                lon = element["lon"]
                lat = element["lat"]
                geometryPoint = DataConvertionHelper.getPoint(lon, lat)
                listGeometries.append(geometryPoint)
                dictData.append(dictElement)
                    
        dataFrameTotal = pd.DataFrame.from_dict(dictData)

        listReturn = []
        listReturn.append(dataFrameTotal)
        listReturn.append(listGeometries)
        
        if len(listGeometries) > 0:
            listOSMData.append(listReturn)

def getWays(categories, categoriesGeometry, osmConfig, minLat, minLon, maxLat, maxLon, lines, polygons):
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
    for keyCategory in categoriesGeometry:
        dictDataPolygon = []
        dictDataPolyline = []
        listGeometriesPolygon = []
        listGeometriesPolyline = []
        attributes = osmConfig["attributes_"+keyCategory]
        for valCategory in categories[keyCategory]:
            category = ('"' + keyCategory + '"="' + valCategory + '"')
            title = category+"_ways"
            i=0
            response = api.Get('way[' + category + '](' + minLat + ',' + minLon + ',' + maxLat + ',' + maxLon + ')', responseformat="json")
            elements = response["elements"]
            for element in elements:
                dictElement = {}
                tags = [element["tags"]]
                tags = tags[0]
                for keyAttribute in attributes:
                    valAttribute = attributes[keyAttribute]
                    if valAttribute in tags:
                        dictElement[keyAttribute] = tags[valAttribute]
                    else:
                        dictElement[keyAttribute] = ""
                id = element["id"]
                inList = False
                if id in listPolygons:
                    inList = True
                
                if inList:
                    dictElement["osm_id"] = id
                    dictElement["category"] = keyCategory + "-" + valCategory
                    nodes = element["nodes"]
                    
                    listRings = []
                    listRing = []
                    
                    timestamp = True
                    user = True
                    for nodeID in nodes:
                        coordinateTuple = []
                        try:
                            node = oApi.NodeGet(nodeID)
                            if "user" in attributes and user:
                                if "user" in node.keys():
                                    dictElement["user_"] = node["user"]
                                    user = False
                            if "timestamp" in attributes and timestamp:
                                if "timestamp" in node.keys():
                                    dictElement["timestamp"] = node["timestamp"]
                                    timestamp = False
                            coordinateTuple.append(node["lon"])
                            coordinateTuple.append(node["lat"])
                            listRing.append(coordinateTuple)
                        except:
                            print("Node for this element not available")
                    
                    listRings.append(listRing)
                    timestamp = True
                    user = True
                    
                    if polygons:
                        geometryPolygonLine = DataConvertionHelper.getLinePolygon(listRings)
                        
                        if "rings" in geometryPolygonLine:
                            listGeometriesPolygon.append(geometryPolygonLine)
                            dictDataPolygon.append(dictElement)
                            
                        if lines:
                            if "paths" in geometryPolygonLine:
                                    listGeometriesPolyline.append(geometryPolygonLine)
                                    dictDataPolyline.append(dictElement)
                                    
                    elif lines:
                        geometryLines = DataConvertionHelper.getLine(listRings)
                        listGeometriesPolyline.append(geometryLines)
                        dictDataPolyline.append(dictElement)
        
        dataFramePolygon = pd.DataFrame.from_dict(dictDataPolygon)
        dataFramePolyline = pd.DataFrame.from_dict(dictDataPolyline)
    
        listPolygonReturn = []
        listPolygonReturn.append(dataFramePolygon)
        listPolygonReturn.append(listGeometriesPolygon)
        
        listPolylineReturn = []
        listPolylineReturn.append(dataFramePolyline)
        listPolylineReturn.append(listGeometriesPolyline)
        
        if len(listGeometriesPolygon) > 0:
            listOSMData.append(listPolygonReturn)
        
        if len(listGeometriesPolyline) > 0:
            listOSMData.append(listPolylineReturn)
    
def getRelations(categories, categoriesGeometry, osmConfig, minLat, minLon, maxLat, maxLon):
    for keyCategory in categoriesGeometry:
        attributes = osmConfig["attributes_"+keyCategory]
        listData = []
        listGeometries = []
        for valCategory in categories[keyCategory]:
            category = ('"' + keyCategory + '"="' + valCategory + '"')
            title = category+"_ways"
            i=0
            response = api.Get('relation[' + category + '](' + minLat + ',' + minLon + ',' + maxLat + ',' + maxLon + ')', responseformat="json")
            elements = response["elements"]
            for element in elements:
                dictElement = {}
                tags = [element["tags"]]
                tags = tags[0]
                for keyAttribute in attributes:
                    valAttribute = attributes[keyAttribute]
                    if valAttribute in tags:
                        dictElement[keyAttribute] = tags[valAttribute]
                    else:
                        dictElement[keyAttribute] = ""
                id = element["id"]
                dictElement["osm_id"] = id
                dictElement["category"] = keyCategory + "-" + valCategory
                    
                relation = element["members"]
                listRings = []
                timestampAndUser = True
                for subelement in relation:
                    listNodes = []
                    id = subelement["ref"]
                    if subelement["role"] == "inner" or subelement["role"] == "outer":
                        listPolygons.append(id)
                        way = oApi.WayGet(id)
                        for node in way["nd"]:
                            coordinateTuple = []
                            wayPoint = oApi.NodeGet(node)
                            coordinateTuple.append(wayPoint["lon"])
                            coordinateTuple.append(wayPoint["lat"])
                            listNodes.append(coordinateTuple)
                            if timestampAndUser:
                                if "user" in attributes:
                                    if "user" in node.keys():
                                        dictElement["user_"] = wayPoint["user"]
                                if "timestamp" in attributes:
                                    if "timestamp" in node.keys():
                                        dictElement["timestamp"] = wayPoint["timestamp"]
                                timestampAndUser = False
                    
                        if subelement["role"] == "inner":
                            listNodes.reverse()
                            
                        listRings.append(listNodes)
                        
                geometry = DataConvertionHelper.getLinePolygon(listRings)
                        
                listGeometries.append(geometry)
                listData.append(dictElement)
                timestampAndUser = True
    
        dataFrameReturn = pd.DataFrame.from_dict(listData)
        if len(listGeometries) > 0:
            listReturn = []
            listReturn.append(dataFrameReturn)
            listReturn.append(listGeometries)
            listOSMData.append(listReturn)