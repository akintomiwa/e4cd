import csv
import random

# def nest_charging_stations(csv_file):
#     nested_dict = {}
    
#     with open(csv_file, newline='') as csvfile:
#         reader = csv.DictReader(csvfile)
        
#         for row in reader:
#             route = row['Route']
#             station = row['Station']
#             cpid = row['CPID']
#             power = int(row['Power'])
#             distance = int(row['Distance'])
#             price = float(row['Price'])
#             green = bool(int(row['Green']))
#             booking = bool(int(row['Booking']))
            
#             if route not in nested_dict:
#                 nested_dict[route] = {}
                
#             if station not in nested_dict[route]:
#                 nested_dict[route][station] = {}
                
#             nested_dict[route][station]['CPID'] = cpid
#             nested_dict[route][station]['Power'] = power
#             nested_dict[route][station]['Distance'] = distance
#             nested_dict[route][station]['Price'] = price
#             nested_dict[route][station]['Green'] = green
#             nested_dict[route][station]['Booking'] = booking
            
#     return nested_dict 



def read_csv(filename):
    """Reads a CSV file and returns a dictionary of dictionaries of dictionaries."""
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
    """Returns a list of charging stations for the specified route."""
    if route_name not in param_dict:
        return f"No charging stations found for route {route_name}."
    stations = param_dict[route_name]
    num_stations = len(stations)
    return num_stations

def count_total_charging_stations(nested_dict):
    """Returns a dictionary of the number of charging stations for each route."""
    station_counts = {}
    for route, stations in nested_dict.items():
        num_stations = len(stations)
        station_counts[route] = num_stations
    return station_counts

def sum_total_charging_stations(nested_dict):
    """Returns the total number of charging stations for all routes."""
    station_counts = {}
    for route, stations in nested_dict.items():
        num_stations = len(stations)
        station_counts[route] = num_stations
    return sum(station_counts.values())

def get_routes(charging_stations):
    """Returns a list of routes."""
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

# unused
def get_charging_stations_on_route(stations_dict, route_name):
    """Returns a list of charging stations for the specified route."""
    route_stations = []
    for key in stations_dict:
        if route_name in key:
            route_stations.extend(stations_dict[key])
    return route_stations

# unused
def charging_stations_on_route_reverse(route_dict, route_name):
    """Returns a reversed list of charging stations for the specified route."""
    charging_stations = []
    if route_name in route_dict:
        for charging_station in route_dict[route_name].values():
            charging_stations.extend(charging_station)
        charging_stations = list(reversed(charging_stations))
    return charging_stations

# unused
def find_cpid_for_charging_station(cs_dict, cpid):
    """Returns a list of CPIDs for the specified charging station."""
    for cs_id, cs_info in cs_dict.items():
        if cs_info['Station Name'] == cpid:
            return [cp for cp in cs_info['CPIDs']]
    return []

# unused
def get_route_cps(route_name, cp_dict):
    """Returns a list of CPIDs for the specified route."""
    cps = []
    for cp in cp_dict[route_name].values():
        cps.append(cp['CPID'])
    return cps

# unused
# def get_checkpoint_list(route_dict, route_name):
#     """Returns a list of checkpoints for the specified route."""
#     route_stations = route_dict.get(route_name)  # Get the dictionary of charging stations for the specified route
#     if route_stations is None:
#         raise ValueError(f"No such route: {route_name}")
    
#     distances = [station['Distance'] for station in route_stations.values()]  # Extract the distance attribute of each charging station
#     checkpoints = [sum(distances[:i+1]) for i in range(len(distances))]  # Calculate the running total of distances
#     return checkpoints

# unused
# def get_checkpoints(route, data):
#     cs_data = data[route]
#     cp_list = []
#     dist = 0
    
#     for cp in cs_data:
#         cp_data = cs_data[cp]
#         dist += cp_data['Distance']
#         cp_list.append((cp_data['CPID'], dist))
    
#     return cp_list





# 24/03/2023

def get_charge_points(route_name, data_dict):
    charge_points = []
    for station in data_dict.keys():
        if route_name in data_dict[station]['route']:
            charge_points.append(data_dict[station]['charge_points'])
    return charge_points


def get_charge_points_2(route_name, data):
    charge_points = []
    for station in data[route_name]:
        for key in station:
            if key.startswith('CS_' + route_name):
                charge_points.append(station[key])
    return charge_points

def charge_points_on_route(route_name, data_dict):
    # Find all charge stations on the given route
    charge_stations = [station for station, routes in data_dict.items() if route_name in routes]
    
    # Get the number of charge points for each charge station
    num_charge_points = [data_dict[station]['charge_points'] for station in charge_stations]
    
    return num_charge_points


def get_charge_points_per_station(route_name, data_dict):
    charge_points = []
    for key, value in data_dict.items():
        if value['Route'] == route_name:
            charge_points.append(sum([int(v['Power']) for k, v in data_dict.items() if v['Station'] == value['Station']]))
    return charge_points


def num_stations_per_route(charging_data):
    num_stations = {}
    for route, stations in charging_data.items():
        num_stations[route] = len(stations)
    return num_stations

