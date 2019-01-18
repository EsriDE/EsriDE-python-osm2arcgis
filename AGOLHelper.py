__version__ = "1.4"
'''
__author__ = "Simon Geigenberger, Lukas Bug"
__copyright__ = "Copyright 2018, Esri Deutschland GmbH"
__license__ = "Apache-2.0"
__version__ = "1.4"
__email__ = "simon@geigenberger.info, lukas.bug@aol.de"

This python module is used to load the data of a data frame an ArcGIS Online or Portal. The ArcGIS Python API is used to achieve this goal. 
At first the connection to the ArcGIS Online or Portal is built by using the URL, user and password. The second step is to build the dictionary that is used to 
publish the Feature Collection.
'''

import datetime
from arcgis import features as fs
from arcgis.gis import GIS
import progressbar
p = 0
t_resultlist = []
t_list = []

def prepareLayerUpload(ftLC, featSetList, i):
    '''
    Function to prepare upload to ArcGIS Online or another Portal and to react on upload errors.
    @param ftLC: Contains the layer item on the portal, where the new feature data is stored.
    @param featSetList: Contains the new features, which are stored in the layer.
    @param i: Contains the layer number.
    '''
    status = addFeaturesToLayer(ftLC.layers[i],featSetList[i])
    successlist = [elem['success'] for elem in status]
    if 'False' not in successlist:
        print('All Items in layer '+ftLC.layers[i].properties.name+' uploaded sucessfully')
    else:
        print('There was an error uploading items in layer '+ftLC.layers[i].properties.name)
        raise ValueError("Upload error to portal")      

def createpbar(total):
    '''
    Function to create a new progressbar, returns the progressbar.
    @param total: Contains the maximum value of the progressbar.
    '''
    pbar = progressbar.ProgressBar(widgets=[progressbar.Percentage(), progressbar.Bar()], maxval=total).start()
    return pbar

def updatepbar(progress, pbar):
    '''
    Function to update an existing progressbar, returns the progress value.
    @param progress: Contains the new value of the progressbar.
    @param pbar: Contains an existing progressbar object.
    '''
    progress+=1
    pbar.update(progress)
    if progress == pbar.maxval:
        pbar.finish()
    return progress

def addFeaturesToLayer(layer, featlist):
    '''
    Function to split featurelist into server processable chunks, calls the upload function, returns a list of upload results.
    @param layer: Contains the layer item on the portal, where the new feature data is stored.
    @param featlist: Contains an existing progressbar object.
    '''
    global t_resultlist 
    global t_list
    n = 500
    featlistchunks = list(featlist.features[i:i+n] for i in range(0, len(featlist.features), n))
    print('Uploading layer '+layer.properties.name+' to Portal . . .')
    pbar = createpbar(len(featlistchunks))
    arglist = [(chunk, layer, pbar) for chunk in featlistchunks]
    p=0
    for chunk in arglist:
        feataddHelper(chunk)
        p = updatepbar(p,pbar)
    resultlist = t_resultlist
    t_resultlist = []
    t_list = []
    return resultlist

def feataddHelper(args):
    '''
    Function to upload a chunk of features to the layer.
    @param args: Two-dimensional list, containing a chunk of features and a reference to the layer in the portal.
    '''
    global t_resultlist
    chunk = args[0]
    layer = args[1]
    t_resultlist+=layer.edit_features(adds = chunk)['addResults']

def updateFieldDefn(ftrs):
    '''
    Function to update field definition for GlobalID and OBJECTID fields, needed for correctly working layers.
    @param ftrs: The featureset, where the field definition is appended.
    '''
    dictFieldGlobalID = {}
    dictFieldGlobalID["alias"] = "GlobalID"
    dictFieldGlobalID["name"] = "GlobalID"
    dictFieldGlobalID["type"] = "esriFieldTypeGlobalID"
    dictFieldGlobalID["sqlType"] = "sqlTypeOther"
    dictFieldGlobalID["length"] = 100
    dictFieldGlobalID["nullable"] = False
    dictFieldGlobalID["editable"] = False
    dictFieldGlobalID["domain"] = None
    dictFieldGlobalID["defaultValue"] = None
    dictFieldOBJECTID = {}
    dictFieldOBJECTID["alias"] = "OBJECTID"
    dictFieldOBJECTID["name"] = "OBJECTID"
    dictFieldOBJECTID["type"] = "esriFieldTypeOID"
    dictFieldOBJECTID["sqlType"] = "sqlTypeOther"
    dictFieldOBJECTID["length"] = 15
    dictFieldOBJECTID["nullable"] = False
    dictFieldOBJECTID["editable"] = False
    dictFieldOBJECTID["domain"] = None
    dictFieldOBJECTID["defaultValue"] = None
    ftrs.fields.append(dictFieldGlobalID)
    ftrs.fields.append(dictFieldOBJECTID)

