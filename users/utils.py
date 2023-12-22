from geopy.distance import distance

def get_distance(lat1, lon1,lat2,lon2):
    coords_1 = (lat1, lon1)
    coords_2 = (lat2, lon2)
    distance = distance(coords_1, coords_2).km
    return distance

