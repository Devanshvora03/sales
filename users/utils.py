import requests
api_key = '8d8ef6c164aca6753bfa6dde97e28667'

def get_distance(lat1,lon1,lat2,lon2):
    url = f'https://apis.mapmyindia.com/advancedmaps/v1/8d8ef6c164aca6753bfa6dde97e28667/route_adv/driving/{lon1},{lat1};{lon2},{lat2}'
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        # Extract distance information from the response
        distance_in_meters = data['routes'][0]['distance']/1000
        print("Coordinates are : " , lat1 , lon1 , lat2 , lon2 , sep= '-') 
        print("Distances are",distance_in_meters)
        return distance_in_meters
    else:
        print(f"Error: {response.status_code}")
        return None