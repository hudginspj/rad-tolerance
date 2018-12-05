#!/usr/bin/python3
import math
import os
import datetime
import time
from inversions import *
from mpi4py import MPI

#print("hello")

start_time = datetime.datetime.now()

BLOCK_SIZE = 10
SPLIT_DEPTH = 4
CITIES = 50000

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
if SPLIT_DEPTH >= 1:
    x_dim = 2**int(math.ceil((SPLIT_DEPTH+1)/2.0))
    y_dim = 2**int(math.floor((SPLIT_DEPTH+1)/2.0))
    cartesian = comm.Create_cart(dims = [x_dim,y_dim],periods =[False,False],reorder=False)
    coord = cartesian.Get_coords(rank)

def get_time():
    return (datetime.datetime.now() - start_time).total_seconds()

def recursive_split_MPI():
    cities, all_cities, depth = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG)
    res = recursive_split(cities, all_cities, depth)
    dest_rank = rank - math.pow(2, depth-1)
    comm.send(res, dest=dest_rank, tag=11)


def recursive_split(cities, all_cities, depth=0):
    if len(cities) <= BLOCK_SIZE:
        path = exact_tsp(cities)
        return path

    if depth % 2 == 0:
        part0, part1 = x_partition(cities)
    else:
        part0, part1 = y_partition(cities)

    if depth <= SPLIT_DEPTH:
        sub_rank = rank + int(math.pow(2, depth))
        print("  " * depth, rank, "sending to", sub_rank, get_time())
        comm.send((part0, all_cities, depth+1), dest=sub_rank, tag=11)
        print("  " * depth, rank, "done sending to", sub_rank, get_time())

        path1 = recursive_split(part1, all_cities, depth+1)

        path0 = comm.recv(source=sub_rank, tag=MPI.ANY_TAG)
        print("  " * depth, rank, "recieved from", sub_rank, get_time())

        
    else:
        path0 = recursive_split(part0, all_cities, depth+1)
        path1 = recursive_split(part1, all_cities, depth+1)

    path = swap(path0, path1, all_cities)
    if depth == SPLIT_DEPTH + 1:
        print("  " * depth, rank, "starting inversions", get_time())
        path, inversions = fix_inv(path, all_cities, 200)
        print("  " * depth, rank, "done inversions", get_time())

    return path

def mpi_tsp(cities):
    path = recursive_split(cities, cities, depth=0)
    return path

def mpi_trial(n):
    cities = gen_cities(n,500)

    path = mpi_tsp(cities)
    runtime = (datetime.datetime.now() - start_time).total_seconds()
    
    distance = total_distance(cities, path)
    return n, runtime, distance

if rank != 0:
    recursive_split_MPI()
else:
    n, runtime, distance = mpi_trial(CITIES)
    print("-- mpi:")
    print((SPLIT_DEPTH, n, runtime, distance))
    



