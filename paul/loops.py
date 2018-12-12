
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
    def __str__(self):
        return f'{self.output_key} {self.function.__name__} {",".join(self.input_keys)}'


def exec_task(task, buffers):
    # Should send to multiple processors
    # Second iteration: figure out which workers are not busy, and send it to them
    # If all workers are busy, wait until they are free
    args = [buffers[key].data for key in task.input_keys]
    out_buffer = buffers[task.output_key]
    out_buffer.data = task.function(*args)
    out_buffer.filled = True
    task.done = True


def print_state(tasks, buffers):
    s = ''
    for key, buf in buffers.items():
        data = str(buf.data).ljust(6) if buf.filled else 'EMPTY '
        s += f"{key}: {data} "
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
    for buffer in buffers.values():
        if buffer.filled and not buffer.needed:
            buffer.filled = False
            buffer.data = None


def buffers_from_tasks(tasks):
    buffers = {}
    for task in tasks:
        buffers[task.output_key] = Buffer()
    buffers['init'] = Buffer('')
    return buffers


tasks = [
    Task('A', lambda x: 5, 'init'),
    Task('B', lambda x: 10, 'init'),
    Task('C', lambda x: 15, 'init'),
    Task('D', max, 'A','B'),
    Task('E', max, 'C','D')
    #Task('init', lambda x: '', 'E')
]

tasks = [
    Task('A', lambda x: 0, 'init'),
    Task('B', lambda x: x, 'A'),
    Task('C', lambda x: x, 'B'),
    Task('A', lambda x: x+1, 'C'),
    # Task('D', max, 'A','B'),
    # Task('E', max, 'C','D')
    #Task('init', lambda x: '', 'E')
]

def cycle(tasks):
    buffers = buffers_from_tasks(tasks)
    while True:
        print_state(tasks, buffers)
        next_t = next_task(tasks, buffers)
        if next_t is None:
            return
        exec_task(next_t, buffers)
        garbage_collect(tasks, buffers)


cycle(tasks)





