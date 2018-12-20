__version__ = "0.0.2"
from osm_runner_utils import Format, Output, Filters, Elements
from arcgis.geometry import Point, Polyline, Polygon
from arcgis.features import SpatialDataFrame
from arcgis import geometry as geom
from datetime import datetime as dt
import requests,time
import progressbar,traceback,operator

def merge_sublist_items(sublist):
    '''
    Function to merge sublist items, returns the merged list.
    @param sublist: A sublist to merge
    '''
    total = []
    for sublistitem in sublist:
        total += sublistitem
    return total

def createpbar(total):
    '''
    Function to create a new progressbar, returns the progressbar.
    @param total: Contains the maximum value of the progressbar.
    '''
    pbar = progressbar.ProgressBar(widgets=[progressbar.Percentage(), progressbar.Bar()], maxval=total).start()
    return pbar

def updatepbar(progress, pbar):
    '''
    Function to update an existing progressbar, returns the progress value.
    @param progress: Contains the new value of the progressbar.
    @param pbar: Contains an existing progressbar object.
    '''
    progress+=1
    pbar.update(progress)
    if progress == pbar.maxval:
        pbar.finish()
    return progress

def checkrings_connected(lst,r):
    '''
    Function to check if all rings in the list are connected, returns the boolean values True or False.
    @param lst: A list of rings.
    '''
    connectedlist = []
    for ring in range(len(lst)):
        try:
            if lst[ring][0] == lst[ring-1][-1]:
                connectedlist.append(ring) 
        except:
            break
    if len(connectedlist) == len(lst):
        return True 
    else:
        return False

def checkrings_closed(lst,r):
    '''
    Function to check if all rings in the list are closed (valid), returns the boolean values True or False.
    @param lst: A list of rings.
    '''
    newlst = []
    for ring in range(len(lst)):
        if lst[ring][0] == lst[ring][-1]:
            newlst.append(ring)
    if len(lst) == len(newlst):            
        return True
    else:
        return False

def detect_rings(lst):
    '''
    Function to identify polygon rings in a ring-ordered geometry list, returns the identified rings containing geometries.
    @param lst: A list with ring-ordered geometries.
    '''
    ringlist = []
    start = 0
    end = -1
    for e in range(len(lst)):
        if lst[e] == lst[start] and e > start:
            end = e
            ringlist.append(lst[start:end+1])
            start = e+1           
    return ringlist

def l_ordered_remove_duplicates(lst):
    '''
    Function to remove duplicates in a ring-ordered geometry list, appends start element to close the polygon ring.
    Returns a duplicate-free (except start and end) list -> a valid polygon ring.
    @param lst: A list with ring-ordered geometries.
    '''
    if lst:
        present = set()
        present_add = present.add
        duplicate_free_l = [x for x in lst if not (x in present or present_add(x))]
        duplicate_free_l.append(lst[0])
        return duplicate_free_l

def lget (l, idx, default=[]):
    '''
    Function to implement a get-method, known from dictionaries, for lists. 
    Returns either the element at the index position or the default value, an empty list.
    @param l: A list.
    @param idx: A list index.
    @param default: A value to be returned by the function if index does not exist.
    '''
    try:
        return l[idx]
    except IndexError:
        return default

def lfindgetsingleidx(l, val, excl):
    '''
    Function to get the position of a value in a list of lists e.g. geometries in a polygon ring list. 
    A known index can be excluded from search results, to find the appropriate index, not the first one.
    Returns the sublist index, where the value is located and the index of the value in the sublist.
    @param l: A list containing a sublist with values.
    @param val: A value e.g. a geometry tuple.
    @param excl: An excluded index e.g. a known index, in cases an element is provided, which is also inside a known sublist.
    '''
    try:
        validx = [idx for idx,item in enumerate(l) if idx != excl and val in item][0]
        result = [validx, l[validx].index(val)]
        return result
    except:
        return []

