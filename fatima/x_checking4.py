#!/usr/bin/python3
import dill

from mpi4py import MPI
MPI.pickle.__init__(dill.dumps, dill.loads)

from enum import Enum
from collections import Counter
#from random import randint

import time
import timeit
import math
import random

class Buffer:
    def __init__(self, data=None):
        self.data = data
        self.needed = True
        self.filled = data is not None
        

class Task:
    def __init__(self, out, f, *ins, redundancy=2):
        self.function = f
        self.input_keys = ins
        self.output_key = out
        self.done = False
        self.redundancy = redundancy

def enum(*sequential, **named):
    """Handy way to fake an enumerated type in Python
    http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
    """
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

# Define MPI message tags
tags = enum('READY', 'REDO', 'DONE', 'EXIT', 'START')   

comm = MPI.COMM_WORLD
size = comm.size        # total number of processes
rank = comm.rank        # rank of this process
status = MPI.Status()   # get MPI status object



def exec_task(task, buffers):  
    print("Master starting")

    workers = []
    retval = {}
    for i in range(task.redundancy):
        data = comm.recv(source=MPI.ANY_SOURCE, tag=tags.READY, status=status)
        source = status.Get_source()
        print("Sending task %d to worker %d" % (i, source), task, buffers)
        comm.send((task, buffers), dest=source, tag=tags.START)
        workers.append(source)

    for worker in workers:
        data = comm.recv(source=worker, tag=tags.DONE, status=status)
        retval[worker] = data
        print("workers: ", workers, "retval", retval.items())

    # print("hola - retval[workers[0]]", retval[workers[0]])
    # print("hola - retval[workers[1]]", retval[workers[1]])

    values_list = list(retval.values())
    eq = len(set(values_list)) == 1         # Using set removes all duplicate elements. https://stackoverflow.com/a/23415761/3516051
    print("eq: ", eq)
    # print("len: ", len(set(values_list)))
    
    if (eq == False and task.redundancy == 2):  # redo
        exec_task(task, buffers)
    elif (eq == False and task.redundancy > 2): # voting
        counter = Counter(values_list)
        majority_vote = counter.most_common(1)[0][0]
        print("majority_vote: ", majority_vote)
        output_buffer = buffers[task.output_key]
        output_buffer.data = majority_vote
        output_buffer.filled = True
    else:
        output_buffer = buffers[task.output_key]
        output_buffer.data = retval[workers[0]]
        output_buffer.filled = True
    print("Master finishing")


def run_worker():
    print("I am a worker with rank %d." % (rank))
    while True:
        comm.send(None, dest=0, tag=tags.READY)
        task, buffers = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
        tag = status.Get_tag()
        
        if tag == tags.START:
            args = [buffers[key].data for key in task.input_keys]
            print("args: ", str(args))
            print("task.input_keys: ", task.input_keys)
            output = task.function(*args)
            comm.send(output, dest=0, tag=tags.DONE)
        elif tag == tags.EXIT:
            break

    comm.send(None, dest=0, tag=tags.EXIT)

def exit_all():
    for i in range(1, size):
        comm.send((None, None), dest=i, tag=tags.EXIT)


def buffers_from_tasks(tasks):
    buffers = {}
    for task in tasks:
        buffers[task.output_key] = Buffer()
    buffers['init'] = Buffer('INIT')
    buffers['quit'] = Buffer(False)
    return buffers

def error_probability(task_time, half_error_time):
    return 1.0 - math.pow(0.5, float(task_time)/half_error_time)

def inc_test(wait_time, half_error_time):
    def f(x):
        desired_value = x+1
        error_value = random.random() + 1000
        error_prob = error_probability(wait_time, half_error_time)
        result = random.choices(
            population=[desired_value, error_value],
            weights=[1-error_prob, error_prob],
            k=1
        )[0]

        time.sleep(wait_time)
        return result   #Increment the input for testing purposes
    return f    

def print_state(tasks, buffers):
    s = ''
    for key, buf in buffers.items():
        data = str(buf.data).ljust(6) if buf.filled else 'EMPTY '
        s += "{0}: {1}".format(key, data)   # f"{key}: {data} "
    # for task in tasks:
    #     ready = ' P' if prereqs_ready(task, buffers) else 'NP'
    #     done = ' D' if task.done else 'ND'
    #     s += f'|{task} {ready} {done} '
    print(s)


def prereqs_ready(task, buffers):
    for input_key in task.input_keys:
        if not buffers[input_key].filled:
            return False
    return True


def next_task(tasks, buffers):
    for task in tasks:
        if not task.done and prereqs_ready(task, buffers):
            return task
    return None


def garbage_collect(tasks, buffers):
    for buffer in buffers.values():
        buffer.needed = False
    for task in tasks:
        output_buffer = buffers[task.output_key]  ### Move down??
        #print(task, task.done, output_buffer.filled)
        task.done = output_buffer.filled
        if not task.done:
            for input_key in task.input_keys:
                buffers[input_key].needed = True  
    for key, buffer in buffers.items():
        if buffer.filled and not buffer.needed:
            buffer.filled = False
            buffer.data = None


if __name__ == "__main__":
    def print_buffers(buffers):
        print("--- Buffers ---")
        for key, buf in buffers.items():
            filled = 'Filled' if buf.filled else 'Empty'
            print('{0}, {1}: {2}'.format(key, filled, buf.data))


    # buffer_data = {
    #     'A': 5,
    #     'B': 10,
    #     'C': 15,
    #     'D': None,
    #     'E': None,
    # }
    # buffers = {key: Buffer(data) for (key, data) in buffer_data.items()}

    # tasks = [
    #     Task('D', max, 'A','B'),
    #     Task('E', lambda self, x: [randint(1, 2)][0], 'C','D', redundancy=3)
    # ]

    trial_2 = [
        Task('A', lambda x: 0, 'init'),
        Task('quit', lambda x: x>=6, 'A'),

        Task('B', inc_test(1, 2), 'A'),
        Task('C', inc_test(1, 2), 'B'),
        Task('A', inc_test(1, 2), 'C'),
    ]

    buffers = buffers_from_tasks(trial_2)
  

    try:
        while True:
            if (rank == 0):
                print_state(trial_2, buffers)

                next_t = next_task(trial_2, buffers)
                if next_t is None:
                    break
                exec_task(next_t, buffers)

                if buffers['quit'].data == True:
                    print_state(trial_2, buffers)
                    break
                    
                garbage_collect(trial_2, buffers)
            else:
                run_worker()

        # if (rank == 0):
        #     # print_buffers(buffers)
        #     # exec_task(tasks[0], buffers)
        #     # print_buffers(buffers)
        #     # exec_task(tasks[1], buffers)
        #     # print_buffers(buffers)
        #     # exit_all()

        #     print_buffers(buffers)
        #     exec_task(trial_2[0], buffers)
        #     print_buffers(buffers)
        #     exec_task(trial_2[1], buffers)
        #     print_buffers(buffers)
        #     exec_task(trial_2[3], buffers)
        #     print_buffers(buffers)
        #     exec_task(trial_2[4], buffers)
        #     print_buffers(buffers)
        #     exec_task(trial_2[5], buffers)
        #     print_buffers(buffers)
        #     exit_all()            
        # else:
        #     run_worker()
    except Exception as e:
        print('execption in', rank)
        raise e
        exit(0)