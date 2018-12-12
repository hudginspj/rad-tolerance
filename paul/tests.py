import time
import timeit
from task_graph import cycle, Task

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

if __name__ == '__main__':
    start = timeit.default_timer()
    cycle(trial_1)
    stop = timeit.default_timer()

    print('Time: ', stop - start)





