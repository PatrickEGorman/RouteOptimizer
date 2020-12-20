from mip import *
from map import Map
from util import vehicles, num_vehicles
import time
import matplotlib.pyplot as plt
import pandas as pd

time_1 = time.perf_counter()

map_1 = Map("Result_1.json")
distances = map_1.distances
points = map_1.points
origin_id = map_1.origin_id

# Declare model
m = Model(sense=MINIMIZE, solver_name=CBC)
m.max_gap = 0.1

path = {}
for dist_key in distances:
    for vehicle in vehicles:
        path[dist_key[0], dist_key[1], vehicle] = m.add_var(var_type=BINARY)

# max_path = m.add_var(var_type=CONTINUOUS)
avg_distance = m.add_var(var_type=CONTINUOUS)
vehicle_distance = {}
for vehicle in vehicles:
    vehicle_distance[vehicle] = m.add_var(var_type=CONTINUOUS)

all_points = points.copy()
all_points.append(origin_id)

order = {}
for point in all_points:
    for vehicle in vehicles:
        order[point, vehicle] = m.add_var(var_type=INTEGER)


# set objective to minimize max path
m.objective = avg_distance
m += avg_distance - xsum(path[point_1, point_2, vehicle] * distances[(point_1, point_2)] / num_vehicles
                         for (point_1, point_2, vehicle) in path) == 0


for point in points:
    point_time = time.perf_counter()
    print("Setting constraints for point %d at %f seconds" % (point, (point_time-time_1)))
    points_exclude = all_points.copy()
    points_exclude.remove(point)
    m += xsum(path[point, point_2, vehicle] for (point_1, point_2, vehicle) in path if point == point_1) == 1
    m += xsum(path[point_2, point, vehicle] for (point_2, point_1, vehicle) in path if point == point_1) == 1
    for vehicle in vehicles:
        m += xsum(path[point, point_2, vehicle] - path[point_3, point, vehicle]
                  for (point_1, point_2, vehicle_num) in path if point == point_1 and vehicle == vehicle_num
                  for (point_3, point_4, vehicle_num_2) in path if point == point_4 and vehicle == vehicle_num_2) == 0

for vehicle in vehicles:
    vehicle_time = time.perf_counter()
    print("Setting constraints for vehicle %d at %f seconds" % (vehicle, (vehicle_time-time_1)))
    # m += max_path - xsum(path[point_1, point_2, vehicle]*distances[(point_1, point_2)] for point_1 in all_points
    #                      for point_2 in all_points if point_1 != point_2) >= 0
    m += vehicle_distance[vehicle] - xsum(path[point_1, point_2, vehicle]*distances[(point_1, point_2)]
                                          for (point_1, point_2, vehicle_num) in path if vehicle == vehicle_num) == 0
    m += vehicle_distance[vehicle] - avg_distance / 2 >= 0
    m += vehicle_distance[vehicle] - 2 * avg_distance <= 0
    m += xsum(path[origin_id, point_1, vehicle] for (origin, point_1, vehicle_num) in path
              if origin == origin_id and vehicle_num == vehicle) == 1
    m += xsum(path[point_1, origin_id, vehicle] for (point_1, origin, vehicle_num) in path
              if origin == origin_id and vehicle_num == vehicle) == 1

# continuity constraint
for vehicle in vehicles:
    m += order[origin_id, vehicle] == 1
    for point_1 in all_points:
        cont_time = time.perf_counter() - time_1
        print("Setting continuity constraints for vehicle %d and point %d at %f seconds"%(vehicle, point_1, cont_time))
        m += order[point_1, vehicle] >= 1
        for point_2 in points:
            if (point_1, point_2, vehicle) in path:
                m += order[point_1, vehicle] - order[point_2, vehicle] + (len(points)+1) * \
                     path[point_1, point_2, vehicle] <= len(points)


# Constrain origin to have 1 in and out route for each vehicle
m += xsum(path[origin_id, point, vehicle] for (origin, point, vehicle) in path if origin == origin_id) == num_vehicles
m += xsum(path[point, origin_id, vehicle] for (point, origin, vehicle) in path if origin == origin_id) == num_vehicles

time_2 = time.perf_counter()
print("Launching solver at time %f" % (time_2-time_1))

# Solve integer program
status = m.optimize(max_seconds=300)


# Display a route based off of routing variables and return routes dictionary
def disp_route(variables, routes=None):
    if routes is None:
        routes = {}
    variables_2 = {}
    for var in variables:
        if variables[var].x == 1:
            (start, end, vehicle) = (var[0], var[1], var[2])
            if vehicle not in routes:
                routes[vehicle] = [start, end]
            elif routes[vehicle][-1] == start and start != origin_id:
                routes[vehicle].append(end)
            elif routes[vehicle][0] == end and end != origin_id:
                route_new = [start]
                for point in routes[vehicle]:
                    route_new.append(point)
                routes[vehicle] = route_new
            else:
                variables_2[var] = variables[var]
    if variables_2:
        return disp_route(variables_2, routes)
    else:
        for route_num in routes:
            distance = vehicle_distance[route_num].x
            route = routes[route_num]
            print("Route %d: %s total distance: %f" % (route_num, str(route), float(distance)))
        print("Total distance of all routes: %f" % (avg_distance*num_vehicles))
        return routes


time_3 = time.perf_counter()
sol = disp_route(path)

print("Time to build model: %f seconds" % (time_2-time_1))
print("Time to solve model: %f seconds" % (time_3-time_2))
print("Total time to build and solve model: %f seconds" % (time_3-time_1))


def graph():
    fig, grph = plt.subplots()
    for route_num in sol:
        long = []
        lat = []
        for point_num in sol[route_num]:
            if point_num == origin_id:
                long.append(map_1.origin["longitude"])
                lat.append(map_1.origin["latitude"])
                continue
            for point_data in map_1.geodata:
                if point_data["route_stop_id"] == point_num:
                    long.append(point_data["longitude"])
                    lat.append(point_data["latitude"])
        df = pd.DataFrame({"longitude": long, "latitude": lat})
        grph.plot('longitude', 'latitude', data=df)

    plt.show()


graph()
