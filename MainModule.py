__version__ = "1.4"
'''
__author__ = "Simon Geigenberger, Lukas Bug"
__copyright__ = "Copyright 2018, Esri Deutschland GmbH"
__license__ = "Apache-2.0"
__version__ = "1.4"
__email__ = "s.geigenberger@esri.de, lukas.bug@aol.de"

This module is used to set up the configuration data and call the functions in the OSMHelper and AGOLHelper modules.
'''

import OSMConfigHelper
import AGOLConfigHelper
import OSMHelper
import AGOLHelper
import datetime
print(datetime.datetime.now())

# The AGOL configuration is read in and validated.
agolConfig = AGOLConfigHelper.readConfig()
print('ArcGIS Online / Portal configuration read in.')

# The OSM configuration is read in and validated.
osmConfig = OSMConfigHelper.readConfig(agolConfig)
print('OpenStreetMap configuration read in.')

# The OSM data of the requested categories and geometries is loaded as point data with the requested attributes if available. The data is returned as a data frame.
OSMDataFrameList = OSMHelper.getDataFrameList(osmConfig)
print('OpenStreetMap data loaded.')

# The data of the data frame with the OSM data is uploaded as a Feature Collection to the ArcGIS Online or Portal account.
AGOLHelper.uploadToPortal(agolConfig, osmConfig, OSMDataFrameList)
print('Upload to ArcGIS Online / Portal finished.')

print(datetime.datetime.now())