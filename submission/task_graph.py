from checking import *



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
        output_buffer = buffers[task.output_key]
        task.done = output_buffer.filled
        if not task.done:
            for input_key in task.input_keys:
                buffers[input_key].needed = True  
    for key, buffer in buffers.items():
        if buffer.filled and not buffer.needed:
            buffer.filled = False
            buffer.data = None




def cycle(tasks):
    errors = 0
    if (rank != 0):
        run_worker()
        return           
    else:
        buffers = buffers_from_tasks(tasks)
        while True:
            print_state(tasks, buffers)
            next_t = next_task(tasks, buffers)

            errors += exec_task(next_t, buffers)

            if buffers['quit'].data == True:
                print_state(tasks, buffers)
                exit_all()
                return errors
                
            garbage_collect(tasks, buffers)
  

if __name__ == "__main__":

    # Tasks which find the maximum value in three buffers
    merge_tasks = [
        Task('A', lambda x: 5, 'init'),
        Task('B', lambda x: 10, 'init'),
        Task('C', lambda x: 15, 'init'),
        Task('D', max, 'A','B'),
        Task('E', max, 'C','D')
        Task('quit', lambda x: True, 'E')
    ]

    cycle(merge_tasks)


