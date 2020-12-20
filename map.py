import json
from util import distance_calc


class Map(object):

    def __init__(self, filename):
        self.filename = filename
        with open(filename) as file:
            self.geodata = json.load(file)
        self.origin = {'latitude': 45.528951, 'longitude': -122.659042, 'route_stop_id': 132}
        self.origin_id = self.origin['route_stop_id']

        # Calculate distances between all points
        self.distances = {}  # set of distances between all points
        self.points = []  # List of all non origin points
        self.load_distance()

    def load_distance(self):
        # Distances from origin
        for point in self.geodata:
            self.points.append(point['route_stop_id'])
            dist = distance_calc(self.origin, point)
            self.distances[(point['route_stop_id'], self.origin_id)] = dist
            self.distances[(self.origin_id, point['route_stop_id'])] = dist  # symmetrical indices

        # Distances between all non origin points
        for point_1 in self.geodata:
            for point_2 in self.geodata:
                # Make sure point is not distanced from itself and that distance has not already been calculated
                if not (point_1 == point_2 or (point_1['route_stop_id'], point_2['route_stop_id']) in
                        self.distances.keys()):
                    dist = distance_calc(point_1, point_2)
                    self.distances[(point_1['route_stop_id'], point_2['route_stop_id'])] = dist
                    self.distances[(point_2['route_stop_id'], point_1['route_stop_id'])] = dist  # symmetrical indices

        avg_dist = sum(self.distances.values())/len(self.distances)
        over_avg = True
        while over_avg:
            over_avg = False
            for val in self.distances:
                if self.distances[val] >= avg_dist:
                    self.distances.pop(val)
                    over_avg = True
                    break
