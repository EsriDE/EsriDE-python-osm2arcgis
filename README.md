# EsriDE-python-osm2arcgis

This Project contains different Python modules to convert node and way datasets from Open Street Map into formats that can be used within Esri technologies.
The current version publishes the data as point Feature Collection on ArcGIS Online. The modules can be extended with filters, schedulers or the possibility
to save the datasets as Geodatabase.

## Requirements

Following Python version and packages have to be installed. It is described how to set up the Python Environment in Anaconda:

Download and install the 3.x Version of [Anaconda](https://www.anaconda.com/download/). Then open the Anaconda Navigator and create a new Python Environment. The Python version must be 3.5 or later. Then install these packages in the environment:

* [pandas 0.20.2](http://pandas.pydata.org/): Can be found in the package list in Anaconda and installed directly.
* [click](https://github.com/pallets/click): Can be found in the package list in Anaconda and installed directly.
The other packages are installed by using the terminal and entering a line of code.
* [ArcGIS API for Python](https://developers.arcgis.com/python/): `conda install -c esri arcgis`
* [Overpass API Python Wrapper](https://github.com/mvexel/overpass-api-python-wrapper): `pip install overpass`
* [OSM API](https://pypi.python.org/pypi/osmapi): `pip install osmapi`
*[pyshp](https://pypi.python.org/pypi/pyshp): `conda install pyshp` and you have to change "path" to "paths" in line 92 in the fileops.py file of this directory in your Anaconda installation: 
Anaconda3\envs\arcgis\Lib\site-packages\arcgis-1.3.0-py3.5.egg\arcgis\features\_data\geodataset\io

## Configuration Files

### OSM Configuration

The user can put his data in two configuration files. The first one is about the [Open Streetmap Data](osmconfig.json). Categories and attributes must have the same syntax as in OSM.

| Parameter | Explanation | Example |
| --- | --- | ---|
| "categories" | Target categories for data that should be exported | "categories" : {
		"public_transport" : ["station", "platform"],
		"leisure" : ["sports_centre", "sauna"]
	} |
| "attributes" | Attributes to be stored. Field name from OSM and field name for Feature Layer. No space allowed! OSM ID is always included. The attributes are set for each category individual. So there is one JSON element for every category. The key for the element is "attributes_" + category | "attributes_public_transport" : {
		"name" : "name", 
		"wheelchair":"wheelchair", 
		"toilets":"toilets:wheelchair"
	},
	
	"attributes_leisure" : {
		"name" : "name", 
		"network" : "network",
		"operator" : "operator"
	}| "boundingBox" | Bounding box for the data to be loaded | "boundingBox" : {"minLatInit" : 48.0937890648, "minLonInit" : 11.4947891235, "maxLatInit" : 48.172382181, "maxLonInit" : 11.6242218018} |
| 
"geometries" | You can decide for every category which geometry types you want to load. If "lineAndPolygon" is chosen every closed way is returned as polygon. | "geometries" : {
		"point" : ["public_transport", "leisure"],
		"line" :[],
		"polygon": ["leisure"],
		"lineAndPolygon" : ["public_transport"]
	} |

### ArcGIS Online Configuration

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


## Input Validation
The input of the configuration files is red in and validated with two python scripts. It is checked if all necessary information is included and correct, the structure is correct and
all modules can be imported. 

## Get OSM Data
The module to get the data from Open Street Map takes a dictionary as input. This dictionary is built with the [ReadOSMConfig.py module](ReadOSMConfig.py) and contains the information
of the config file. The return value is a data frame that has the format that can be used to transform it into Esri conform data. As the Overpass API has limitations for [data download](https://wiki.openstreetmap.org/wiki/Overpass_API#Limitations) there can occur problems after finishing a download.
There is no fix limit mentioned.

## Publish Data do ArcGIS Online
The module takes the dictionary from the [ReadAGOLConfig.py module](ReadAGOLConfig.py) and the data frame with the Open Street Map data. The data is published as a Feature Collection
to the ArcGIS Online account that is defined in the configuration file.

## Issues 
Find a bug or want to request a new feature? Please let us know by submitting an issue.

## Licensing

Copyright 2017 Esri Deutschland GmbH

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

A copy of the license is available in the repository's [license.txt](license.txt) file.