def get_stations_for_route(route_name, charging_data):
    stations = []
    for route in charging_data:
        if route['Route'] == route_name:
            for station in route['Stations']:
                stations.append(station['Station'])
            break
    return stations

# =======


def read_charging_stations(csv_file):
    charging_stations = []

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            charging_stations.append(row)

    return charging_stations


# =======


def read_charging_data(file_path):
    charging_data = {}
    with open(file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            route = row['Route']
            station = row['Station']
            cpid = row['CPID']
            power = int(row['Power'])
            distance = int(row['Distance'])
            price = int(row['Price'])
            green = bool(int(row['Green']))
            booking = bool(int(row['Booking']))
            if route not in charging_data:
                charging_data[route] = {}
            if station not in charging_data[route]:
                charging_data[route][station] = []
            charging_data[route][station].append({
                'CPID': cpid,
                'Power': power,
                'Distance': distance,
                'Price': price,
                'Green': green,
                'Booking': booking
            })
    return charging_data


def get_charge_points_per_station_on_route(data, route_name):
    charge_points_per_station = {}
    for route in data:
        if route['Route'] == route_name:
            for station in data[route]['Stations']:
                cp_count = len(data[route]['Stations'][station]['Charge Points'])
                charge_points_per_station[station] = cp_count
    return charge_points_per_station


def count_charge_points_by_station(data, route_name):
    charge_stations = {}
    for route, stations in data.items():
        if route == route_name:
            for station, charge_points in stations.items():
                charge_stations[station] = len(charge_points)
    return charge_stations

# # not working well 
def get_route_from_config(route_id: str, station_config:dict) -> dict:
    route_dict = {}
    try:
        for station_id in station_config[route_id]:
            for cs in station_config[route_id][station_id]:
                if route_dict.get(cs['Distance']):
                    route_dict[cs['Distance']].append(cs)
                else:
                    route_dict[cs['Distance']] = [cs]
        return route_dict
    except KeyError:
        return None

def get_distances_along_route(station_config, route_name):
    """
    Returns a list of distance values for each charging station along the named route.

    Args:
    station_config: dictionary containing the configuration of charging stations and charge points.
    route_name: string representing the name of the route.

    Returns:
    A list of distance values for each charging station along the named route.
    """
    distances = []
    for station, values in station_config.items():
        if route_name in values['routes']:
            distances.append(values['distance'])
    return distances



# general
def get_dict_values(d):
    """
    Returns a list containing the associated values for each key in the dictionary.
    """
    return list(d.values())

def cumulative_cs_distances(numbers):
    result = []
    for i in range(len(numbers)):
        if i == 0:
            result.append(numbers[i])
        else:
            result.append(numbers[i] + result[i-1])
    return result


# used - for CS agents

def select_route_as_key(input):
    """
    This function returns one of the keys in input dictionary, up to the integer value of the key
    """
    # calculate the sum of values in the input dictionary
    n = sum(input.values())
    
    # create a dictionary to keep track of the number of times each key is returned
    counter = {key: 0 for key in input}
    
    # select a key and return it as a string
    def helper():
        for key in input:
            if counter[key] < input[key]:
                counter[key] += 1
                return str(key)
        # if all keys have been returned the maximum number of times, raise an exception
        raise Exception('no more route assignments')
    
    # keep track of the number of times the function has been run
    num_runs = 0
    
    # run the function at most n times
    while num_runs < n:
        try:
            key = helper()
            num_runs += 1
            yield key
        except Exception as e:
            yield str(e)
            return

# works okay
# def remove_list_item_random(lst):
#     """
#     Removes a random item from the given list without replacement.
    
#     Parameters:
#     lst (list): The list to remove an item from.
    
#     Returns:
#     The removed item.
#     """
#     if len(lst) == 0:
#         raise ValueError("Cannot remove an item from an empty list.")
    
#     idx = random.randrange(len(lst))
#     return lst.pop(idx)


def remove_list_item_seq(lst):
    """
    Removes the first item from the given list.
    
    Parameters:
    lst (list): The list to remove an item from.
    
    Returns:
    The removed item.
    """
    if len(lst) == 0:
        raise ValueError("Cannot remove an item from an empty list.")
    
    return lst.pop(0)


def set_lists(self, lst, n) -> None:
    """
    Sets the given list of attributes to empty lists. 
    Accepts an integer n and a list of strings. 
    This function creates an n number of class attributes named as each string in the list, and initialised as empty lists
    
    """
    for s in lst:
        setattr(self, s, [])
        for  i in range(n):
            getattr(self, s).append(None)


# 29/03/2023

# # modify for cp charge rating extraction.
# def get_distance_values(station_config, route_name):
#     """Returns a list of all distance values, for every CP on a given route."""
#     distance_values = []
#     for station in station_config[route_name]:
#         for charger in station_config[route_name][station]:
#             distance_values.append(int(charger['Distance']))
#     return distance_values

def get_charging_stations_along_route(station_config, route_name):
    """
    Returns a dictionary of charging stations distances along the route. 
    The key is the station name and the value is the distance from the start of the route.   
    """
    charging_stations = {}
    route_stations = station_config.get(route_name)
    if route_stations:
        for station_name, station_data in route_stations.items():
            for station in station_data:
                charging_stations[station_name] = int(station['Distance'])
    return charging_stations