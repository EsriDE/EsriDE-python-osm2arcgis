'''
__author__ = "Simon Geigenberger"
__copyright__ = "Copyright 2018, Esri Deutschland GmbH"
__license__ = "Apache-2.0"
__version__ = "1.3"
__email__ = "s.geigenberger@esri.de"

This module is used to set up the configuration data and call the functions in the OSM_to_DataFrame and DataFrame_to_AGOL modules.
'''

import ReadAGOLConfig
import ReadOSMConfig
import OSM_to_DataFrame
import DataFrame_to_AGOL

import datetime
print(datetime.datetime.now())

dictAGOLConfig = ReadAGOLConfig.readAGOLConfig()
print("ArcGIS Online / Portal configuration red in.")

dictOSMConfig = ReadOSMConfig.readOSMConfig()
print("OpenStreetMap configuration red in.")

# The OSM data of the requested categories and geometries is loaded as point data with the requested attributes if available. The data is returned as a data frame.
dataFrameOSMData = OSM_to_DataFrame.run(dictOSMConfig)
print("OpenStreetMap data loaded.")

# The data of the data frame with the OSM data is loaded as a Feature Collection to the ArcGIS Online or Portal account. 
for spatialDataFrameCategory in dataFrameOSMData:
    DataFrame_to_AGOL.run(dictAGOLConfig, spatialDataFrameCategory)
print("Upload to ArcGIS Online / Portal finished.")

print(datetime.datetime.now())