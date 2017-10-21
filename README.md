# EsriDE-python-osm2arcgis

This Project contains different Python modules to convert node and way datasets from Open Street Map into formats that can be used within Esri technologies.
The current version publishes the data as point Feature Collection on ArcGIS Online. The modules can be extended with filters, schedulers or the possibility
to save the datasets as Geodatabase.

##Requirements

Following Python version and packages have to be installed:

* [Python 3.5](https://www.python.org/downloads/release/python-350/)
* [ArcGIS API for Python](https://developers.arcgis.com/python/)
* [pandas 0.20.2](http://pandas.pydata.org/)
* [Overpass API Python Wrapper](https://github.com/mvexel/overpass-api-python-wrapper)
* [OSM API](https://pypi.python.org/pypi/osmapi)

## Configuration Files
The user can put his data in two configuration files. The first one is about the [Open Streetmap Data](osmconfig.json). Categories and attributes must have the same syntax as in OSM.

| Parameter | Explanation | Example |
| --- | --- | ---|
| "categories" | Target categories for data that should be exported | "categories" : {"public_transport" : ["station"],"amenity" : ["place_of_worship", "bar"]} |
| "attributes" | Attributes to be stored. Field name from OSM and field name for Feature Layer. No space allowed! Latitude, longitude, user, timestamp and id are always included. | "attributes" : {"Name" : "name", "Rollstuhlgerecht":"wheelchair", "Rollstuhlgerechte_Toilette":"toilets:wheelchair"} |
| "boundingBox" | Bounding box for the data to be loaded | "boundingBox" : {"minLatInit" : 48.0937890648, "minLonInit" : 11.4947891235, "maxLatInit" : 48.172382181, "maxLonInit" : 11.6242218018} |
| "geometryChosen" | Geometry of data to be loaded. 0:nodes, 1:ways, 2:both | "geometryChosen" : 0 |


The second file is used do configure the [ArcGIS Online access](agolconfig.json).

| Parameter | Explanation | Example |
| --- | --- | ---|
| "portalInit" | URL from ArcGIS Online or the portal to publish the service | "portalInit" : "http://www.arcgis.com/home/index.html" |
| "userInit" | User to publish the service | "userInit" : "user" |
| "passwordInit" | User´s password | "passwordInit" : "password" |
| "title" | Service´s title | "title" : "title" |
| "tags" | Tags for the service. Seperated by comma | "tags" : ["tag1, tag2, tag2"] |
| "description" | Description for the service | "description" : "description." |
| "copyrightText" | Copyright text for the service | "copyrightText" : "Copyright" |
| "maxRecordCount" | Max Record Count for the service | "maxRecordCount" : 5000 |
| "updateService" | If the value is "0" a new service with the data is published. If the value is "1" an existing service is overwritten and a service id is required | "updateService" : 1 |
| "featureServiceID" | Feature Service ID to update a service. | "featureServiceID" : "4cfcbee9f1de4ed9a167e0c7b8d11825" |
| "overwriteFeatureService" | This tag is for the users safety. Because it hast o be  "1" that the Feature Service is realy overwritten with the new data. If the Feature Service should be updated and the value is not "1" there will not be an update. | "overwriteFeatureService" : 1 |



## Input Validation
The input of the configuration files is red in and validated with two python scripts. It is checked if all necessary information is included and correct, the structure is correct and
all modules can be imported. 

## Get OSM Data
The module to get the data from Open Street Map takes a dictionary as input. This dictionary is built with the [ReadOSMConfig.py module](ReadOSMConfig.py) and contains the information
of the config file. The return value is a data frame that has the format that can be used to transform it into Esri conform data.

## Publish Data do ArcGIS Online
The module takes the dictionary from the [ReadAGOLConfig.py module](ReadAGOLConfig.py) and the data frame with the Open Street Map data. The data is published as a Feature Collection
to the ArcGIS Online account that is defined in the configuration file.

##Issues 
Find a bug or want to request a new feature? Please let us know by submitting an issue.

##Licensing

Copyright 2017 Esri Deutschland GmbH

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

A copy of the license is available in the repository's [license.txt](license.txt) file.