import csv

def nest_charging_stations(csv_file):
    nested_dict = {}
    
    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            route = row['Route']
            station = row['Station']
            cpid = row['CPID']
            power = int(row['Power'])
            distance = int(row['Distance'])
            price = float(row['Price'])
            green = bool(int(row['Green']))
            booking = bool(int(row['Booking']))
            
            if route not in nested_dict:
                nested_dict[route] = {}
                
            if station not in nested_dict[route]:
                nested_dict[route][station] = {}
                
            nested_dict[route][station]['CPID'] = cpid
            nested_dict[route][station]['Power'] = power
            nested_dict[route][station]['Distance'] = distance
            nested_dict[route][station]['Price'] = price
            nested_dict[route][station]['Green'] = green
            nested_dict[route][station]['Booking'] = booking
            
    return nested_dict 

def read_csv(filename):
    data = {}
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            route = row['Route']
            station = row['Station']
            cpid = row['CPID']
            power = row['Power']
            distance = row['Distance']
            price = row['Price']
            green = row['Green']
            booking = row['Booking']
            if route not in data:
                data[route] = {}
            if station not in data[route]:
                data[route][station] = []
            data[route][station].append({
                'CPID': cpid,
                'Power': power,
                'Distance': distance,
                'Price': price,
                'Green': green,
                'Booking': booking
            })
    return data


def get_target_charging_stations(route_name, param_dict):
    if route_name not in param_dict:
        return f"No charging stations found for route {route_name}."
    stations = param_dict[route_name]
    num_stations = len(stations)
    print(f"Route {route_name} has {num_stations} charging stations.")
    return num_stations

def get_target_charging_stations(route_name, param_dict):
    if route_name not in param_dict:
        return f"No charging stations found for route {route_name}."
    stations = param_dict[route_name]
    num_stations = len(stations)
    return num_stations

def count_total_charging_stations(nested_dict):
    station_counts = {}
    for route, stations in nested_dict.items():
        num_stations = len(stations)
        station_counts[route] = num_stations
    return station_counts

def sum_total_charging_stations(nested_dict):
    station_counts = {}
    for route, stations in nested_dict.items():
        num_stations = len(stations)
        station_counts[route] = num_stations
    return sum(station_counts.values())

def get_routes(charging_stations):
    routes = []
    for key in charging_stations.keys():
        routes.append(key)
    return routes

def total_route_length(route_dict, route_name):
    """Returns the total length of the specified route by summing the distance of all charging stations."""
    route_stations = route_dict.get(route_name)  # Get the dictionary of charging stations for the specified route
    if route_stations is None:
        raise ValueError(f"No such route: {route_name}")
    total_distance = sum(station['Distance'] for station in route_stations.values())  # Sum the distance attribute of each charging station
    return total_distance

# def cpids_for_route(route_dict, route_name):
#     """Returns a list of CPIDs for the specified route."""
#     route_stations = route_dict.get(route_name)  # Get the dictionary of charging stations for the specified route
#     if route_stations is None:
#         raise ValueError(f"No such route: {route_name}")
#     cpids = [station['CPID'] for station in route_stations.values()]  # Extract the CPID attribute of each charging station
#     return cpids

def get_charging_stations_on_route(stations_dict, route_name):
    route_stations = []
    for key in stations_dict:
        if route_name in key:
            route_stations.extend(stations_dict[key])
    return route_stations

def charging_stations_on_route_reverse(route_dict, route_name):
    charging_stations = []
    if route_name in route_dict:
        for charging_station in route_dict[route_name].values():
            charging_stations.extend(charging_station)
        charging_stations = list(reversed(charging_stations))
    return charging_stations

# works but not sure if it's the best way
# def charging_stations_on_route_reverse_2(route_dict, route_name):
#     charging_stations = []
#     if route_name in route_dict:
#         for charging_station in route_dict[route_name].values():
#             charging_stations.extend(charging_station)
#         charging_stations = list(reversed(charging_stations))
#     return charging_stations

def find_cpid_for_charging_station(cs_dict, cpid):
    for cs_id, cs_info in cs_dict.items():
        if cs_info['Station Name'] == cpid:
            return [cp for cp in cs_info['CPIDs']]
    return []


def get_route_cps(route_name, cp_dict):
    cps = []
    for cp in cp_dict[route_name].values():
        cps.append(cp['CPID'])
    return cps

def get_checkpoint_list(route_dict, route_name):
    """Returns a list of checkpoints for the specified route."""
    route_stations = route_dict.get(route_name)  # Get the dictionary of charging stations for the specified route
    if route_stations is None:
        raise ValueError(f"No such route: {route_name}")
    
    distances = [station['Distance'] for station in route_stations.values()]  # Extract the distance attribute of each charging station
    checkpoints = [sum(distances[:i+1]) for i in range(len(distances))]  # Calculate the running total of distances
    return checkpoints

# unused
def get_checkpoints(route, data):
    cs_data = data[route]
    cp_list = []
    dist = 0
    
    for cp in cs_data:
        cp_data = cs_data[cp]
        dist += cp_data['Distance']
        cp_list.append((cp_data['CPID'], dist))
    
    return cp_list


# def count_charging_stations(param_dict, target_route):
#     station_counts = {}
#     for route, stations in param_dict.items():
#         num_stations = len(stations)
#         station_counts[route] = num_stations
#     return station_counts


# doesnt work for some reason
# def charge_points_on_route(route_name, charging_stations):
#     route_stations = charging_stations.get(route_name, {})
#     charge_points = [station.get('charge_points', 0) for station in route_stations.values()]
#     return charge_points
