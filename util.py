import math, re
from itertools import chain, combinations

num_vehicles = 4
vehicles = range(num_vehicles)


# Calculate the distance between to points
def distance_calc(point_1, point_2):
    return math.sqrt((point_1['latitude']-point_2['latitude'])**2+(point_1['longitude']-point_2['longitude'])**2)


# Generate a power set
def power_set(dataset):
    return chain.from_iterable(combinations(list, r+1) for r in range(len(dataset)))


# Extract all numbers from any string
def extract_numbers(var):
    coords = re.findall(r'\d+', var)
    for x in range(len(coords)):
        coords[x] = int(coords[x])
    return coords


# Display a route based off of routing variables
def disp_route(variables, origin_id, distances):
    routes = {}
    for var in variables:
        if var.varValue == 1:
            data = extract_numbers(var.name)
            (start, end, vehicle) = (data[0], data[1], data[2])
            if vehicle not in routes:
                routes[vehicle] = [start, end]
            elif routes[vehicle][-1] == start and start != origin_id:
                routes[vehicle].append(end)
            elif routes[vehicle][0] == end and end != origin_id:
                route_num = [start]
                for point in routes[vehicle]:
                    route_num.append(point)
                routes[vehicle] = route_num
            else:
                variables.append(var)
    total_distance = 0
    for route_num in routes:
        distance = 0
        route = routes[route_num]
        for x in range(len(route) - 1):
            distance += distances[(route[x], route[x + 1])]
        total_distance += distance
        print("Route %d: %s total distance: %f" % (route_num, str(route), distance))
    print("Total distance of all routes: %f" % total_distance)