def merge_dict_lists(dict_list1, dict_list2):
    '''
    Function to merge lists in a dictionary.
    Returns a dictionary with merged lists.
    @param dict_list1: First list.
    @param dict_list2: Second list.
    '''
    keys = set(dict_list1).union(dict_list2)
    empty1 = ['' for i in range(len(dict_list1['osm_id']))]
    empty2 = ['' for i in range(len(dict_list2['osm_id']))]
    return dict((k, dict_list1.get(k, empty1) + dict_list2.get(k, empty2)) for k in keys)

def gen_osm_sdf(geom_type, bound_box, excludedattributes, osm_tag=None, relation=None, time_one=None, time_two=None, present=False):
    '''
    Function to send requests to OpenStreetMap.
    Returns an Esri SpatialDataFrame.
    @param geom_type: Specifies input geometry. Value must be either "point", "line", or "polygon".
    @param bound_box: A bounding box specified.
    @param subdict: A boolean value, True or False. Controls if subdictionaries are included into searches or not.
    '''

    geom_type = geom_type.lower()

    if geom_type not in ['point', 'line', 'polygon']:
        raise Exception('Geometry Type "{0}" Does Not Match Input Options: point|line|polygon'.format(geom_type))

    else:
        osm_element = Elements.get(geom_type)

        query = get_query(osm_element, bound_box, osm_tag, time_one, time_two, present)

        osm_response = get_osm_elements(query, 0)
        
        if geom_type == 'polygon':
            
            r_query = get_query("relation", bound_box, osm_tag, time_one, time_two, present)

            osm_r_response = get_osm_elements(r_query, 0)

            base_sdf = build_ways_sdf_topoly(osm_response, excludedattributes, osm_r_response)

        if geom_type == 'point':
            base_sdf = build_node_sdf(osm_response, excludedattributes)

        if geom_type == 'line':
            base_sdf = build_ways_sdf_toline(osm_response, excludedattributes)

        sdf = fields_cleaner(base_sdf)

        return sdf


def get_query(osm_el, b_box, o_tag, t1, t2, present_flag):
    '''
    Function to construct query for OpenStreetMap Server.
    Returns the assembled query.
    @param osm_el: Specifies the OpenStreetMap element. Valid values are "node", "way" or "relation" 
    @param b_box: Specifies bounding box with geodata inside. Valid values are either "point", "line", or "polygon".
    @param o_tag: Specifies the OpenStreetMap tag / category element.
    @param t1: Minimum timestamp of the returned OSM content.
    @param t2: Maximum timestamp of the returned OSM content.
    @param present_flag: Specifies if the time until or from now is used to define the minimum or maximum timestamp. 
                         Only t1 or t2 and the present_flag are valid combinations. 
                         Present_flag can be any positive value e.g. True, 1...
    '''

    if osm_el.lower() not in ['node', 'way', 'relation']:
        raise Exception('OSM Element {0} Does Not Match Configuration Options: node|way'.format(osm_el))

    head = get_query_head(Format, t1, t2, present_flag)
    if o_tag:

        o_tag = o_tag.lower()
        filters = Filters.get(o_tag)

        if filters:
            filters = [f.lower() for f in filters]
            f = '|'.join(filters)
            f_clause = '["' + o_tag + '"~"' + f + '"]'
            return ';'.join([
                head,
                ''.join([str(osm_el), f_clause, str(b_box)]),
                Output
            ])
            # E.G. [out:json];way["highway"~"primary|residential"](bounding_box);(._;>;);out geom qt;

        else:
            f_clause = '["' + o_tag + '"]'
            return ';'.join([
                head,
                ''.join([str(osm_el), f_clause, str(b_box)]),
                Output
            ])
            # E.G. [out:json];way["highway"](bounding_box);(._;>;);out geom qt;

    else:
        return ';'.join([
            head,
            ''.join([str(osm_el), str(b_box)]),
            Output
        ])
        # E.G. [out:json];way(bounding_box);(._;>;);out geom qt;


