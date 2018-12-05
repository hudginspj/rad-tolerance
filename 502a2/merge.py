import math
import os
import datetime
import time
from multiprocessing import Process, Pipe
from heldkarp import *

def x_partition(cities):
    
    n = len(cities)
    if n < 100:
        x_sorted = sorted(cities, key=lambda p: p[0])
        halfway = n // 2
        x_divider = x_sorted[halfway][0]
    else:
        coords = [p[0] for p in cities]
        min_coord = min(coords)
        max_coord = max(coords)
        x_divider = min_coord + (0.5 * (max_coord-min_coord))

    part1 = []
    part2 = []
    for p in cities:
        if p[0] < x_divider:
            part1.append(p)
        elif p[0] >= x_divider:
            part2.append(p)
        else:
            raise Exception()
    return part1, part2

def y_partition(cities):
    n = len(cities)
    if n < 100:
        y_sorted = sorted(cities, key=lambda p: p[1])
        halfway = n // 2
        y_divider = y_sorted[halfway][1]
    else:
        coords = [p[1] for p in cities]
        min_coord = min(coords)
        max_coord = max(coords)
        y_divider = min_coord + (0.5 * (max_coord-min_coord))
    part1 = []
    part2 = []
    for p in cities:
        if p[1] < y_divider:
            part1.append(p)
        elif p[1] >= y_divider:
            part2.append(p)
        else:
            raise Exception()
    return part1, part2

comps = []
non_comps = []


def near_path_indexies(path0, path1, all_cities):
    n_ideal = 50
    n = max(len(path0), len(path1))
    if n < n_ideal:
        return range(len(path0)), range(len(path1))
    xs0 = [all_cities[i][0] for i in path0]
    min_x0 , max_x0 = min(xs0), max(xs0)
    xs1 = [all_cities[i][0] for i in path1]
    min_x1 , max_x1 = min(xs1), max(xs1)

    if max_x0 < min_x1:
        cutoff0 = max_x0 - ((n_ideal/n) * (max_x0-min_x0))
        cutoff1 = min_x1 + ((n_ideal/n) * (max_x1-min_x1))
        path0_indexes = [i for i in range(len(path0)) if all_cities[path0[i]][0] > cutoff0]
        path1_indexes = [i for i in range(len(path1)) if all_cities[path1[i]][0] < cutoff1]
        return path0_indexes, path1_indexes
    
    ys0 = [all_cities[i][1] for i in path0]
    min_y0 , max_y0 = min(ys0), max(ys0)
    ys1 = [all_cities[i][1] for i in path1]
    min_y1 , max_y1 = min(ys1), max(ys1)
    if max_y0 < min_y1:
        cutoff0 = max_y0 - ((n_ideal/n) * (max_y0-min_y0))
        cutoff1 = min_y1 + ((n_ideal/n) * (max_y1-min_y1))
        path0_indexes = [i for i in range(len(path0)) if all_cities[path0[i]][1] > cutoff0]
        path1_indexes = [i for i in range(len(path1)) if all_cities[path1[i]][1] < cutoff1]
        return path0_indexes, path1_indexes
    else:
        raise Exception("Couldn't guess partition")



def swap(path0, path1, all_cities):
    def index_length(i, j):
        return length(all_cities[i], all_cities[j])
    def swap_cost():
        return index_length(l0, r0) + index_length(l1, r1) - index_length(l0, l1) - index_length(r0, r1)
    best_swap_cost = float("inf")
    best_swap = (None, None, None, None)
    
    path0_indexes, path1_indexes = near_path_indexies(path0, path1, all_cities)

    for i0 in path0_indexes:   #TODO handle last i
        i1 = (i0+1)%len(path0)
        l0 = path0[i0]
        l1 = path0[i1]
        for j0 in path1_indexes:
            j1 = (j0+1)%len(path1)
            r0 = path1[j0]
            r1 = path1[j1]
            if swap_cost() < best_swap_cost:
                best_swap_cost = swap_cost()
                best_swap = (i0, i1, j0, j1)
            r0 = path1[j1]
            r1 = path1[j0]
            if swap_cost() < best_swap_cost:
                best_swap_cost = swap_cost()
                best_swap = (i0, i1, j0, j1)
    (i0, i1, j0, j1) = best_swap
    
    
    if i1 == 0:
        path = path0[1:i0+1]
    else:
        path = path0[:i0+1]
    if j0 == 0 and j1 > 1:
        path += path1
    elif j0 > 1 and j1 == 0:
        path += reversed(path1)    
    elif j0 > j1:
        path += path1[j0:]
        path += path1[:j1+1]
    else:
        path += list(reversed(path1[:j0+1]))
        path += list(reversed(path1[j1:]))
    if i1 == 0:
        path.append(path0[0])
    else:
        path += path0[i1:]
    if len(path) != len(path0) + len(path1):
        print("err", len(path), len(path0), len(path1))
        raise Exception("....")
    return path
    

def one_swap(cities, all_cities):
    part0, part1 = x_partition(cities)
    path0 = exact_tsp(part0)
    path1 = exact_tsp(part1)
    # print(path0)
    # print(path1)
    path = swap(path0, path1, all_cities)
    return path


def swap_test(n):
    cities = gen_cities(n,500)
    print("len cities", len(cities))
    #cities = read_cities()

    start_time = datetime.datetime.now()
    path = one_swap(cities, cities)
    runtime = (datetime.datetime.now() - start_time).total_seconds()
    
    distance = total_distance(cities, path)
    print(distance)

    #plot_path(path, cities)

    path_opt = exact_tsp(cities)
    distance_opt = total_distance(cities, path_opt)
    print(distance_opt)

    #plot_path(path, cities)


    #return len(cities), runtime, distance
    return distance/distance_opt


def plot_path(path, all_cities, color, swap_points=None):
    x = [all_cities[i][0] for i in path]
    y = [all_cities[i][1] for i in path]
    plt.plot(x, y, color)
    plt.grid(True)
    #plt.show()
   


if __name__ == "__main__":
    ratios = []
    for i in range(100):
        ratios.append(swap_test(14))
    print(ratios)
    print(np.mean(ratios))
    plt.show()
    
