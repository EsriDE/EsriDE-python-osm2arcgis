__version__ = "1.4"
'''
__author__ = "Lukas Bug"
__copyright__ = "Copyright 2018, Esri Deutschland GmbH"
__license__ = "Apache-2.0"
__version__ = "1.4"
__email__ = "lukas.bug@aol.de"
'''
from enum import Enum

class OSMConfigHelperExceptions(Enum):
    invalid_boundingbox = (1001,'The specified boundingbox is invalid, please check "boundingBox"-item in OSM-configfile (osmconfig.json).')
    invalid_category = (1002,'The specified category is invalid, please check "categoryName"-item in OSM-configfile (osmconfig.json).')
    invalid_exclude = (1003,'The specified excluded attributes are invalid, please check "attributeFieldsToExclude"-item in OSM-configfile (osmconfig.json).')
    invalid_catval = (1004,'The specified category-values are invalid, please check "categoryValues"-item in OSM-configfile (osmconfig.json).')
    invalid_geomtype = (1005,'The specified geometry-type is invalid, please check "geometryType"-item in OSM-configfile (osmconfig.json).')
    def __init__(self, cde, dsc):
        self.err = cde
        self.dsc = dsc
    @property
    def code(self):
        return self.err
    @property
    def description(self):
        return self.dsc


class AGOLConfigHelperExceptions(Enum):
    invalid_credentials = (2001,'The specified credentials are invalid, please check "userInit" and "passwordInit"-items in ArcGIS Online-configfile (agolconfig.json).')
    invalid_portal = (2002,'The specified portal is invalid or not connected to your account, please check "portalInit"-item in ArcGIS Online-configfile (agolconfig.json).')
    no_title = (2003,'No title chosen, please check "title"-item in ArcGIS Online-configfile (agolconfig.json).')
    no_tags = (2004,'No tags chosen, please check "tags"-item in ArcGIS Online-configfile (agolconfig.json).')
    no_description = (2005,'No description chosen, please check "description"-item in ArcGIS Online-configfile (agolconfig.json).')
    no_copyright = (2006,'No copyright-text chosen, please check "copyrightText"-item in ArcGIS Online-configfile (agolconfig.json).')
    no_maxrecordcount = (2007,'No maximum value for record count chosen, please check "maxRecordCount"-item in ArcGIS Online-configfile (agolconfig.json).')
    tohigh_maxrecordcount = (2008,'Maximum value for record count is set higher than 200,000 items, this may result in a large network traffic volume and poor performance. \n \
    You are advised to reduce value in "maxRecordCount"-item in ArcGIS Online-configfile (agolconfig.json).')
    def __init__(self, cde, dsc):
        self.err = cde
        self.dsc = dsc
    @property
    def code(self):
        return self.err
    @property
    def description(self):
        return self.dsc


class OSMHelperExceptions(Enum):
    osm_unreachable  = (3001,'The OSM-Server is not reachable, try again later.')
    osm_emptyresponse = (3002,'The OSM-Server returned an empty response, no features were fetched, please check your OSM-configfile (osmconfig.json).')
    osm_extenttolarge = (3003,'The OSM-Server returned an error, because your data extent is to large to be handled by the server, select a smaller extent.')
    osm_confignotfound = (3004,'OSM-configfile (osmconfig.json) was not found, please ensure the file exists.')
    osm_unknownerror = (3005,'Unknown error occured, please check your OSM-configfile (osmconfig.json).')
    osm_emptydataset = (3006,'No OSM-data returned, the resulting spatialDataFrame is empty, cannot proceed to ArcGIS Online upload.')
    def __init__(self, cde, dsc):
        self.err = cde
        self.dsc = dsc
    @property
    def code(self):
        return self.err
    @property
    def description(self):
        return self.dsc


class AGOLHelperExceptions(Enum):
    agol_couldnotupload = (4001,'The data could not be uploaded to ArcGIS Online, please ensure the dataset is valid and not to large.')
    agol_unknownerror = (4002,'Unknown error occured, please try again later.')
    def __init__(self, cde, dsc):
        self.err = cde
        self.dsc = dsc
    @property
    def code(self):
        return self.err
    @property
    def description(self):
        return self.dsc