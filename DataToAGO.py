'''
__author__ = "Simon Geigenberger"
__copyright__ = "Copyright 2017, Esri Deutschland GmbH"
__license__ = "Apache-2.0"
__version__ = "1.0"
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
        updateService(gis, data, featureServiceID)
    else:
        uploadData(gis, data, title, tags, description, copyrightText, maxRecordCount)
    

def uploadData(gis, data, title, tags, description, copyrightText, maxRecordCount):
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
        title = title + "_1"
        
    dataForFrame = data[:999]
    dataAdd = data[998:]
    
    data_frame = pd.DataFrame.from_dict(dataForFrame)
    fc = gis.content.import_data(data_frame)
    item_properties_input = {
    "title": title,
    "tags" : tags,
    "description": description,
    "text": json.dumps({"featureCollection": {"layers": [dict(fc.layer)]}}),
    "type": "Feature Collection",
    }

    item = gis.content.add(item_properties_input)
    new_item = item.publish()
    print("Service with " + str(len(dataForFrame)) + " features published.")
    item.delete()
    
    layer = new_item.layers[0]
    update_dict = {'copyrightText': copyrightText,
                   'maxRecordCount': maxRecordCount,
                   "name":title,
                   "description": description,
                   "capabilities": 'Create,Editing,Query,Update,Uploads,Delete,Sync,Extract'}
    layer.manager.update_definition(update_dict)
    
    fset = layer.query()
    template_feature = fset.features[0]
    
    update_data = getDictUpdate(gis, dataAdd, template_feature, layer)
    
def updateService(gis, data, featureID):
    existing_service = gis.content.get(featureID)
    service_layer = existing_service.layers[0]
    fset = service_layer.query()
    template_feature = fset.features[0]
    service_layer.edit_features(deletes = fset)
    getDictUpdate(gis, data, template_feature, service_layer)
     
def getDictUpdate(gis, data, template_feature, layer):
    for key in template_feature.attributes.keys():
        template_feature.attributes[key] = None
        
    del template_feature.attributes["FID"]
    
    counterData = 1
    listFeaturesAdd = []
    for feature in data:
        new_feature = deepcopy(template_feature)
        
        input_geometry = {'y':feature['lat'],
                       'x':feature['lon']}
        output_geometry = geometry.project(geometries=[input_geometry], in_sr=4326,
                                           out_sr=3857, gis=gis)
        
        new_feature.geometry = output_geometry[0]
        
        for key in feature.keys():
            new_feature.attributes[key] = feature[key]
        
        layer.edit_features(adds = [new_feature])
        listFeaturesAdd.append(new_feature)
        print(str(counterData) + " of " + str(len(data)) + " features added.")
        counterData = counterData + 1
    
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
    #token_params = {'username':user,'password': password,'referer': portal,'f':'json','expiration':60}
    token_params = {'username' : user,
                    'password' : password,
                    'client' : 'referer',
                    'referer': portal,
                    'expiration': 60,
                    'f' : 'json'}
        
    print("requesting token with username: {}".format(user))
    r = requests.post(token_URL,token_params)
    
    print(r.text)
        
    token_obj = r.json()
        
    token = token_obj['token']
    expires = token_obj['expires']
        
    tokenExpires = datetime.datetime.fromtimestamp(int(expires)/1000)
        
    print("token for user {}, valid till: {}".format(user, tokenExpires))
        
    featureLayerAdminUrl = layerURL.replace("/rest/", "/rest/admin/")
        
    params = {"f":"json", "token":token}
    params["addToDefinition"] = json.dumps({"fields":[newField]})
        
    print("Adding field.")
    layerUpdateUrl = "{}/addToDefinition".format(featureLayerAdminUrl)
    layerResult = requests.post(layerUpdateUrl, params)
    print(layerResult.text)
        
    print("Addding field complete.")
