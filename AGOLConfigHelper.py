__version__ = "1.4"
'''
__author__ = "Simon Geigenberger, Lukas Bug"
__copyright__ = "Copyright 2018, Esri Deutschland GmbH"
__license__ = "Apache-2.0"
__version__ = "1.4"
__email__ = "simon@geigenberger.info, lukas.bug@aol.de"
'''

import json
import sys

def readConfig():
    dictAGOLConfig = {}
    
    #Try to import the ArcGIS API for Python
    try:
        from arcgis.gis import GIS
    except:
        print("ArcGIS API for Python cannot be imported")
        sys.exit()
    
    #Try to open the config file.
    try:
        json_data = open("agolconfig.json").read()
    except:
        print("JSON file does not exist.")
        sys.exit()
    
    #Try to load the config file as JSON.
    try:
        data = json.loads(json_data)
    except:
        print("JSON file cannot be read.")
        sys.exit()
    
    #Check if a portal is selected
    try:
        portalInit = data["portalInit"]
        dictAGOLConfig["portal"] = portalInit
    except:
        print("No Portal chosen.")
        sys.exit()
    
    #Check if a user is selected
    try:
        userInit = data["userInit"]
        dictAGOLConfig["user"] = userInit
    except:
        print("No user chosen.")    
        sys.exit()
    
    #check if a password is selected
    try:
        passwordInit = data["passwordInit"]
        dictAGOLConfig["password"] = passwordInit
    except:
        print("No passord box chosen.")
        sys.exit()
    
    #Try to connect to the selected portal with the login information.
    try:
        GIS(portalInit, userInit, passwordInit)
    except:
        print("Cannot connect to the portal.")
        sys.exit()
    
    #Checks if a titel is selected
    try:
        title = data["title"]
        dictAGOLConfig["title"] = title
    except:
        print("No title chosen.")
        sys.exit()
    
    #Check if tags are selected. Remove tags if the string contains only spaces.
    try:
        tags = data["tags"]
        if len(tags) == 0:
            print("No tags chosen - 1.")
            sys.exit()
        should_restart = True
        while should_restart:
            should_restart = False
            for tag in tags:
                tagTest = tag.lstrip()
                if len(tagTest) == 0:
                    tags.remove(tag)
                    should_restart = True
        if len(tags) == 0:
            print("No tags chosen - 2.")
            sys.exit()
        else:
            dictAGOLConfig["tags"] = tags
    except:
        print("No tags chosen - 3.")
        sys.exit()
    
    #Check if a description is selected.
    try:
        description = data["description"]
        dictAGOLConfig["description"] = description
    except:
        print("No description chosen.")
        sys.exit()
        
    #Checks if a copyrightText is selected
    try:
        copyrightText = data["copyrightText"]
        dictAGOLConfig["copyrightText"] = copyrightText
    except:
        print("No copyrightText chosen.")
        sys.exit()
        
    #Checks if a maxRecordCount is selected
    try:
        maxRecordCount = data["maxRecordCount"]
        dictAGOLConfig["maxRecordCount"] = maxRecordCount
    except:
        print("No maxRecordCount chosen.")
        sys.exit()
        
    dictAGOLConfig["overwriteService"] = 0
    return dictAGOLConfig
