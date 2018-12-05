#!/usr/bin/python3
import math
import os
import datetime
import time
from multiprocessing import Process, Pipe
from heldkarp import *
from inversions import *

def recursive_split_process(cities, depth, conn):
    #print("Starting ", os.getpid())
    res = recursive_split(cities, depth)
    #print("done: ", os.getpid())
    conn.send(res)
    conn.close()

def recursive_split(cities, all_cities, depth=0):
    if len(cities) < 11:
        path = exact_tsp(cities)
        return path

    if depth % 2 == 0:
        part0, part1 = x_partition(cities)
    else:
        part0, part1 = y_partition(cities)

    path0 = recursive_split(part0, all_cities, depth+1)
    path1 = recursive_split(part1, all_cities, depth+1)

    if depth < 4:
        pass
        print("  " * depth, len(cities), len(part0), len(path0), len(part1), len(path1))
    path = swap(path0, path1, all_cities)

    return path

def threaded_tsp(cities):
    return recursive_split(cities, cities, depth=0)

def threaded_trial(n):
    cities = gen_cities(n,500)

    start_time = datetime.datetime.now()
    path = threaded_tsp(cities)
    plot_path(path, cities, "b")
    plt.savefig("new_mp.png")
    plt.show()
    runtime = (datetime.datetime.now() - start_time).total_seconds()
    
    distance = total_distance(cities, path)
    return n, runtime, distance


def inv_test3():
    cities = gen_cities(5000,500)

    start_time = datetime.datetime.now()
    path = threaded_tsp(cities)
    plot_path(path, cities, "r:")
    #plt.savefig("new_mp.png")
    distance = total_distance(cities, path)
    print("distance", distance)
    print("runtime", (datetime.datetime.now() - start_time).total_seconds())

    path, inversions = fix_inv(path, cities, 100)
    path, inversions = fix_inv(path, cities, 50)
    path, inversions = fix_inv(path, cities, 100)
    
    distance = total_distance(cities, path)
    print("distance", distance)
    print("runtime", (datetime.datetime.now() - start_time).total_seconds())
    #plot_path(path, cities, "g:")

    path, inversions = fix_inv(path, cities, 5000)
    path, inversions = fix_inv(path, cities, 500)
    path, inversions = fix_inv(path, cities, 50)
    distance = total_distance(cities, path)
    print("distance", distance)
    print("runtime", (datetime.datetime.now() - start_time).total_seconds())
    #plot_path(path, cities, "b")

    #plt.show()


def inv_test4():
    n = 50000
    cities = gen_cities(n,500)

    start_time = datetime.datetime.now()
    path = threaded_tsp(cities)
    #plot_path(path, cities, "r:")
    #plt.savefig("new_mp.png")
    print("-- n=", n)
    distance = total_distance(cities, path)
    print("distance", distance)
    print("runtime", (datetime.datetime.now() - start_time).total_seconds())

    path, inversions = fix_inv(path, cities, 100)
    path, inversions = fix_inv(path, cities, 25)
    
    distance = total_distance(cities, path)
    print("distance", distance)
    print("runtime", (datetime.datetime.now() - start_time).total_seconds())
    #plot_path(path, cities, "b")

    #plt.show()


if __name__ == "__main__":
    #print(threaded_trial(5000))
    inv_test4()
    