def checkStringInNumericField(ftrs, fld):
    '''
    Function to check if a string is inside a numeric field, returns the boolean types True or False.
    @param ftrs: The featureset containing the field, that should be checked.
    @param fld: The field to be checked for strings.
    '''
    templist = []
    for val in ftrs.features:
        cols = val.attributes
        templist.append(type(cols[fld]))
    
    if type('str') in templist:
        return True
    else:
        return False


def repairDateFields(fields, ftrs):
    '''
    Function to perform inplace repairs for date type related fields.
    @param fields: The list of fields to be repaired.
    @param ftrs: The featureset containing the fields to be repaired.
    '''
    for fldname in fields:
        dictField = {}
        dictField["alias"] = fldname
        dictField["name"] = dictField["alias"]
        dictField["type"] = "esriFieldTypeDate"
        dictField["length"] = 20
        dictField["sqlType"] = "sqlTypeOther"
        ftrs.fields[fields[fldname]] = dictField     

def repairBigIntFields(fields, ftrs):
    '''
    Function to perform inplace repairs for big integer type related fields.
    @param fields: The list of fields to be repaired.
    @param ftrs: The featureset containing the fields to be repaired. 
    '''
    for fldname in fields:
        dictField = {}
        dictField["alias"] = fldname
        dictField["name"] = dictField["alias"].replace(":",u"\u005F")
        dictField["sqlType"] = "sqlTypeBigInt"
        dictField["type"] = "esriFieldTypeInteger"
        dictField["length"] = 15
        ftrs.fields[fields[fldname]] = dictField 

def createLayerDefintion(fieldDef, osmConfig, geometry, idx):
    '''
    Function to create layer definitions for upload to the portal, returns a dictionary with the layer definition.
    @param fieldDef: A list containing the field definition.
    @param osmConfig: A dictionary containing the OSM configuration defined in the file osmconfig.json. 
    @param geometry: The geometry type of the current layer.
    @param idx: The index of the current layer.
    '''
    currentCategory = osmConfig['categories'][idx]
    dictLayer = {}
    dictLayer["geometryType"] = geometry
    dictLayer["minScale"] = 0
    dictLayer["maxScale"] = 0
    dictLayer["globalIdField"] = "GlobalID"
    dictLayer["objectIdField"] = "OBJECTID"
    dictLayer["extent"] = {"xmin":osmConfig['minLon'],
                            "ymin":osmConfig['minLat'],
                            "xmax":osmConfig['maxLon'],
                            "ymax":osmConfig['maxLat'],
                            "spatialReference": {"wkid" : 4326, "latestWkid" : 4326}}
    dictLayer["name"] = str(currentCategory['categoryName'])+'-'+str(idx)+"-"+str(geometry[12:])
    dictLayer["fields"] = fieldDef
    return dictLayer      


