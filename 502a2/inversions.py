#!/usr/bin/python3
import math
import os
import datetime
import time
from heldkarp import *
from merge import *



def ccw(a,b,c):
    return (c[1]-a[1]) * (b[0]-a[0]) > (b[1]-a[1]) * (c[0]-a[0])

def is_inv(four_idx, all_cities):
    i0, i1, j0, j1 = four_idx
    a0, a1, b0, b1 = [all_cities[i] for i in four_idx]
    return ccw(a0,b0,b1) != ccw(a1,b0,b1) and ccw(a0,a1,b0) != ccw(a0,a1,b1)

def show_inv(path, all_cities):
    for i in range(len(path)-3):
        for j in range(i+2,len(path)-1):
            four_path_idx = (i, i+1, j, j+1)
            four_idx = [path[k] for k in four_path_idx]
            if is_inv(four_idx, all_cities):
                print(i, j)
                plot_path(four_idx, all_cities, 'ro')
                path = path[:i+1] + list(reversed(path[i+1:j+1])) + path[j+1:]
                plot_path(path, all_cities, 'r:')
                

def fix_inv(path, all_cities, limit=10):
    count = 0
    for i in range(len(path)-3):
        j_limit = min(len(path)-1, i + limit)
        for j in range(i+2, j_limit):
            four_path_idx = (i, i+1, j, j+1)
            four_idx = [path[k] for k in four_path_idx]
            if is_inv(four_idx, all_cities):
                #print(i, j, j-i)
                path = path[:i+1] + list(reversed(path[i+1:j+1])) + path[j+1:]
                count += 1
    #print("inversions: ", count)
    return path, count



    
    

def inv_test():
    cities = [[0,0], [0,1], [1,0], [1,1]]
    print(is_inv([0,3,1,2], cities))

def inv_test2():
    cities = gen_cities(24,500)
    print("len cities", len(cities))

    start_time = datetime.datetime.now()
    path = one_swap(cities, cities)
    runtime = (datetime.datetime.now() - start_time).total_seconds()
    
    distance = total_distance(cities, path)
    print(distance)

    plot_path(path, cities, 'b')
    show_inv(path, cities)
    plt.show()





if __name__ == "__main__":
    inv_test3()
    