def get_query_head(f, t_1, t_2, p_flag):
    '''
    Function to construct query for OpenStreetMap Server.
    Returns the assembled query.
    @param Format: Specifies the OSM format for queries, specified inside the .utils class of this module" 
    @param t1: Minimum timestamp of the returned OSM content.
    @param t2: Maximum timestamp of the returned OSM content.
    @param present_flag: Specifies if the time until or from now is used to define the minimum or maximum timestamp. 
                         Only t1 or t2 and the present_flag are valid combinations. 
                         Present_flag can be any positive value e.g. True, 1...
    '''

    if not t_1 and not t_2:
        return f

    else:
        if p_flag:
            if t_1 and not t_2:
                d = '[diff: "' + t_1 + '", "' + dt.today().strftime('%Y-%m-%d') + '"]'

            elif t_2 and not t_1:
                d = '[diff: "' + t_2 + '", "' + dt.today().strftime('%Y-%m-%d') + '"]'

            else:
                raise Exception('Invalid Parameters - Please Only Specify One Time Parameter When Using Present')

        else:
            if t_1 and not t_2:
                d = '[date: "' + t_1 + '"]'

            elif t_2 and not t_1:
                d = '[date: "' + t_2 + '"]'

            else:
                d = '[diff: "' + t_1 + '", "' + t_2 + '"]'

    return ''.join([f, d])


def get_osm_elements(osm_query, retry_once, response=None):
    '''
    Function to request data from the OpenStreetMap Server.
    Returns the requested data or raises an exception after a few unsuccessful tries.
    @param osm_query: Specifies the OSM query as returned by the get_query function" 
    @param retry_once: Specifies if a request to OSM has already been send. The value at first runtime should be 0.
    @param response: Specifies the answer from the server, default is None. 
                     Has no None value if a previous request to the server failed and the function is recalled internally only.
    @param present_flag: Specifies if the time until or from now is used to define the minimum or maximum timestamp. 
                         Only t1 or t2 and the present_flag are valid combinations. 
                         Present_flag can be any positive value e.g. True, 1...
    '''

    osm_api = 'https://lz4.overpass-api.de/api/interpreter'

    if retry_once == 0:

        r = requests.get(osm_api, data=osm_query)
    
    elif retry_once == 1:
        r = requests.get(osm_api, data=osm_query) 

    if r.status_code == 200:

        if len(r.json()['elements']) == 0:

            try:
                raise FileNotFoundError('OSM Returned Zero Results with Remark: {}'.format(r.json()['remark']))

            except KeyError:
                raise FileNotFoundError('OSM Returned Zero Results for Query: {}'.format(osm_query))

        else:
            result = r.json()['elements']
            return result

    if r.status_code == 429:
        print("OSM Request Limit Reached. We are waiting 60 seconds and retry afterwards...")
        time.sleep(60)
        get_osm_elements(osm_query, 1)

    if r.status_code == 429 and retry_once == 1:
            get_osm_elements(osm_query, 2, r)       
    else:
            result = r.json()['elements']
            return result
    
    if response.status_code == 429 and retry_once == 2:
        raise ConnectionRefusedError('OSM Request Limit Reached. Please Try Again in a Few Minutes . . .')

    else:
        raise RuntimeError('OSM Returned Status Code: {0}'.format(r.status_code))


def build_node_sdf(n_list, excludedattributes):
    '''
    Function to convert returned OSM point data to Esri SpatialDataFrame.
    Returns an ESRI SpatialDataFrame.
    @param n_list: The list of nodes as returned by th get_osm_elements function 
    @param excludedattributes: The attributes exluded in the configuration file osmconfig.json
    '''

    # Dictionary For Geometries & IDs
    geo_dict = {"geo": []}
    val_dict = {'osm_id': [], 'timestamp': []}

    # Dictionary For Incoming Tags
    for n in n_list:
        n_tags = n['tags'].keys()
        for tag in n_tags:
            if tag not in val_dict.keys() and tag not in excludedattributes:
                tagname = tag
                val_dict[tagname] = []
    
    print('Constructing points...')                
    p=0
    pbar = createpbar(len(n_list))
    # Build Lists
    for n in n_list:
        try:
            p = updatepbar(p, pbar)
            # Populate Tags
            for tag in [key for key in val_dict.keys() if key not in ['osm_id','timestamp'] and key not in excludedattributes]:
                val_dict[tag].append(n['tags'].get(str(tag),''))

            # Populate Geometries & IDs
            point = Point({
                "x": n['lon'],
                "y": n['lat'],
                "spatialReference": {"wkid": 4326}
            })
            geo_dict['geo'].append(point)
            val_dict['osm_id'].append(str(n['id']))
            val_dict['timestamp'].append(dt.strptime(n['timestamp'],'%Y-%m-%dT%H:%M:%SZ'))

        except Exception as ex:
            print('Node ID {0} Raised Exception: {1}'.format(n['id'], str(ex)))

    try:
        val_dict = {k: v for k, v in val_dict.items() if v is not None}
        return SpatialDataFrame(val_dict, geometry=geo_dict['geo'])

    except TypeError:
        raise Exception('Ensure ArcPy is Included in Python Interpreter')


