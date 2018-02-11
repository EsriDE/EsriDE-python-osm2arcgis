'''
__author__ = "Simon Geigenberger"
__copyright__ = "Copyright 2018, Esri Deutschland GmbH"
__license__ = "Apache-2.0"
__version__ = "1.3"
__email__ = "s.geigenberger@esri.de"

This python module is used to load the data of a data frame an ArcGIS Online or Portal. The ArcGIS Python API is used to achieve this goal. 
At first the connection to the ArcGIS Online or Portal is built by using the URL, user and password. The second step is to build the dictionary that is used to 
publish the Feature Collection.
'''

import datetime
import json
import sys
import DataConvertionHelper

from arcgis.gis import GIS
import requests

def run(dictAGOLConfig, listData):
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
    title = dictAGOLConfig["title"]
    tags = dictAGOLConfig["tags"]
    description = dictAGOLConfig["description"]
    copyrightText = dictAGOLConfig["copyrightText"]
    maxRecordCount = dictAGOLConfig["maxRecordCount"]
    gis = GIS(portal, user, password)
    overwriteServiceParam = dictAGOLConfig["overwriteService"]
    spatialDataFrameTotal = DataConvertionHelper.getEsriSpatialDataFrame(listData)
    listOneFeature = []
    listOneFeature.append(listData[0][:1])
    listOneFeature.append(listData[1][:1])
    spatialDataFrameOneFeature = DataConvertionHelper.getEsriSpatialDataFrame(listOneFeature)
    if overwriteServiceParam == 1:
        featureServiceID = dictAGOLConfig["featureServiceID"]
        overwriteFeatureService(gis, spatialDataFrameTotal, featureServiceID, copyrightText, description, maxRecordCount, title, tags)
    else:
        uploadData(gis, spatialDataFrameOneFeature, spatialDataFrameTotal, title, tags, description, copyrightText, maxRecordCount, portal, user, password)
    

def uploadData(gis, spatialDataFrameOneFeature, spatialDataFrameTotal, title, tags, description, copyrightText, maxRecordCount, portal, user, password):
    """
    Function to publish the OSM data on the ArcGIS Online or Portal.
    @param gis: connection to the user in the ArcGIS Online or Portal
    @param data: data frame with the OSM data
    @param title: title of the Feature Collection
    @param tags: tags of the Feature Collection
    @param description: description of the Feature Collection      
    """ 
    elementExists = gis.content.is_service_name_available(service_name=title, service_type='featureService')
    if elementExists:
        timeNow = str(datetime.datetime.now())
        title = title + "_" + timeNow
    
    
    
    listBigInt = list(spatialDataFrameOneFeature.select_dtypes(include=["int64"]).columns)

    for field in listBigInt:
        del spatialDataFrameOneFeature[field]
        
    spatialDataFrameLayer = spatialDataFrameOneFeature.to_featurelayer(title)
    
    layer = spatialDataFrameLayer.layers[0]
    
    layer.edit_features(deletes = layer.query())

    updateFeatureDescription(copyrightText, maxRecordCount, title, description, layer, tags)
    
    layerURL = layer.url
    
    for field in listBigInt:
        addBigIntField(layerURL, field, portal, user, password)
    
    spatialDataFrameGroups = splitdataframeTotalIntoSmaller(spatialDataFrameTotal)
    i=1;
    for spatialDataFrameSub in spatialDataFrameGroups:
        featureSet = spatialDataFrameSub.to_featureset()
        layer.edit_features(adds = featureSet)
        progress(i, len(spatialDataFrameGroups))
        i = i+1
    
def overwriteFeatureService(gis, spatialDataFrameTotal, featureID, copyrightText, description, maxRecordCount, title, tags):
    featureServiceExisting = gis.content.get(featureID)
    serviceLayer = featureServiceExisting.layers[0]
    featureSet = serviceLayer.query()
    serviceLayer.edit_features(deletes = featureSet)
    updateFeatureDescription(copyrightText, maxRecordCount, title, description, serviceLayer, tags)
    spatialDataFrameGroups = splitdataframeTotalIntoSmaller(spatialDataFrameTotal)
    i=1;
    for spatialDataFrameSub in spatialDataFrameGroups:
        featureSet = spatialDataFrameSub.to_featureset()
        serviceLayer.edit_features(adds = featureSet)
        progress(i, len(spatialDataFrameGroups))
        i = i+1
    
def addDataToFeatureService(featureClassAddData, layer):
    
    listAddFeatures = []
    i = 0
    dataAvailable = True
    dataUploaded = False
    dataQuery = featureClassAddData.query()
    
    while dataAvailable:
        moduloI = i % 100
        if moduloI == 0 and i != 0 and not dataUploaded:
            layer.edit_features(adds = listAddFeatures)
            listAddFeatures.clear()
            dataUploaded = True
        else:
            try:
                listAddFeatures.append(dataQuery.features[i])
                i = i + 1
                dataUploaded = False
            except:
                dataAvailable = False
        
    layer.edit_features(adds = listAddFeatures)
    
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
    
    tokenURL = "{}/sharing/generateToken".format(portal)
    tokenParams = {'username' : user,
                    'password' : password,
                    'client' : 'referer',
                    'referer': portal,
                    'expiration': 60,
                    'f' : 'json'}
        
    r = requests.post(tokenURL,tokenParams)
        
    tokenObj = r.json()
        
    token = tokenObj['token']
    expires = tokenObj['expires']
        
    tokenExpires = datetime.datetime.fromtimestamp(int(expires)/1000)
                
    featureLayerAdminUrl = layerURL.replace("/rest/", "/rest/admin/")
        
    params = {"f":"json", "token":token}
    params["addToDefinition"] = json.dumps({"fields":[newField]})
        
    layerUpdateUrl = "{}/addToDefinition".format(featureLayerAdminUrl)
    layerResult = requests.post(layerUpdateUrl, params)
        
            
def splitdataframeTotalIntoSmaller(dataFrame): 
    dataFrameList = list()
    numberChunks = len(dataFrame) // 1000 + 1
    for i in range(numberChunks):
        dataFrameList.append(dataFrame[i*1000:(i+1)*1000])
    return dataFrameList

def updateFeatureDescription(copyrightText, maxRecordCount, title, description, layer, tags):
    dictUpdate = {'copyrightText': copyrightText,
                   'maxRecordCount': maxRecordCount,
                   "tags" : tags,
                   "name":title,
                   "description": description,
                   "capabilities": 'Create,Editing,Query,Update,Uploads,Delete,Sync,Extract'}
    layer.manager.update_definition(dictUpdate)

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()