#!/usr/bin/python3
import dill

from mpi4py import MPI
MPI.pickle.__init__(dill.dumps, dill.loads)

from enum import Enum
from collections import Counter
from random import randint

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
        # print("Sending task %d to worker %d" % (i, source), task, buffers)
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
    if not eq:
        print("------ ERROR: ", values_list)
    # print("len: ", len(set(values_list)))
    
    if (eq == False and task.redundancy == 2):  # redo
        return exec_task(task, buffers) + 1
    elif (eq == False and task.redundancy > 2): # voting
        counter = Counter(values_list)
        majority_vote = counter.most_common(1)[0][0]
        print("majority_vote: ", majority_vote)
        output_buffer = buffers[task.output_key]
        output_buffer.data = majority_vote
        output_buffer.filled = True
        return 1
    else:
        output_buffer = buffers[task.output_key]
        output_buffer.data = retval[workers[0]]
        output_buffer.filled = True
        return 0
    print("Master finishing")


def run_worker():
    print("I am a worker with rank %d." % (rank))
    while True:
        comm.send(None, dest=0, tag=tags.READY)
        task, buffers = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
        tag = status.Get_tag()
        
        if tag == tags.START:
            args = [buffers[key].data for key in task.input_keys]
            # print("args: ", str(args))
            # print("task.input_keys: ", task.input_keys)
            output = task.function(*args)
            comm.send(output, dest=0, tag=tags.DONE)
        elif tag == tags.EXIT:
            print(rank, "exiting")
            break

    comm.send(None, dest=0, tag=tags.EXIT)
    return 0

def exit_all():
    print("Sending exit signal")
    for i in range(1, size):
        comm.send((None, None), dest=i, tag=tags.EXIT)


if __name__ == "__main__":
    def print_buffers(buffers):
        print("--- Buffers ---")
        for key, buf in buffers.items():
            filled = 'Filled' if buf.filled else 'Empty'
            print('{0}, {1}: {2}'.format(key, filled, buf.data))


    buffer_data = {
        'A': 5,
        'B': 10,
        'C': 15,
        'D': None,
        'E': None,
    }
    buffers = {key: Buffer(data) for (key, data) in buffer_data.items()}

    tasks = [
        Task('D', max, 'A','B'),
        Task('E', lambda self, x: [randint(1, 2)][0], 'C','D', redundancy=3)
    ]

    try:
        if (rank == 0):
            print_buffers(buffers)
            exec_task(tasks[0], buffers)
            print_buffers(buffers)
            exec_task(tasks[1], buffers)
            print_buffers(buffers)
            exit_all()
        else:
            run_worker()
    except Exception as e:
        print('execption in', rank)
        raise e
        exit(0)