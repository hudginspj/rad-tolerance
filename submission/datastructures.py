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

def buffers_from_tasks(tasks):
    buffers = {}
    for task in tasks:
        buffers[task.output_key] = Buffer()
    buffers['init'] = Buffer('INIT')
    buffers['quit'] = Buffer(False)
    return buffers


def print_state(tasks, buffers):
    s = 'Buffers: '
    for key, buf in buffers.items():
        data = str(buf.data).ljust(6) if buf.filled else 'EMPTY '
        s += str(key) + ": " + str(data)
    print(s)


