
__version__ = "0.0.2"
'''
__author__ = "Jeffrey Scarmazzi, Lukas Bug"
__copyright__ = "Copyright 2018, Jeffrey Scarmazzi, Esri Deutschland GmbH"
__license__ = "Apache-2.0"
__version__ = "0.0.2"
__email__ = "lukas.bug@aol.de"
The module "osm_runner" was written by Jeffrey Scarmazzi (Jwmazzi) and all copyright belongs to him.
The original module can be found using the following URL: https://github.com/Jwmazzi/osm_runner
It was extended to output complex multipolygons based on relation items in OSM.
This module provides properties to configure the osm_runner module and to control requests to Overpass API.
Copyright for parts of this version of osm_runner belongs to Jeffrey Scarmazzi.
'''

# Format: http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide
# Section 13 / 13.1
Format = '[out:json]'

# Period: http://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL
# Section 5 / 5.1
Output = '(._;>;);out meta geom qt;'

# OSM Features: http://wiki.openstreetmap.org/wiki/Map_Features
# E.G. "highway" = ["primary", "residential"]
# E.G. [out:json];way["highway"~"primary|residential"](bounding_box);(._;>;);out geom qt;
Filters = {
    "aerialway": [],
    "aeroway": [],
    "amenity": [],
    "barrier": [],
    "boundary": [],
    "building": [],
    "craft": [],
    "emergency": [],
    "geological": [],
    "highway": [],
    "historic": [],
    "landuse": [],
    "leisure": [],
    "man_made": [],
    "military": [],
    "natural": [],
    "office": [],
    "place": [],
    "power": [],
    "public transport": [],
    "railway": [],
    "route": [],
    "shop": [],
    "sport": [],
    "tourism": [],
    "waterway": [],
}

# OSM Element Types
Elements = {"point": "node", "line": "way", "polygon": "way"}
