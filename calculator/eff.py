import urllib, json, math, random, time

# coord_list cannot exceed 8 in length due to Google Maps API restrictions.
def road_dist(coord_list):
    BASE_URL = 'http://dev.virtualearth.net/REST/V1/Routes/Driving?'
    place_args = {'key':'At0amIrddUlTB6v55LmH0IeDw35TqiqyiHueMFlotBLuVbM6Tz3xXFcfV013IW9W'}
    for (i, coord) in enumerate(coord_list):
        place_args['wp.' + str(i)] = str(coord[0]) + ',' + str(coord[1])
    url = BASE_URL + urllib.urlencode(place_args)
    result = json.load(urllib.urlopen(url))
    leg_dist = []
    try:
        route = result['resourceSets'][0]['resources'][0]
    except IndexError:
        raise IndexError(result['statusDescription'])
    else:
        for leg in route['routeLegs']:
            leg_dist.append(leg['travelDistance'] * 1000)
        return leg_dist # meters

def crow_dist(coord_list):
    leg_dist = []
    for i in xrange(len(coord_list)-1):
        leg_dist.append(distance((coord_list[i], coord_list[i+1])))
    return leg_dist #meters

# Uses Haversine's formula to calculate distance between two points.
def distance((coord1, coord2)):
    lat_s = math.radians(coord1[0])
    lng_s = math.radians(coord1[1])
    lat_f = math.radians(coord2[0])
    lng_f = math.radians(coord2[1])
    delta_lat = lat_f - lat_s
    delta_lng = lng_f - lng_s
    a = (math.sin(delta_lat/2))**2 + math.cos(lat_s)*math.cos(lat_f)*(math.sin(delta_lng/2))**2
    return 2 * 6371009 * math.asin(math.sqrt(a)) # 6371009 = Earth's radius

# Takes in a top right coordinate and bottom left coordinate and outputs random point within range.

def random_coord(boundbox):
    nw = boundbox[0]
    se = boundbox[1]
    lat = random.uniform(se[0], nw[0])
    lng = random.uniform(se[1], nw[1])
    return (lat, lng)

# Returns (bbox, center, name) of city.
def get_city_bounds_and_center(city):
    BASE_URL = 'http://dev.virtualearth.net/REST/v1/Locations?'
    url_args = {}
    '''if city.count(',') == 1:
        locality, adminDistrict = city.split(',')
        url_args['adminDistrict'] = adminDistrict
    else:
        locality = city'''
    #url_args['locality'] = locality
    url_args['query'] = city
    url_args['key'] = 'At0amIrddUlTB6v55LmH0IeDw35TqiqyiHueMFlotBLuVbM6Tz3xXFcfV013IW9W'
    url = BASE_URL + urllib.urlencode(url_args)
    result = json.load(urllib.urlopen(url))
    try:
        geodata = result['resourceSets'][0]['resources'][0]
    except IndexError:
        raise IOError(result['status'])
    else:
        nw = (geodata['bbox'][0], geodata['bbox'][1])
        se = (geodata['bbox'][2], geodata['bbox'][3])
        center = (geodata['point']['coordinates'][0],
                  geodata['point']['coordinates'][1])
        city_name = geodata['name']
        return ((nw, se), center, city_name)

# Computes the straight to driving distance ratio for <num_points> points.
def compute_points(city, num_points): # num_points should be < 25
    boundbox = get_city_bounds_and_center(city)[0]
    coord_list = [random_coord(boundbox) for i in xrange(num_points)]
    for i in xrange(20, 0, -1):
        try:
            return efficiency(coord_list)
        except IndexError:
            if i == 1:
                raise IndexError()
            else:
                #print "Failed to get road distances from Bing. Retrying..."
                coord_list = [random_coord(boundbox) for i in xrange(num_points)]
        except ZeroDivisionError:
            if i == 1:
                raise IndexError()
            else:
                coord_list = [random_coord(boundbox) for i in xrange(num_points)]

#Iterates above function <iterations> times.                
def compute_lots(city, num_points, iterations):
    efficiencies = []
    for i in xrange(iterations):
        efficiencies.append(compute_points(city, num_points))
        #print str(len(efficiencies)-1) + ": " + str(efficiencies[-1])
    return sum(efficiencies)/len(efficiencies)

def stdev(l):
    mean = sum(l)/len(l)
    return math.sqrt(sum([(x-mean)**2 for x in l])/(len(l)-1))

def efficiency(coord_list):
    crow_list = crow_dist(coord_list)
    try:
        road_list = road_dist(coord_list)
    except IndexError:
        raise IndexError()
    else:
        if len(crow_list) != len(coord_list)-1 or len(crow_list) != len(coord_list)-1:
            raise IndexError("List length mismatch!")
        else:
            efficiency_list = []
            for i in xrange(len(crow_list)):
                if road_list[i] != 0 and crow_list[i]/road_list[i] < 1:
                    efficiency_list.append(crow_list[i]/road_list[i])
            avg_eff = sum(efficiency_list)/len(efficiency_list)
            if avg_eff > 1: # Sometimes occurs when endpoints are too close.
                print "Crow list: " + str(crow_list)
                print "Road List: " + str(road_list)
                print "Coord List: " + str(coord_list)
                raise RuntimeError()
            else:
                return avg_eff
