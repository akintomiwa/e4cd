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

# def count_charging_stations(param_dict, target_route):
#     station_counts = {}
#     for route, stations in param_dict.items():
#         num_stations = len(stations)
#         station_counts[route] = num_stations
#     return station_counts