'''
__author__ = "Simon Geigenberger"
__copyright__ = "Copyright 2017, Esri Deutschland GmbH"
__license__ = "Apache-2.0"
__version__ = "1.0"
__email__ = "s.geigenberger@esri.de"

This module is used to set up the configuration data and call the functions in the GetOsmData and DataToAGO modules.
'''

import ReadAGOLConfig
import ReadOSMConfig
import GetOsmData
import DataToAGO

dictAGOLConfig = ReadAGOLConfig.readAGOLConfig()
print("ArcGIS Online / Portal configuration red in.")

dictOSMConfig = ReadOSMConfig.readOSMConfig()
print("OpenStreetMap configuration red in.")

#The OSM data of the requested categories and geometries is loaded as point data with the requested attributes if available. The data is returned as a data frame.
god = GetOsmData.run(dictOSMConfig, dictAGOLConfig)
print("OpenStreetMap data loaded.")

#The data of the data frame with the OSM data is loaded as a Feature Collection to the ArcGIS Online or Portal account. 
dta = DataToAGO.run(dictAGOLConfig, god)
print("Upload to ArcGIS Online / Portal finished.")

#Geigenberger01 - Passwort Portal, https://vsdev1817.esri-de.com/arcgis/home/