__version__ = "1.4"
'''
__author__ = "Lukas Bug"
__copyright__ = "Copyright 2018, Esri Deutschland GmbH"
__license__ = "Apache-2.0"
__version__ = "1.4"
__email__ = "lukas.bug@aol.de"
'''

from osm_runner import gen_osm_sdf
from osm_runner_utils import Filters
from threading import Thread
from ExceptionHelper import OSMHelperExceptions as osmh_excps
import os,traceback
threadlist = []
sdflist = []
def requestOSMData(osmconfig, elem, sdflist):
    '''
    Function to prepare request of an OSM data item using osm-runner
    @param osmconfig: A dictionary containing the OSM configuration defined in the file osmconfig.json. 
    @param elem: OSM-configuration item (category) defined in the file osmconfig.json
    @param sdflist: List of spatial dataframes needed for upload to portal.
    '''
    if elem['isEnabled'] == 'yes':
        geom = elem['geometryType']
        bbox = osmconfig['boundingBox']
        category = elem['categoryName']
        excludedattributes = elem['attributeFieldsToExclude']
        Filters[elem['categoryName']] = elem['categoryValues']
        osmdata = fetchOSMData(geom, bbox, category, excludedattributes)
        sdflist.append(osmdata)

def getDataFrameList(osmconfig):
    '''
    Function to initiate simulatenous (Thread-based) requests to OSM using osm-runner.
    @param osmConfig: A dictionary containing the OSM configuration defined in the file osmconfig.json. 
    '''
    for elem in osmconfig['categories']:
        t = Thread(target=requestOSMData, args=[osmconfig, elem, sdflist])
        threadlist.append(t)
        t.start()
    for t in threadlist:
        t.join()
    return sdflist

def fetchOSMData(geom, bbox, category, excludedattributes):
    '''
    Function to create layer definitions for upload to portal.
    @param geom: The geometry type of the requested data.
    @param bbox: The extent of the requested data defined by a bounding box. 
    @param category: The category name of the requested data.
    @param excludedattributes: The attributes to be excluded from the current layer.
    '''
    try:
        print('Fetching '+geom+' data from OpenStreetMap on category: '+category+' . . .')
        if geom != 'polygon':
            sdf = gen_osm_sdf(geom, bbox, excludedattributes, category)
            if not sdf.empty:
                return sdf
            else:
                if FileNotFoundError:
                    raise FileNotFoundError
                if ConnectionRefusedError:
                    raise ConnectionRefusedError
                if RuntimeError:
                    raise RuntimeError
        else:
            sdf = gen_osm_sdf(geom, bbox, excludedattributes, category, 1)
            if not sdf.empty:
                return sdf
            else:
                if FileNotFoundError:
                    raise FileNotFoundError
                if ConnectionRefusedError:
                    raise ConnectionRefusedError
                if RuntimeError:
                    raise RuntimeError
    except FileNotFoundError:
        tb = traceback.format_exc()
        print('OSM request could not be completed. \n Cause: OSM returned empty result for geometry '+geom+' , \
        the scripts exits now. Additional configuration information: Category: '+category+', excluded attributes: \
        '+excludedattributes+', \n Disable this configuration and try again. Detailed information: '+tb)
        os._exit(-1)
    except ConnectionRefusedError:
        tb = traceback.format_exc()
        print('OSM request could not be completed. \n Cause: OSM refused the connection due to too many requests, \
        try again later. Detailed information: '+tb)
        os._exit(-1)
    except RuntimeError:
        tb = traceback.format_exc()
        print('OSM request could not be completed. \n Cause: OSM returned an unknown error. Detailed information: '+tb)
        os._exit(-1)