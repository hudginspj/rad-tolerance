#!/usr/bin/python3
import random
import math
import itertools
import sys
import time
import datetime


def read_cities(threshold=float("inf")):
    lines = sys.stdin.readlines()
    time.sleep(2)
    lines = [line.split() for line in lines]
    cities = [[float(line[0]), float(line[1])] for line in lines]
    points = []
    for i, p in enumerate(cities):
        points.append((p[0], p[1], i))
    return points

def gen_cities(n, max_xy, threshold=float("inf")):
    min_xy = max_xy / 200.0
    def coord():
        return min_xy + random.uniform(min_xy, max_xy)
    cities = [(coord(), coord()) for i in range(n)]
    points = []
    for i, p in enumerate(cities):
        points.append((p[0], p[1], i))
    return points

def length(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 )

def held_karp_start_endpoints(cities, start_point, endpoints):
    cities = cities.copy()

    start = cities.index(start_point)
    cities[0], cities[start] = cities[start], cities[0]
    
    all_distances = [[length(x,y) for y in cities] for x in cities]
    
    #{(S, endpoint):(distance, path)}
    best_paths = {}
    for i in range(1, len(cities)):
        best_paths[(frozenset([i]), i)] = (all_distances[0][i], [0,i])
    
    for s in range(2, len(cities)):
        subsets = [frozenset(S) for S in itertools.combinations(range(1, len(cities)), s)]
        new_best_paths = {}
        for S in subsets:
            for i in S:
                best_length = float("inf")
                best_path = None
                s_minus_i = S-{i}
                for j in s_minus_i:
                    path_length = best_paths[(s_minus_i,j)][0] + all_distances[j][i]
                    if path_length < best_length:
                        best_length = path_length
                        best_path = best_paths[(s_minus_i,j)][1] + [i]
                new_best_paths[(S, i)] = (best_length, best_path)
        best_paths = new_best_paths
    
    res = []
    endpoint_indexes = [cities.index(ep) for ep in endpoints]
    for set_endpoint in iter(best_paths):
        if set_endpoint[1] in endpoint_indexes:
            endpoint = cities[set_endpoint[1]]
            distance = best_paths[set_endpoint][0]
            calc_path = best_paths[set_endpoint][1]
            path = [cities[index][2] for index in calc_path]
            #print(calc_path, path)
            res.append((start_point, endpoint, distance, path))

    return res
    
def best_between_endpoints_annotated(points, endpoints):
    res = []
    for i in range(len(endpoints)):
        start = endpoints[i]
        for solution in held_karp_start_endpoints(points, start, endpoints[:i] + endpoints[i+1:]):
            res.append(solution)
    return res

def best_closed_sol(sols):  
    def closed_dist(sol):
        return sol[2] + length(sol[0], sol[1])
    best = min(sols, key=closed_dist)
    return closed_dist(best), best[3]#, best[2]

def total_distance(cities, path):
    if len(path) != len(cities):
        print("path/cities", len(path), len(cities))
        raise Exception("not a complete path")
    dist = length(cities[path[0]], cities[path[-1]])
    for i in range(len(cities)-1):
        dist += length(cities[path[i]], cities[path[i+1]])
    return dist
    


def exact_tsp(cities):
    exact_sols =  held_karp_start_endpoints(cities, cities[0], cities)
    res_exact = best_closed_sol(exact_sols)
    return res_exact[1]

def exact_trial(n):
    cities = gen_cities(n,500)
    #cities = read_cities()

    start_time = datetime.datetime.now()
    path = exact_tsp(cities)
    print(path)
    runtime = (datetime.datetime.now() - start_time).total_seconds()
    
    distance = total_distance(cities, path)
    return len(cities), runtime, distance



if __name__ == "__main__":
    print(exact_trial(12))
    