def build_ways_sdf_topoly(o_response, excludedattributes, o_r_response=None):
    '''
    Function to convert returned OSM polygon data to Esri SpatialDataFrame.
    Returns an ESRI SpatialDataFrame.
    @param o_response: The valid response data from the OSM server containing the way elements
    @param excludedattributes: The attributes exluded in the configuration file osmconfig.json
    @param o_r_response: The optional valid response data from the OSM server containing the relation elements
    '''
    # Extract relevant relations and way elements from OSM response
    if o_r_response:
        relations = [e for e in o_r_response if e['type'] == 'relation']
    ways = [e for e in o_response if e['type'] == 'way' and e['nodes'][0] == e['nodes'][-1]]

    # Dictionary for geometries & IDs
    geo_dict_r = {'geo': []}
    val_dict_r = {'osm_id': [], 'timestamp': []}
    geo_dict_w = {'geo': []}    
    val_dict_w = {'osm_id': [], 'timestamp': []}
    invalid_rel_idx_list = []
    for r in range(len(relations)):
        nodesinrel = []
        nodesinrel = [relations[r]['members'].index(item) for item in filter(lambda n: n.get('type') == 'node', lget(relations,r)['members'])]
        if len(nodesinrel) > 0:
            invalid_rel_idx_list.append(r)
    
    relations = [lget(relations,r) for r in range(len(relations)) if r not in invalid_rel_idx_list]

    # Dictionary for incoming relation tags
    for r in relations:
        r_tags = r['tags'].keys()
        for tag in r_tags:
            if tag not in val_dict_r.keys() and tag not in excludedattributes:
                tagname = tag
                val_dict_r[tagname] = []
    
    valid_list = []
    # Build Lists
    print('Constructing complex polygons...')
    p=0
    pbar = createpbar(len(relations))
    for r in relations:
        try:
            p = updatepbar(p, pbar)
            relation = r["members"]
            relation = sorted(relation, key=lambda item: item['role'])
            outerlist = [memb for memb in relation if memb['role'] == 'outer']
            innerlist = [memb for memb in relation if memb['role'] == 'inner']
            innerlistgeomtuple = []
            outerlistgeomtuple = []
            innerlistgeomtuple2 = []
            outerlistgeomtuple2 = []
            rngitn_i = False
            rngitn_o = False
            
            innerlistgeomtuple = [[(x['lon'],x['lat']) for x in ol['geometry']] for ol in innerlist]
            if len(innerlistgeomtuple) > 1:
                all_rings_connected_i = checkrings_connected(innerlistgeomtuple,r)
                if all_rings_connected_i and innerlistgeomtuple:
                    for ring in innerlistgeomtuple:
                        innerlistgeomtuple2+=ring
                    innerlistgeomtuple = []
                    innerlistgeomtuple.append(l_ordered_remove_duplicates(innerlistgeomtuple2))
                    innerlistgeomtuple2 = innerlistgeomtuple
                    innerlistgeomtuple = []
            all_rings_closed_i = checkrings_closed(innerlistgeomtuple, r)
            if all_rings_closed_i and innerlistgeomtuple:
                for ring in innerlistgeomtuple:
                    innerlistgeomtuple2.append(ring)
                    innerlistgeomtuple = []
            innerlistgeomtuple3 = []
            if innerlistgeomtuple2:
                all_rings_connected_i = checkrings_connected(innerlistgeomtuple2, r)
            if not innerlistgeomtuple2:
                all_rings_connected_i = checkrings_connected(innerlistgeomtuple, r)
            if innerlistgeomtuple and not all_rings_connected_i:
                innerlistgeomtuple2 = innerlistgeomtuple                                     
                innerlistgeomtuple3.append(innerlistgeomtuple2[0])
                startgeom = innerlistgeomtuple2[0][0]
                for ridx in range(0,len(innerlistgeomtuple2)):
                    next_ring = innerlistgeomtuple3[-1][-1]
                    if next_ring == startgeom and ridx < len(innerlistgeomtuple2)-1:
                        next_ring = innerlistgeomtuple2[len(innerlistgeomtuple3)][-1]
                        startgeom = next_ring
                    idx_next_ring = lfindgetsingleidx(innerlistgeomtuple2, next_ring, ridx)                            
                    try:
                        if innerlistgeomtuple2[idx_next_ring[0]] not in innerlistgeomtuple3:
                            if innerlistgeomtuple2[idx_next_ring[0]][-1] == innerlistgeomtuple3[-1][-1]:
                                innerlistgeomtuple2[idx_next_ring[0]].reverse()
                            innerlistgeomtuple3.append(innerlistgeomtuple2[idx_next_ring[0]])    
                        rngitn_i = True      
                    except:
                        continue
            if rngitn_i:
                innerlistgeomtuple4 = []
                innerlistgeomtuple4 = merge_sublist_items(innerlistgeomtuple3)
                rings = detect_rings(innerlistgeomtuple4)
                if len(rings) > 1:
                    rings = [l_ordered_remove_duplicates(rng) for rng in rings]
                    all_rings_closed_i = checkrings_closed(rings,r)
                else:
                    innerlistgeomtuple3 = l_ordered_remove_duplicates(innerlistgeomtuple4)
                    all_rings_closed_i = checkrings_closed([innerlistgeomtuple3],r)
            if innerlistgeomtuple and rngitn_i and all_rings_closed_i:
                innerlistgeomtuple2 = []
                all_rings_connected_i = True
                if len(rings) < 2:
                    innerlistgeomtuple2.append([])
                    innerlistgeomtuple2[0] = innerlistgeomtuple3
                else:
                    innerlistgeomtuple2 = rings
           
            outerlistgeomtuple = [[(x['lon'],x['lat']) for x in ol['geometry']] for ol in outerlist]
            if len(outerlistgeomtuple) > 1:
                all_rings_connected_o = checkrings_connected(outerlistgeomtuple, r)
                if all_rings_connected_o:
                    for ring in outerlistgeomtuple:
                        outerlistgeomtuple2+=ring
                    outerlistgeomtuple = []
                    outerlistgeomtuple.append(l_ordered_remove_duplicates(outerlistgeomtuple2))
                    outerlistgeomtuple2 = outerlistgeomtuple
                    outerlistgeomtuple = []
            all_rings_closed_o = checkrings_closed(outerlistgeomtuple, r)
            if all_rings_closed_o:
                for ring in outerlistgeomtuple:
                    outerlistgeomtuple2.append(ring)
                    outerlistgeomtuple = []
            outerlistgeomtuple3 = []
            if outerlistgeomtuple2:
                all_rings_connected_o = checkrings_connected(outerlistgeomtuple2, r)
            if not outerlistgeomtuple2:
                all_rings_connected_o = checkrings_connected(outerlistgeomtuple, r)
            if not all_rings_connected_o:
                outerlistgeomtuple2 = outerlistgeomtuple
                outerlistgeomtuple3.append(outerlistgeomtuple2[0])
                startgeom = outerlistgeomtuple2[0][0]
                for ridx in range(0,len(outerlistgeomtuple2)):
                    next_ring = outerlistgeomtuple3[-1][-1]
                    if next_ring == startgeom and ridx < len(outerlistgeomtuple2)-1:
                        next_ring = outerlistgeomtuple2[len(outerlistgeomtuple3)][-1]
                        startgeom = next_ring
                    idx_next_ring = lfindgetsingleidx(outerlistgeomtuple2, next_ring, ridx)
                    try:
                        if outerlistgeomtuple2[idx_next_ring[0]] not in outerlistgeomtuple3:
                            if outerlistgeomtuple2[idx_next_ring[0]][-1] == outerlistgeomtuple3[-1][-1]:
                                outerlistgeomtuple2[idx_next_ring[0]].reverse()
                            outerlistgeomtuple3.append(outerlistgeomtuple2[idx_next_ring[0]])    
                        rngitn_o = True                     
                    except:
                        continue
            if rngitn_o:
                outerlistgeomtuple4 = []
                outerlistgeomtuple4 = merge_sublist_items(outerlistgeomtuple3)
                rings = detect_rings(outerlistgeomtuple4)
                if len(rings) > 1:
                    rings = [l_ordered_remove_duplicates(rng) for rng in rings]
                    all_rings_closed_o = checkrings_closed(rings,r)
                else:
                    outerlistgeomtuple3 = outerlistgeomtuple4
                    outerlistgeomtuple3 = l_ordered_remove_duplicates(outerlistgeomtuple4)
                    all_rings_closed_o = checkrings_closed([outerlistgeomtuple3],r)
                if outerlistgeomtuple and rngitn_o and all_rings_closed_o:
                    outerlistgeomtuple2 = []
                    all_rings_connected_o = True
                if len(rings) < 2:
                    outerlistgeomtuple2.append([])
                    outerlistgeomtuple2[0] = outerlistgeomtuple3
                else:
                    outerlistgeomtuple2 = rings                   
            
            if innerlistgeomtuple or innerlistgeomtuple2:
                innerlistgeomtuple = innerlistgeomtuple2
            if outerlistgeomtuple2:
                outerlistgeomtuple = outerlistgeomtuple2   
            
            l_polygon_rings = []    
            for subelement in range(len(outerlistgeomtuple)):
                ncoordsouter = [(n[0],n[1]) for n in outerlistgeomtuple[subelement]]
                temppolyarea = Polygon({"rings": [ncoordsouter], "spatialReference": {"wkid": 4326}}).area
                if temppolyarea < 0.0:
                    ncoordsouter.reverse()
                if ncoordsouter:
                    l_polygon_rings.append(ncoordsouter)           
            
            for subelement in range(len(innerlistgeomtuple)):
                if innerlistgeomtuple[subelement]:
                    ncoordsinner = [(n[0],n[1]) for n in innerlistgeomtuple[subelement]]
                    temppolyarea = Polygon({"rings": [ncoordsinner], "spatialReference": {"wkid": 4326}}).area
                    if temppolyarea > 0.0:
                        ncoordsinner.reverse()
                    if ncoordsinner:
                        l_polygon_rings.append(ncoordsinner)     

            poly = Polygon({"rings": l_polygon_rings, "spatialReference": {"wkid": 4326}})
            valid_list.append([poly.is_valid,r['id']])

            if poly.is_valid:
                geo_dict_r['geo'].append(poly)
                val_dict_r['osm_id'].append(str(r['id']))
                val_dict_r['timestamp'].append(dt.strptime(r['timestamp'],'%Y-%m-%dT%H:%M:%SZ'))

            # Populate Relation tags
            for tag in [key for key in val_dict_r.keys() if key not in ['osm_id','timestamp'] and key not in excludedattributes]:
                val_dict_r[tag].append(r['tags'].get(str(tag),''))

        except Exception as ex:
            tb = traceback.format_exc()
            print('Relation ID {0} Raised Exception: {1}'.format(r['id'], str(tb)))

    # Dictionary For Incoming Way Tags
    for w in ways:
        w_tags = w['tags'].keys()
        for tag in w_tags:
            if tag not in val_dict_w.keys() and tag not in excludedattributes:
                tagname = tag
                val_dict_w[tagname] = []
    
    print('Constructing simple polygons...')
    p=0
    pbar = createpbar(len(ways))
    # Build Lists
    for w in ways:
        try:
            p = updatepbar(p, pbar)
            # Populate Tags
            for tag in [key for key in val_dict_w.keys() if key not in ['osm_id','timestamp'] and key not in excludedattributes]:
                val_dict_w[tag].append(w['tags'].get(str(tag),''))
            # Populate Geometries & IDs
            coords = [[e['lon'], e['lat']] for e in w.get('geometry')]
            poly = Polygon({"rings":  [coords], "spatialReference": {"wkid": 4326}})
            geo_dict_w['geo'].append(poly)
            val_dict_w['osm_id'].append(str(w['id']))
            val_dict_w['timestamp'].append(dt.strptime(w['timestamp'],'%Y-%m-%dT%H:%M:%SZ'))


        except Exception as ex:
            print('Way ID {0} Raised Exception: {1}'.format(w['id'], str(ex)))

    try:
        val_dict = merge_dict_lists(val_dict_r, val_dict_w)
        val_dict = {k: v for k, v in val_dict.items() if v is not None}
        geo_dict = geo_dict_r['geo']+geo_dict_w['geo']
        len(valid_list)
        return SpatialDataFrame(val_dict, geometry=geo_dict)

    except TypeError:
        raise Exception('Ensure ArcPy is Included in Python Interpreter')    

