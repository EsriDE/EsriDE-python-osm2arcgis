'''
__author__ = "Simon Geigenberger"
__copyright__ = "Copyright 2017, Esri Deutschland GmbH"
__license__ = "Apache-2.0"
__version__ = "1.1"
__email__ = "s.geigenberger@esri.de"

This python module is used to load the data of a data frame an ArcGIS Online or Portal. The ArcGIS Python API is used to achieve this goal. 
At first the connection to the ArcGIS Online or Portal is built by using the URL, user and password. The second step is to build the dictionary that is used to 
publish the Feature Collection.
'''

from _overlapped import NULL
from copy import deepcopy
import datetime
import json
import sys
import math
import numpy as np

from arcgis import geometry
from arcgis.gis import GIS
import requests

import pandas as pd


def run(dictAGOLConfig, data):
    """
    Function to build the connection to the user of the ArcGIS Online or Portal.
    @param portal: URL of the portal where the data is uploaded
    @param user: portal user
    @param password: password of the user
    @param data: data frame with the OSM data
    @param title: title of the Feature Collection
    @param tags: tags of the Feature Collection
    @param description: description of the Feature Collection      
    """
    portal = dictAGOLConfig["portal"]
    user = dictAGOLConfig["user"]
    password = dictAGOLConfig["password"]
    data = data
    title = dictAGOLConfig["title"]
    tags = dictAGOLConfig["tags"]
    description = dictAGOLConfig["description"]
    copyrightText = dictAGOLConfig["copyrightText"]
    maxRecordCount = dictAGOLConfig["maxRecordCount"]
    gis = GIS(portal, user, password)
    updateServiceParam = dictAGOLConfig["updateService"]
    if updateServiceParam == 1:
        featureServiceID = dictAGOLConfig["featureServiceID"]
        updateService(gis, data, featureServiceID, copyrightText, description, maxRecordCount, title)
    else:
        uploadData(gis, data, title, tags, description, copyrightText, maxRecordCount, portal, user, password)
    

def uploadData(gis, data, title, tags, description, copyrightText, maxRecordCount, portal, user, password):
    """
    Function to publish the OSM data on the ArcGIS Online or Portal.
    @param gis: connection to the user in the ArcGIS Online or Portal
    @param data: data frame with the OSM data
    @param title: title of the Feature Collection
    @param tags: tags of the Feature Collection
    @param description: description of the Feature Collection      
    """ 
    element_exists = gis.content.is_service_name_available(service_name=title, service_type='featureService')
    if not element_exists:
        time_now = str(datetime.datetime.now())
        title = title + "_" + time_now
        
    data_frame = pd.DataFrame.from_dict(data)
    
    title_row = data_frame[:0]
    
    data_row = data_frame[0:]
    
    listBigInt = list(data_row.select_dtypes(include=["int64"]).columns)
    #print(listBigInt)
    for field in listBigInt:
        del title_row[field]
        
    fc = gis.content.import_data(title_row)
    
    item_properties_input = {
    "title": title,
    "tags" : tags,
    "description": description,
    "text": json.dumps({"featureCollection": {"layers": [dict(fc.layer)]}}),
    "type": "Feature Collection",
    }

    item = gis.content.add(item_properties_input)
    new_item = item.publish()
    #print("Service with " + str(len(dataForFrame)) + " features published.")
    item.delete()
    
    layer = new_item.layers[0]
    updateFeatureDescription(copyrightText, maxRecordCount, title, description, layer)
    
    #fset = layer.query()
    #template_feature = fset.features[0]
    
    layerURL = layer.url
    
    for field in listBigInt:
        addBigIntField(layerURL, field, portal, user, password)
    
    groups = splitDataFrameIntoSmaller(data_row)
    i=1;
    for sub_df in groups:
        fc_dataAdd = gis.content.import_data(sub_df)
        update_data = getDictUpdate(fc_dataAdd, layer)
        print(str(i)+"000 Features of about "+str((len(groups)))+"000 Features added.")
        i = i+1
    
def updateService(gis, data, featureID, copyrightText, description, maxRecordCount, title):
    existing_service = gis.content.get(featureID)
    service_layer = existing_service.layers[0]
    fset = service_layer.query()
    #service_layer.edit_features(deletes = fset)
    data_frame = pd.DataFrame.from_dict(data)
    data_row = data_frame[0:]
    groups = splitDataFrameIntoSmaller(data_row)
    updateFeatureDescription(copyrightText, maxRecordCount, title, description, service_layer)
    i=1;
    for sub_df in groups:
        fc_dataAdd = gis.content.import_data(sub_df)
        getDictUpdate(fc_dataAdd, service_layer)
        print(str(i)+"000 Features of about "+str((len(groups)))+"000 Features added.")
        i = i+1
    
def getDictUpdate(fc_dataAdd, layer):
    
    listAddFeatures = []
    i = 0
    dataAvailable = True
    dataUploaded = False
    dataQuery = fc_dataAdd.query()
    
    while dataAvailable:
        modulo_i = i % 100
        if modulo_i == 0 and i != 0 and not dataUploaded:
            layer.edit_features(adds = listAddFeatures)
            listAddFeatures.clear()
            dataUploaded = True
            print(str(i)+" Features of "+str(len(dataQuery))+" added.")
        else:
            try:
                listAddFeatures.append(dataQuery.features[i])
                i = i + 1
                dataUploaded = False
            except:
                dataAvailable = False
        
    layer.edit_features(adds = listAddFeatures)
    print("All "+str(len(dataQuery))+" Features added.")
    
def addBigIntField(layerURL, intFieldName, portal, user, password):

    newField = {
                "name" : intFieldName, 
                "type" : "esriFieldTypeInteger",   
                "alias" : intFieldName, 
                "sqlType" : "sqlTypeBigInt", 
                "nullable" : True, 
                "editable" : True,
                "visible" : True
                }
    
    token_URL = "{}/sharing/generateToken".format(portal)
    token_params = {'username' : user,
                    'password' : password,
                    'client' : 'referer',
                    'referer': portal,
                    'expiration': 60,
                    'f' : 'json'}
        
    #print("requesting token with username: {}".format(user))
    r = requests.post(token_URL,token_params)
        
    token_obj = r.json()
        
    token = token_obj['token']
    expires = token_obj['expires']
        
    tokenExpires = datetime.datetime.fromtimestamp(int(expires)/1000)
        
    #print("token for user {}, valid till: {}".format(user, tokenExpires))
        
    featureLayerAdminUrl = layerURL.replace("/rest/", "/rest/admin/")
        
    params = {"f":"json", "token":token}
    params["addToDefinition"] = json.dumps({"fields":[newField]})
        
    #print("Adding field.")
    layerUpdateUrl = "{}/addToDefinition".format(featureLayerAdminUrl)
    layerResult = requests.post(layerUpdateUrl, params)
    #print(layerResult.text)
        
    print("Addding field complete.")
    
def splitDataFrameIntoSmaller(df): 
    listOfDf = list()
    numberChunks = len(df) // 1000 + 1
    for i in range(numberChunks):
        listOfDf.append(df[i*1000:(i+1)*1000])
    return listOfDf

def updateFeatureDescription(copyrightText, maxRecordCount, title, description, layer):
    update_dict = {'copyrightText': copyrightText,
                   'maxRecordCount': maxRecordCount,
                   "name":title,
                   "description": description,
                   "capabilities": 'Create,Editing,Query,Update,Uploads,Delete,Sync,Extract'}
    layer.manager.update_definition(update_dict)
