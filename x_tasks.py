
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
    #print("--- State ---")
    for key, buf in buffers.items():
        data = str(buf.data).ljust(6) if buf.filled else 'EMPTY '
        s += f"{key}: {data} "
    #print("--- Tasks ---")
    for task in tasks:
        ready = ' P' if prereqs_ready(task, buffers) else 'NP'
        done = ' D' if task.done else 'ND'
        s += f'|{task} {ready} {done} '
        #print(prereqs_ready(task, buffers), task)
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
# void garbage_collect(TASK *tasks, int num_tasks, BUF *bufs, int num_bufs) {
#     for (int i = 0; i < num_bufs; i++) {
#         bufs[i].needed = 0;
#     }
#     for (int i = 0; i < num_tasks; i++) {
#         //printf(" %i:", tasks[i].is_done);
#         if (!tasks[i].is_done){
#             for (int j = 0; j < tasks[i].num_inputs; j++){
#                 int input_j = tasks[i].input_indexes[j];
#                 //printf("%i:", input_j);
#                 bufs[input_j].needed = 1;
#             }
#         }
#     }
#     //printf(":done\n");
#     for (int i = 0; i < num_bufs; i++) {
#         BUF *buf = bufs + i;
#         if (buf->is_filled && !buf->needed) {
#             //printf("freeing %i\n", i);
#             buf_free(bufs + i);
#         }
#     }
# }



buffer_data = {
    'init': '',
    'A': 5,
    'B': 10,
    'C': 15,
    'D': None,
    'E': None,
}

tasks = [
    Task('D', max, 'A','B'),
    Task('E', max, 'C','D'),
    Task('A', lambda x: 5, 'E'),
    Task('B', lambda x: 10, 'E')
    #Task('C', lambda x: 15, 'E')
]
# tsp = None
# tsp_stitch = None

# Task('Path1', tsp, 'Block1', redundancy=3)
# Task('Path2', tsp, 'Block2', redundancy=3)
# Task('Path', tsp_stitch, 'Path1','Path2', redundancy=2)


buffers = {key: Buffer(data) for (key, data) in buffer_data.items()}


def reset():
    buffers['A']= Buffer(5)
    buffers['B'] = Buffer(10)
    buffers['C'] = Buffer(15)

def cycle(tasks, buffers):
    #print('r', prereqs_ready(tasks[1], buffers))
    count = 0
    while True:
        print_state(tasks, buffers)
        next_t = next_task(tasks, buffers)
        if next_t is None:
            return
        exec_task(next_t, buffers)
        garbage_collect(tasks, buffers)

for i in range(3):
    cycle(tasks, buffers)
    print(">>>>", i )
    reset()
    #print_state(tasks, buffers)
    garbage_collect(tasks, buffers)
    #print_state(tasks, buffers)
    #print("<<<<<")
# print_state(tasks, buffers)
# exec_task(tasks[0], buffers)
# print_state(tasks, buffers)
# exec_task(tasks[1], buffers)
# print_state(tasks, buffers)



