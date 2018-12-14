import time
import timeit
import math
import random
import argparse
from task_graph import cycle, Task, rank




# A set of tasks that increment a value in a loop
loop_tasks = [
    Task('A', lambda x: 0, 'init'),
    Task('quit', lambda x: x>=5, 'A'),
    
    Task('B', lambda x: x, 'A'),
    Task('C', lambda x: x, 'B'),
    Task('A', lambda x: x+1, 'C'),
    
]

def error_probability(task_time, half_error_time):
    return 1.0 - math.pow(0.5, float(task_time)/half_error_time)


def inc_test(wait_time, half_error_time):
    '''Generates task functions for experiments'''
    def f(x):
        '''Increments the input buffer with simulated task time and error probabilities'''
        error_prob = error_probability(wait_time, half_error_time)
        if random.random() > error_prob:
            result = x+1  #Increment the input for testing purposes
        else:
            result = random.random() * 1000
        time.sleep(wait_time)
        return result   
    return f

def make_trial(wait_time, half_error_time, repetitions, redundancy):
    '''Generates a set of tasks for experiments'''
    return [
        Task('A', lambda x: 0, 'init'),
        Task('quit', lambda x: x>=repetitions, 'A'),

        Task('B', inc_test(wait_time, half_error_time), 'A', redundancy=redundancy),
        Task('C', inc_test(wait_time, half_error_time), 'B', redundancy=redundancy),
        Task('A', inc_test(wait_time, half_error_time), 'C', redundancy=redundancy),
    ]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run project experiments')
    parser.add_argument('task_time', type=float)
    parser.add_argument('half_error_time', type=float)
    parser.add_argument('repetitions', type=int)
    parser.add_argument('redundancy', type=int)
    args = parser.parse_args()


    tasks = make_trial(args.task_time, args.half_error_time, args.repetitions, args.redundancy)

    start = timeit.default_timer()  
    redos = cycle(tasks)
    
    if rank == 0:
        runtime = timeit.default_timer() - start
        print('task time', args.task_time, 'half_error_time', args.half_error_time, 'repititions', args.repetitions, 'redundancy', args.redundancy)
        print("total redos:", redos, "redo ratio", redos/args.repetitions)
        print('runtime', runtime, 'average runtime', runtime/args.repetitions, 'average work', runtime * args.redundancy / args.repetitions)





