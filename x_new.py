#!/usr/bin/python3
from mpi4py import MPI
from enum import Enum

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

def exec_task(tasks, buffers):
    # Should send to multiple processors
    # Second iteration: figure out which workers are not busy, and send it to them
    # If all workers are busy, wait until they are free
    comm = MPI.COMM_WORLD
    size = comm.size        # total number of processes
    rank = comm.rank        # rank of this process
    status = MPI.Status()   # get MPI status object

    retval = dict()     # we store the results of multiple processors
    workers = list()    # we save here the true workers that are doing the job
    
    if rank == 0:
        # run_master(task, buffers, comm, size, rank, status, retval, workers)

        total_iterations = 0
        for i in range(len(tasks)):
            total_iterations = total_iterations + (1 * tasks[i].redundancy)

        redundancy = tasks[0].redundancy
        task_index = 0
        current_task_exec = 0   # counter of times task is being executed. Should stop when == redundancy
        num_workers = size - 1
        finished_workers = 0
        
        print("Master starting with %d workers" % num_workers)

        #while (True):
        while (finished_workers < num_workers):
            while (task_index < len(tasks)):
                while (current_task_exec < redundancy):
            
                    data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
                    source = status.Get_source()
                    tag = status.Get_tag()

            if tag == tags.READY:
                
                    


            if tag == tags.READY:
                if task_index < len(tasks):  # if we still need to send the task to more processors 
                    
                    if (current_task_exec < redundancy):
                        comm.send((tasks[task_index], buffers), dest=source, tag=tags.START)
                        print("Sending task %d to worker %d" % (task_index, source))
                        workers.append(source)
                        current_task_exec += 1
                    else:
                        task_index += 1
                        if (task_index == len(tasks)):
                            comm.send((None, None), dest=source, tag=tags.EXIT)        
                        else:
                            current_task_exec = 0
                            redundancy = tasks[task_index].redundancy
                            comm.send((tasks[task_index], buffers), dest=source, tag=tags.START)
                            print("Sending task %d to worker %d" % (task_index, source))
                            workers.append(source)
                            current_task_exec += 1
                else:
                    comm.send((None, None), dest=source, tag=tags.EXIT)

            elif tag == tags.DONE:
                retval[source] = data
                print("Got data from worker %d" % source)
            elif tag == tags.EXIT:
                print("Worker %d exited." % source)
                finished_workers += 1
                if (finished_workers == num_workers):
                    break

        print("Master finishing")
    else:
        run_worker(task, buffers, comm, size, rank, status)
    
    comm.barrier()

    # redo = False
    # if (rank == 0):
    #     print("workers: ", workers)
    #     if (retval[workers[0]][task.output_key].data != retval[workers[1]][task.output_key].data):  #todo: consider more than two processors
    #         redo = True
    #     else:
    #         buffers = retval[workers[0]]
    #         #print_buffers(buffers)

    # print("redo: ", redo, " - rank: ", rank)
    # if (rank == 0):
    #     run_master(task, buffers, comm, size, rank, status, retval, workers, redo)
    # else:
    #     run_worker(task, buffers, comm, size, rank, status)

    if (rank == 0):
        print_buffers(buffers, "Im your final master")
    
    comm.barrier()

def run_master(task, buffers, comm, size, rank, status, retval, workers, redo=True):
    redundancy = task.redundancy
    task_index = 0
    num_workers = size - 1
    finished_workers = 0
    
    print("Master starting with %d workers" % num_workers)

    #while (True):
    while finished_workers < num_workers:
        data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
        source = status.Get_source()
        tag = status.Get_tag()

        if (redo==False):
            comm.send((None, None), dest=source, tag=tags.EXIT)
            finished_workers += 1
        else:
            
            if tag == tags.READY:
                if task_index < redundancy:  # if we still need to send the task to more processors 
                    comm.send((task, buffers), dest=source, tag=tags.START)
                    print("Sending task %d to worker %d" % (task_index, source))
                    workers.append(source)
                    task_index += 1
                else:
                    comm.send((None, None), dest=source, tag=tags.EXIT)

            elif tag == tags.DONE:
                retval[source] = data
                print("Got data from worker %d" % source)
            elif tag == tags.EXIT:
                print("Worker %d exited." % source)
                finished_workers += 1

    print("Master finishing")


def run_worker(task, buffers, comm, size, rank, status):
    print("I am a worker with rank %d." % (rank))
    while True:
        comm.send(None, dest=0, tag=tags.READY)
        task, buffers = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
        tag = status.Get_tag()
        
        if tag == tags.START:
            args = [buffers[key].data for key in task.input_keys]
            print("args: ", str(args))
            print("task.input_keys: ", task.input_keys)
            out_buffer = buffers[task.output_key]
            out_buffer.data = task.function(*args)
            out_buffer.filled = True
            # buffers[task.output_key] = bit_gremlin(out_buffer)

            print("task.output_key: ", task.output_key)
            print("out_buffer.data: ", out_buffer.data)
            comm.send(buffers, dest=0, tag=tags.DONE)
        elif tag == tags.EXIT:
            break

    comm.send(None, dest=0, tag=tags.EXIT)

def print_buffers(buffers, msg=""):
    print("---", msg, "---Buffers ---")
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
# tsp = None
# tsp_stitch = None

# Task('Path1', tsp, 'Block1', redundancy=3)
# Task('Path2', tsp, 'Block2', redundancy=3)
# Task('Path', tsp_stitch, 'Path1','Path2', redundancy=2)


buffers = {key: Buffer(data) for (key, data) in buffer_data.items()}

print_buffers(buffers)
# exec_task(tasks[0], buffers)
# print_buffers(buffers)
# exec_task(tasks[1], buffers)
# print_buffers(buffers)

exec_task(tasks, buffers)
