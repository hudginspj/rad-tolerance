
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

def exec_task(task, buffers):
    # Should send to multiple processors
    # Second iteration: figure out which workers are not busy, and send it to them
    # If all workers are busy, wait until they are free
    args = [buffers[key].data for key in task.input_keys]
    out_buffer = buffers[task.output_key]
    out_buffer.data = task.function(*args)
    out_buffer.filled = True


def print_buffers(buffers):
    print("--- Buffers ---")
    for key, buf in buffers.items():
        filled = 'Filled' if buf.filled else ' Empty'
        print(f"{key}, {filled}: {buf.data}")

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
exec_task(tasks[0], buffers)
print_buffers(buffers)
exec_task(tasks[1], buffers)
print_buffers(buffers)


# void exec_task(int task_num, TASK *task, BUF *bufs){
#     BUF inputs[INPUTS_PER_TASK];
#     for (int i = 0; i < task->num_inputs; i++) {
#         inputs[i] = bufs[task->input_indexes[i]];
#     }

#     BUF outputs[OUTPUTS_PER_TASK];
#     for (int i = 0; i < task->num_outputs; i++) {
#         int output_i = task->output_indexes[i];
#         buf_calloc(bufs+output_i);
#         outputs[i] = bufs[output_i];
#     }

#     //printf("%p-%p\n", inputs[0].p, outputs[0].p);
    
#     void (*f)(BUF *,BUF *);
#     f = task->f;
#     f(inputs, outputs);
#     //printf("Task %d completed, first four chars of output buffer: %x%x%x%x\n", task_num, outputs[0].p[0], outputs[0].p[1], outputs[0].p[2], outputs[0].p[3]);
#     int *value = (int *)outputs[0].p;
#     printf("Task %d completed, output buffer as integer: %d\n", task_num, *value);
# }