def createFeatureServiceLayerCollection(agolConfig, osmConfig):
    '''
    Function to create a new feature service in the portal, returns a feature layer collection.
    @param agolConfig: A dictionary object containing the AGOL configuration defined in the file agolconfig.json.
    @param osmConfig: A dictionary object containing the OSM configuration defined in the file osmconfig.json.
    '''
    gis = GIS(agolConfig['portal'], agolConfig['user'], agolConfig['password'])
    title = agolConfig['title']
    tags = agolConfig['tags']
    description = agolConfig['description']
    copyrightText = agolConfig['copyrightText']
    maxRecordCount = agolConfig['maxRecordCount']
    timeNow = str(datetime.datetime.now()).replace(':','-').replace(' ','_')
    serviceName = title+'_'+timeNow
    featureService = gis.content.create_service(serviceName, wkid=4326, item_properties={"tags":tags,"extent":[osmConfig['minLat']-1.0,osmConfig['minLon']-1.0,osmConfig['maxLat']+1.0,osmConfig['maxLon']+1.0]})
    featureLayerCollection = fs.FeatureLayerCollection.fromitem(featureService)
    serviceConfiguration = {"copyrightText": copyrightText,
                            "objectIdField" : "OBJECTID",
                            "globalIdField" : "GlobalID",
                            "maxRecordCount": maxRecordCount,
                            "serviceDescription": description,
                            "capabilities": 'Create,Editing,Query,Update,Uploads,Delete,Sync,Extract',
                            "spatialReference": {"wkid": 4326,"latestWkid": 4326},
                            "initialExtent":{"xmin":osmConfig['minLon'],"ymin":osmConfig['minLat'],"xmax":osmConfig['maxLon'],"ymax":osmConfig['maxLat'], 
                                "spatialReference":{ "wkid" : 4326, "latestWkid" : 4326}},
                            "fullExtent":{"xmin":osmConfig['minLon'],"ymin":osmConfig['minLat'],"xmax":osmConfig['maxLon'],"ymax":osmConfig['maxLat'],
                                "spatialReference": {"wkid" : 4326, "latestWkid" : 4326}}}
    result = featureLayerCollection.manager.update_definition(serviceConfiguration)
    if result ['success'] == True:                            
        return featureLayerCollection
    else:
        raise Exception(result).with_traceback(result)



def uploadToPortal(agolConfig, osmConfig, osmdata):
    '''
    Function to upload osm-data to ArcGIS Online or another Portal.
    @param agolConfig: Contains user credentials and information on the portal where the data is uploaded
    @param osmConfig: Contains information on the OSM-configuration
    @param osmdata: Contains the downloaded data from osm as list of SpatialDataFrames
    '''
    layerList = []
    featSetList = []
    i=-1
    for df in osmdata:
        i+=1
        print("Preparing layer "+str(i+1)+" for upload to Portal")
        p=0
        pbar = createpbar(10)
        p = updatepbar(p, pbar)
        cols = {k:df.columns.get_loc(k) for k in dict(df.dtypes) if dict(df.dtypes)[k] in ['int64']}
        dcols = {k:df.columns.get_loc(k) for k in dict(df.dtypes) if dict(df.dtypes)[k] in ['datetime64[ns]']}
        ftrs = df.to_featureset()
        cntr=0
        fielddict={}
        p = updatepbar(p, pbar)
        for f in ftrs.fields:
            if f['name'] != 'timestamp':
                cntr+=1
                f['alias'] = f['name']
                f['name'] = "f_"+str(cntr)
                fielddict[f['alias']] = f['name']
                f['length'] = 1000
                f['sqlType'] = "sqlTypeOther"
                f['type'] = "esriFieldTypeString" 
        p = updatepbar(p, pbar)
        for feat in ftrs.features:
            for f in fielddict:
                feat.attributes[fielddict[f]] = feat.attributes.pop(f)
        p = updatepbar(p, pbar)                
        for feat in ftrs.features:
            if ftrs.global_id_field_name in feat.attributes:
                feat.attributes.pop(ftrs.global_id_field_name)
            if ftrs.object_id_field_name in feat.attributes:
                feat.attributes.pop(ftrs.object_id_field_name)
        p = updatepbar(p, pbar)
        ftrs.fields = [field for field in ftrs.fields if field['name'] != ftrs.global_id_field_name]
        p = updatepbar(p, pbar)
        updateFieldDefn(ftrs)
        repairBigIntFields(cols, ftrs)
        p = updatepbar(p, pbar)
        repairDateFields(dcols, ftrs)
        fieldlist = list(ftrs.fields)
        p = updatepbar(p, pbar)
        layerDef = createLayerDefintion(fieldlist, osmConfig, ftrs.geometry_type, osmConfig['enabledCategories'][i])
        p = updatepbar(p, pbar)
        layerList.append(layerDef)
        featSetList.append(ftrs)
        p = updatepbar(p, pbar)
    try:
        print("Preparing feature service")
        p=0
        pbar = createpbar(4)
        p = updatepbar(p, pbar)
        ftLC = createFeatureServiceLayerCollection(agolConfig, osmConfig)
        p = updatepbar(p, pbar)
        layerDict = {"layers" : layerList}
        p = updatepbar(p, pbar)
        ftLC.manager.add_to_definition(layerDict)
        p = updatepbar(p, pbar)
        for i in range(len(ftLC.layers)):
            prepareLayerUpload(ftLC, featSetList, i)
    except Exception as e:
        print('Service creation failed !, Detailed information: '+str(e))
