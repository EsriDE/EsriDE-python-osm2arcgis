# EsriDE-python-osm2arcgis

This Project contains different Python modules to convert node and way datasets from Open Street Map into formats that can be used within Esri technologies.
The current version publishes the geometry types point, polygon and polyline in seperate layers inside one feature service on ArcGIS Online. The modules can be extended with additional filters, schedulers or the possibility
to save the datasets as Geodatabase.

## Requirements

### Python
Following Python version and packages have to be installed. It is described how to set up the Python Environment in Anaconda:

Download and install the 3.x Version of [Anaconda](https://www.anaconda.com/download/). Then open the Anaconda Navigator and create a new Python Environment. The Python version must be 3.5 or later. Then install these packages in the environment:

* [pandas >= 0.20.2](http://pandas.pydata.org/): Can be found in the package list in Anaconda and installed directly. 
* [click >= 6.7](https://github.com/pallets/click): Can be found in the package list in Anaconda and installed directly.
The other packages are installed by using the terminal and entering a line of code.
* [ArcGIS API for Python <= 1.5.0](https://developers.arcgis.com/python/): ArcGIS API for Python must be less then version 1.5.0 or equal to work correctly with OSM2ArcGIS,ArcGIS API for Python must be equal or less than version 1.5.0 to work correctly with OSM2ArcGIS. For further information see this issue:(https://github.com/Esri/arcgis-python-api/issues/335) `conda install -c esri arcgis=1.5.0`
* [requests >= 2.18.4](http://docs.python-requests.org/en/master/) `pip install requests`
* [progressbar >= 2.5](https://pypi.org/project/progressbar/) `pip install progressbar`

### Additional Requirement
An ArcGIS Online Account with user type “Creator” (New user types) or an ArcGIS Enterprise account with user type “Level 2” (Named user, for version 10.6. and below) and at least a “Publisher” role. (An ArcGIS Online Developer Account also meets these requirements)

## First steps
1.	Setup your python environment as described in the section “Requirements”
2.	Extract the files from the downloaded OSM2ArcGIS zip archive to a location of your choice.
3.	Adapt the content of the file runScript.bat to match the paths of your Anaconda installation, the python-environment and the location of the OSM2ArcGIS folder, where the project files have been extracted to in step 2. E.g.:
```
set path=C:\your_anaconda_install_path\Anaconda3\Library\bin\;%PATH%
call conda activate OSM2ArcGIS
call "C:\Users\your_username\AppData\Local\conda\conda\envs\your_python_environment"\python.exe "C:\your_project_extraction_path"\MainModule.py
```
4.	Adapt the content of the ArcGIS Online / Portal for ArcGIS configuration file [agolconfig.json](agolconfig.json) to match your portal URL, your username and password.
5.	Optionally adapt the content of the OpenStreetMap configuration file [osmconfig.json](osmconfig.json) to the desired region, add configurations or remove the sample configuration.
6.	Execute the file [runScript.bat](runScript.bat) from your file-browser
7.	Go to your ArcGIS Online portal and look at the results
8.	Click on your most recently created feature service and use the pane “Visualization” to show the results. If you did not modify [osmconfig.json](osmconfig.json), the result should be an output like this: ![Screenshot](/OSM2ArcGIS.png?raw=true)

## Configuration Files

### OSM Configuration

The user can put his data in two configuration files. The first one is about the [Open Streetmap Data](osmconfig.json). Valid OSM keys and tags can be found on the following two OSM websites: 
* For keys: https://taginfo.openstreetmap.org/api/4/projects/keys
* For tags: https://taginfo.openstreetmap.org/api/4/projects/tags

| Parameter | Usage | <img width=2000/> Example |
| --- | --- | --- |
| "categories" | Controls the export of elements from OpenStreetMap, for every new configuration with another geometry or OSM key a new category has to be created within the following 5 properties: <br><br> - The desired OSM key for "categoryName" property. Multiple values not allowed here. <br><br> - The desired OSM tags for "categoryValue" property. Multiple values in square brackets. <br><br> - The excluded fields from service on ArcGIS Online for the "attributeFieldsToExclude" property. Multiple values in square brackets. <br><br> - The geometry type, valid types are "line", "point" or "polygon". Multiple values not allowed here. <br><br> - Set the "isEnabled" property to "yes" to activate or to "no" to deactivate a configuration. Currently unneeded configurations retainable in configuration file. | "categories" : <br> [ <br> &nbsp;&nbsp;&nbsp;&nbsp; { <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "categoryName" : "public_transport", <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "categoryValues" :["station", "platform"], <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "attributeFieldsToExclude" : ["bus", "tram"], <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "geometryType" : "polygon", <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "isEnabled" : "yes" <br> &nbsp;&nbsp;&nbsp;&nbsp; }, <br> &nbsp;&nbsp;&nbsp;&nbsp; { <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "categoryName" : "public_transport", <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "categoryValues" : ["station", "platform"], <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "attributeFieldsToExclude" : ["bus", "tram"], <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "geometryType" : "point", <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "isEnabled" : "yes" <br> &nbsp;&nbsp;&nbsp;&nbsp; }, <br> &nbsp;&nbsp;&nbsp;&nbsp; { <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "categoryName" : "public_transport", <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "categoryValues" : ["platform", "network"], <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "attributeFieldsToExclude" : ["bus", "tram"], <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "geometryType" : "line", <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "isEnabled" : "yes" <br> &nbsp;&nbsp;&nbsp;&nbsp; } <br> ] 
| "boundingBox" | Bounding box for the data to be loaded. Multiple bounding boxes not allowed here. | "boundingBox" : <br> { <br> &nbsp;&nbsp;&nbsp;&nbsp; "minLatInit" : "48.0503", <br> &nbsp;&nbsp;&nbsp;&nbsp; "minLonInit" : "11.2723", <br> &nbsp;&nbsp;&nbsp;&nbsp; "maxLatInit" : "48.2597", <br> &nbsp;&nbsp;&nbsp;&nbsp; "maxLonInit" : "11.8113" <br> } |

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
The input of the configuration files is read in and validated with two python scripts. It is checked if all necessary information is included and correct, the structure is correct and
all modules can be imported. 

## Get OSM Data
The module to get the data from Open Street Map takes a dictionary as input. This dictionary is built with the [OSMConfigHelper.py module](OSMConfigHelper.py) and contains the information
of the config file. The return value is a data frame that has the format that can be used to transform it into Esri conform data. As the Overpass API has limitations for [data download](https://wiki.openstreetmap.org/wiki/Overpass_API#Limitations) there can occur problems after finishing a download.
There is no fix limit mentioned. The boundingBox should not be larger as a city or town an its suburbs. A good approach is the selection of an extent, which matches the area of a city or town. This can be accomplished by searching for the name of the city or town on [OSM](https://www.openstreetmap.org/export#map=12/48.1551/11.5418) and click on the "Export" button.

## Publish Data to ArcGIS Online
The module takes the dictionary from the [AGOLConfigHelper.py module](AGOLConfigHelper.py) and the data frame with the Open Street Map data. The data is published in up to three layers for the three geometry types line, point and polygon in one feature service in ArcGIS Online.
The ArcGIS Online account defined in the configuration file will be used to upload the data to your ArcGIS Online portal.
When the script has finished to upload the data successfully, a new layer is visible in the ["Content"](http://www.arcgis.com/home/content.html) pane in your ArcGIS Online portal.

## Issues 
Find a bug or want to request a new feature? Please let us know by submitting an issue.

## Licensing

Copyright 2018 Esri Deutschland GmbH

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

A copy of the license is available in the repository's [license.txt](license.txt) file.
