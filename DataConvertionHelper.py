'''
__author__ = "Simon Geigenberger"
__copyright__ = "Copyright 2018, Esri Deutschland GmbH"
__license__ = "Apache-2.0"
__version__ = "1.3"
__email__ = "s.geigenberger@esri.de"
'''

from arcgis import features as fs
from arcgis import geometry as geom

def getEsriSpatialDataFrame(listGeometries):
    spatialDataFrame = fs.SpatialDataFrame(data = listGeometries[0], geometry = listGeometries[1])
    return spatialDataFrame

def getEsriFeatureSet(listGeometries):
    spatialDataFrame = getEsriSpatialDataFrame(listGeometries)
    featureSet = spatialDataFrame.to_featureset()
    
    return featureSet

def getPoint(lon, lat):
    dictSpatialReference = {}
    dictPoint = {}
    
    dictSpatialReference["wkid"] = 4326
    
    dictPoint["x"] = lon
    dictPoint["y"] = lat
    dictPoint["spatialReference"] = dictSpatialReference
    
    geometryPoint = geom.Point(dictPoint)
    
    return geometryPoint

def getPointGeometry(dictPoint):
    
    geometryPoint = geom.Point(dictPoint)
    
    return geometryPoint

def getLinePolygon(listCoordinates):
    dictSpatialReference = {}
    dictPolygon = {}
    dictPolyline = {}
    
    dictSpatialReference["wkid"] = 4326
    
    dictPolygon["rings"] = listCoordinates
    dictPolygon["spatialReference"] = dictSpatialReference
    
    geometry = geom.Polygon(dictPolygon)
    
    if geometry.is_valid:
        return geometry
    
    else:
        dictPolyline["paths"] = listCoordinates
        dictPolyline["spatialReference"] = dictSpatialReference
        geometry = geom.Polyline(dictPolyline)
        return geometry
    
def getLine(listCoordinates):
    dictSpatialReference = {}
    dictPolyline = {}
    
    dictSpatialReference["wkid"] = 4326

    dictPolyline["paths"] = listCoordinates
    dictPolyline["spatialReference"] = dictSpatialReference
    
    geometry = geom.Polyline(dictPolyline)
    
    return geometry
    
def getLinePolygonGeometry(dictPolygonLine):
    
    if "rings" in dictPolygonLine:
        geometry = geom.Polygon(dictPolygonLine)
        return geometry
    
    elif "paths" in dictPolygonLine:
        geometry = geom.Polyline(dictPolygonLine)
        return geometry