def build_ways_sdf_toline(o_response, excludedattributes):
    '''
    Function to convert returned OSM polyline data to Esri SpatialDataFrame.
    Returns an ESRI SpatialDataFrame.
    @param o_response: The valid response data from the OSM server containing the way elements
    @param excludedattributes: The attributes exluded in the configuration file osmconfig.json
    '''
    # Extract Relevant Way Elements from OSM Response
    ways = [e for e in o_response if e['type'] == 'way' and e['nodes'][0] != e['nodes'][-1]]

    # Dictionary For Geometries & IDs
    geo_dict = {'geo': []}
    val_dict = {'osm_id': [], 'timestamp': []}  

    # Dictionary For Incoming Tags
    for w in ways:
        w_tags = w['tags'].keys()
        for tag in w_tags:
            if tag not in val_dict.keys() and tag not in excludedattributes:
                tagname = tag
                val_dict[tagname] = []
    
    print('Constructing lines...')
    p=0
    pbar = createpbar(len(ways))
    # Build Lists
    for w in ways:
        try:
            p = updatepbar(p, pbar)
            # Populate Tags
            for tag in [key for key in val_dict.keys() if key not in ['osm_id','timestamp'] and key not in excludedattributes]:
                val_dict[tag].append(w['tags'].get(str(tag),''))

            # Populate Geometries & IDs
            coords = [[e['lon'], e['lat']] for e in w.get('geometry')]
            poly = Polyline({"paths": [coords], "spatialReference": {"wkid": 4326}})

            geo_dict['geo'].append(poly)
            val_dict['osm_id'].append(str(w['id']))
            val_dict['timestamp'].append(dt.strptime(w['timestamp'],'%Y-%m-%dT%H:%M:%SZ'))

        except Exception as ex:
            print('Way ID {0} Raised Exception: {1}'.format(w['id'], str(ex)))

    try:
        geo_dict = geo_dict['geo']
        val_dict = {k: v for k, v in val_dict.items() if v is not None}
        return SpatialDataFrame(val_dict, geometry=geo_dict)

    except TypeError:
        raise Exception('Ensure ArcPy is Included in Python Interpreter')
            

def fields_cleaner(b_sdf):
    '''
    Optional function to cleanup fields, where 99% of the data contains 'Null' values.
    Returns an ESRI SpatialDataFrame. Currently not applied in this version of the module.
    @param b_sdf: The ESRI Spatial DataFrame to be cleaned from 99% empty fields.
    '''

    # Set Cutoff & Collect Field List
    cutoff = int(len(b_sdf) * .99)
    f_list = list(b_sdf)

    # Flag Fields Where >= 99% of Data is Null
    fields = []
    for f in f_list:
        try:
            if b_sdf[f].dtype == 'object' and f != 'SHAPE':
                null_count = b_sdf[f].value_counts().get('Null', 0)
                if null_count >= cutoff:
                    fields.append(f)
        except:
            print('Cannot Determine Null Count for Field {0}'.format(str(f)))
            continue

    # Drop Flagged Fields & Return
    if fields:
        b_sdf.drop(fields, axis=1, inplace=True)
        return b_sdf

    else:
        return b_sdf