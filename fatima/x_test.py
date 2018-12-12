#!/usr/bin/python3
from mpi4py import MPI
from enum import Enum
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

class Tags(Enum):
    READY = 1
    DONE = 2
    EXIT = 3
    START = 4 

GREMLIN_RATE = 4

def bit_gremlin(buff):
    if (random.randint(2,100)%GREMLIN_RATE == 0):
        buff.data = buff.data + 1
    return buff

def exec_task(task, buffers):
    # Should send to multiple processors
    # Second iteration: figure out which workers are not busy, and send it to them
    # If all workers are busy, wait until they are free
    # args = [buffers[key].data for key in task.input_keys]
    # out_buffer = buffers[task.output_key]
    # out_buffer.data = task.function(*args)
    # out_buffer.filled = True
    
    comm = MPI.COMM_WORLD
    size = comm.size        # total number of processes
    rank = comm.rank        # rank of this process
    status = MPI.Status()   # get MPI status object

    if rank == 0:
        # Master code
        redundancy = 1
        num_workers = size - 1
        _count = 0

        while (True):
            while (redundancy <= task.redundancy):
                print("Sending task to worker %d" % (redundancy))            
                comm.send((task, buffers), dest=redundancy, tag=Tags.START.value)            
                redundancy = redundancy + 1

            retval = dict()
            redundancy = 1
            while (redundancy <= task.redundancy):
                retval[redundancy] = comm.recv(source=redundancy, tag=MPI.ANY_TAG, status=status)
                
                print("Receiving from worker %d" % (redundancy))
                redundancy = redundancy + 1

            #comm.Barrier()
            # if _count == 0:
            #     retval[1][task.output_key].data = 11
            #     _count = _count + 1

            print("retval[1] -> ", retval[1][task.output_key].data)
            print("retval[2] -> ", retval[2][task.output_key].data)

            # if (retval[1][task.output_key].data != retval[2][task.output_key].data):
            if _count == 0:
                print("Checking again..")
                _count = 1
                redundancy = 1
                break
            else:
                buffers = retval[1]
                print("Breaking..")
                break      
       
        print("Master done")
    else:
        # Workers code
        print("I am worker with rank %d." % (rank))

        task, buffers = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
        tag = status.Get_tag()

        args = [buffers[key].data for key in task.input_keys]
        print("args: ", str(args))
        print("task.input_keys: ", task.input_keys)
        out_buffer = buffers[task.output_key]
        out_buffer.data = task.function(*args)
        out_buffer.filled = True
        # buffers[task.output_key] = bit_gremlin(out_buffer)

        print("task.output_key: ", task.output_key)
        print("out_buffer.data: ", out_buffer.data)
        comm.send(buffers, dest=0, tag=Tags.DONE.value)


def print_buffers(buffers):
    print("--- Buffers ---")
    for key, buf in buffers.items():
        filled = 'Filled' if buf.filled else 'Empty'
        print('{0}, {1}: {2}'.format(key, filled, buf.data))

def prereqs_ready(task, buffers):
    for input_key in task.input_keys:
        if not buffers[input_key].filled:
            return False
    return True

buffer_data = {
    'A': 5,
    'B': 10,
    'C': 15,
    'D': None,
    'E': None,
}

tasks = [
    Task('D', max, 'A','B'),
    Task('E', max, 'C','D')
]


buffers = {key: Buffer(data) for (key, data) in buffer_data.items()}

print_buffers(buffers)
exec_task(tasks[0], buffers)
print_buffers(buffers)
# exec_task(tasks[1], buffers)
# print_buffers(buffers)

print("Bye")





