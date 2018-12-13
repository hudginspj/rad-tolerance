import time
import timeit
import math
import random
import argparse
from task_graph import cycle, Task, rank


merges = [
    Task('A', lambda x: 5, 'init'),
    Task('B', lambda x: 10, 'init'),
    Task('C', lambda x: 15, 'init'),
    Task('D', max, 'A','B'),
    Task('E', max, 'C','D')
    #Task('init', lambda x: '', 'E')
]


def check_count(A):
    print("checking count", A)
    if A >= 20:
        return True
    else:
        return False

loop_count = [
    Task('A', lambda x: 0, 'init'),
    Task('quit', check_count, 'A'),
    Task('B', lambda x: x, 'A'),
    Task('C', lambda x: x, 'B'),
    Task('A', lambda x: x+1, 'C'),
]

def wait_and_pass(wait_time):
    def f(x):
        time.sleep(wait_time)
        return x
    return f



trial_1 = [
    Task('A', lambda x: 0, 'init'),
    Task('quit', lambda x: x>=5, 'A'),
    Task('B', lambda x: x, 'A'),
    Task('C', wait_and_pass(1), 'B'),
    Task('A', lambda x: x+1, 'C'),
    
]

def error_probability(task_time, half_error_time):
    return 1.0 - math.pow(0.5, float(task_time)/half_error_time)

def inc_test(wait_time, half_error_time):
    def f(x):
        error_prob = error_probability(wait_time, half_error_time)
        if random.random() > error_prob:
            result = x+1  #Increment the input for testing purposes
        else:
            result = random.random() * 1000
        

        time.sleep(wait_time)
        return result   
    return f

trial_2 = [
    Task('A', lambda x: 0, 'init'),
    Task('quit', lambda x: x>=60, 'A'),

    Task('B', inc_test(0.1, 0.2), 'A'),
    Task('C', inc_test(0.1, 0.2), 'B'),
    Task('A', inc_test(0.1, 0.2), 'C'),
]

def make_trial(wait_time, half_error_time, repetitions, redundancy):
    return [
        Task('A', lambda x: 0, 'init'),
        Task('quit', lambda x: x>=repetitions, 'A'),

        Task('B', inc_test(wait_time, half_error_time), 'A', redundancy=redundancy),
        Task('C', inc_test(wait_time, half_error_time), 'B', redundancy=redundancy),
        Task('A', inc_test(wait_time, half_error_time), 'C', redundancy=redundancy),
    ]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run project experiments')
    # parser.add_argument('integers', metavar='N', type=float,
    #                     help='an integer for the accumulator')
    parser.add_argument('task_time', type=float)
    parser.add_argument('half_error_time', type=float)
    parser.add_argument('repetitions', type=int)
    parser.add_argument('redundancy', type=int)

    args = parser.parse_args()

    # wait_time=0.1
    # half_error_time=0.2
    # repetitions=30
    # redundancy=2

    tasks = make_trial(args.task_time, args.half_error_time, args.repetitions, args.redundancy)

    start = timeit.default_timer()  
    redos = cycle(tasks)
    
    if rank == 0:
        runtime = timeit.default_timer() - start
        print('wait time', wait_time, 'half_error_time', half_error_time, 'repititions', repetitions, 'redundancy', redundancy)
        print("total redos:", redos, "redo ratio", redos/repetitions)
        print('runtime', runtime, 'average runtime', runtime/repetitions, 'average work', runtime * redundancy / repetitions)





