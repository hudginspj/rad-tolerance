#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <assert.h>
#include <time.h>
// #include <mpi.h>
// #include "md4.h"

//#define BUFSIZE 128
//#define HASHSIZE 33
//#define TAG 0
//#define TAG_GOT_DATA 1


#define INPUTS_PER_TASK 8
#define OUTPUTS_PER_TASK 4



typedef struct{
    //MPI_DATATYPE type;
    int size;
    char *p;
    char is_filled;
    char needed;
} BUF;

void buf_calloc(BUF *buf) {
    assert(!buf->is_filled);
    buf->p = calloc(buf->size, sizeof(char));
}

void buf_free(BUF *buf) {
    free(buf->p);
    buf->is_filled = 0;
    buf->p = NULL;
}
void buf_fill(BUF *buf, char *str){
    buf_calloc(buf);
    sprintf(buf->p, str);
    buf->is_filled = 1;
}
void buf_int_fill(BUF *buf, int num){
    buf_calloc(buf);
    int *value = (int *) buf->p;
    *value = num;
    buf->is_filled = 1;
}



typedef struct{
    void (*f)(BUF *,BUF *);
    int input_indexes[INPUTS_PER_TASK];
    int num_inputs;
    int output_indexes[OUTPUTS_PER_TASK];
    int num_outputs;
    char is_done;
} TASK;



void exec_task(int task_num, TASK *task, BUF *bufs){
    BUF inputs[INPUTS_PER_TASK];
    for (int i = 0; i < task->num_inputs; i++) {
        inputs[i] = bufs[task->input_indexes[i]];
    }

    BUF outputs[OUTPUTS_PER_TASK];
    for (int i = 0; i < task->num_outputs; i++) {
        int output_i = task->output_indexes[i];
        buf_calloc(bufs+output_i);
        outputs[i] = bufs[output_i];
    }

    //printf("%p-%p\n", inputs[0].p, outputs[0].p);
    
    void (*f)(BUF *,BUF *);
    f = task->f;
    f(inputs, outputs);
    //printf("Task %d completed, first four chars of output buffer: %x%x%x%x\n", task_num, outputs[0].p[0], outputs[0].p[1], outputs[0].p[2], outputs[0].p[3]);
    int *value = (int *)outputs[0].p;
    printf("Task %d completed, output buffer as integer: %d\n", task_num, *value);
}

void exec_and_check(int task_num, TASK *task, BUF *bufs) {
    exec_task(task_num, task, bufs);
    for (int i = 0; i < task->num_outputs; i++) {
        int output_i = task->output_indexes[i];
        bufs[output_i].is_filled = 1;
    }
}


int find_task_for_output(TASK *tasks, int num_tasks, int buf_num) {
    for (int i = 0; i < num_tasks; i++) {
        for (int j = 0; j < tasks[i].num_outputs; j++) {
            if (tasks[i].output_indexes[j] == buf_num) return i;
        }
    }
    return -1;
}

char check_prereqs(TASK *task, BUF *bufs) {
    char prereqs_met = 1;
    for (int i = 0; i < task->num_inputs; i++) {
        int input_i = task->input_indexes[i];
        prereqs_met &= bufs[input_i].is_filled;
    }
    return prereqs_met;
}

char check_needed(TASK *task, BUF *bufs) {
    char output_needed = 0;
    for (int i = 0; i < task->num_outputs; i++) {
        int output_i = task->output_indexes[i];
        output_needed |= !bufs[output_i].is_filled;
    }
    return output_needed;
}

int next_task(TASK *tasks, int num_tasks, BUF *bufs) {
    for (int i = 0; i < num_tasks; i++) {
        //char needed = check_needed(tasks + i, bufs);
        char prereqs = check_prereqs(tasks + i, bufs);
        //printf("%i/%i ", needed, prereqs);
        if (!tasks[i].is_done && prereqs) {
            //printf("\n");
            return i;
        }
    }
    //printf("\n");
    return -1;
}

void set_needed(TASK *tasks, int num_tasks, BUF *bufs) {
    for (int i = 0; i < num_tasks; i++) {
        tasks[i].is_done = !check_needed(tasks + i, bufs);
    }
}

void garbage_collect(TASK *tasks, int num_tasks, BUF *bufs, int num_bufs) {
    for (int i = 0; i < num_bufs; i++) {
        bufs[i].needed = 0;
    }
    for (int i = 0; i < num_tasks; i++) {
        //printf(" %i:", tasks[i].is_done);
        if (!tasks[i].is_done){
            for (int j = 0; j < tasks[i].num_inputs; j++){
                int input_j = tasks[i].input_indexes[j];
                //printf("%i:", input_j);
                bufs[input_j].needed = 1;
            }
        }
    }
    //printf(":done\n");
    for (int i = 0; i < num_bufs; i++) {
        BUF *buf = bufs + i;
        if (buf->is_filled && !buf->needed) {
            //printf("freeing %i\n", i);
            buf_free(bufs + i);
        }
    }
}


void inc_all(BUF *inputs, BUF *outputs) {
    char *a = inputs[0].p;  //NOTE, copy
    char *b = outputs[0].p;
    int size = inputs[0].size;
    for (int i = 0; i < size-1; i++) {
        b[i]  = a[i] + 1;
    }
    b[size-1] = a[size-1];
}


void copy_all(BUF *inputs, BUF *outputs) {
    char *a = inputs[0].p;  //NOTE, copy
    char *b = outputs[0].p;
    int size = inputs[0].size;
    for (int i = 0; i < size; i++) {
        b[i]  = a[i];
    }
}
void combine(BUF *inputs, BUF *outputs) {
    char *a = inputs[0].p;  //NOTE, copy
    char *b = inputs[1].p;
    char *c = outputs[0].p;
    int a_size = inputs[0].size;
    int b_size = inputs[1].size;
    for (int i = 0; i < a_size; i++) {
        c[i]  = a[i];
    }
    //printf("%s / %s\n", a, c);
    c[a_size-1] = a[a_size-2];
    for (int i = 0; i < b_size; i++) {
        c[a_size + i]  = b[i];
    }
}

void map(BUF *inputs, BUF *outputs) {
    int *a = (int *)inputs[0].p;  //NOTE, copy
    int *b = (int *)outputs[0].p;
    *b = *a * 3;
}

void reduce(BUF *inputs, BUF *outputs) {
    int *a = (int *)inputs[0].p;  //NOTE, copy
    int *b = (int *)inputs[1].p;
    int *c = (int *)outputs[0].p;
    //printf("a&b %d %d\n", *a, *b);
    *c = *a + *b;
}
void transmit(BUF *inputs, BUF *outputs) {
    int *a = (int *)inputs[0].p;
    printf("Map/reduce done, transmitting: %d\n", *a);
}

void run(BUF *bufs, int NUM_BUFS, TASK *tasks, int NUM_TASKS) {
    set_needed(tasks, NUM_TASKS, bufs);
    int task_num = next_task(tasks, NUM_TASKS, bufs);
    while (task_num >= 0) {

        usleep(500000);

        exec_and_check(task_num, tasks+task_num, bufs);
        set_needed(tasks, NUM_TASKS, bufs);

        garbage_collect(tasks, NUM_TASKS, bufs, 6);
        task_num = next_task(tasks, NUM_TASKS, bufs);

        // for (int i = 0; i < 6; i++) {
        //     printf("%i ", bufs[i].needed);
        // }
        // printf(":needed\n");
        printf("filled buffers: ");
        for (int i = 0; i < NUM_BUFS; i++) {
            printf("%i,", bufs[i].is_filled);
        }
        printf("\n");
    }
        
        // for (int i = 0; i < NUM_TASKS; i++) {
        //     printf(" %i:", tasks[i].is_done);
        //     if (!tasks[i].is_done){
        //         for (int j = 0; j < tasks[i].num_inputs; j++){
        //             int input_j = tasks[i].input_indexes[j];
        //             printf("%i:", input_j);
        //         }
        //     }
        // }
        // printf(":is_done\n");
}


void make_task_graph(BUF **buf_ret, int *num_bufs, TASK **tasks_ret, int *num_tasks){
    int NUM_BUFS = 36;
    int NUM_TASKS = 25;
    BUF *bufs = calloc(NUM_BUFS, sizeof(BUF));
    TASK *tasks = calloc(NUM_TASKS, sizeof(TASK));

    for (int i = 0; i < NUM_BUFS; i++) {
        bufs[i].size = 5;
    }

    /* populate buffers with integers for mapping */
    for (int i = 6; i < 16; i++){
        buf_int_fill(bufs+i, i);
    }
    /* Apply map function (x = x*3) to each of the above buffers */
    for (int i = 0; i < 10; i++) {   
        tasks[i+0] = (TASK) {&map, {i+6}, 1, {i+16}, 1};
    }
    /* Reduce the above buffers with addition */
    for (int i = 0; i < 10; i++) {   
        tasks[i+10] = (TASK) {&reduce, {i+25, 24-i}, 2, {i+26}, 1};
    }
    
    /*infine loop */
    buf_fill(bufs+0, "AAAA");
    tasks[21] = (TASK) {&copy_all, {0}, 1, {1}, 1};
    tasks[22] = (TASK) {&copy_all, {1}, 1, {4}, 1};    /* Tasks 22, 23, and 24 form an infininte loop */
    tasks[23] = (TASK) {&copy_all, {4}, 1, {5}, 1};
    tasks[24] = (TASK) {&copy_all, {5}, 1, {1}, 1};


    *buf_ret = bufs;
    *tasks_ret = tasks;
    *num_bufs = NUM_BUFS;
    *num_tasks = NUM_TASKS;
}

void main (int argc, char * argv[])
{
    BUF *bufs;
    TASK *tasks;
    int num_bufs;
    int num_tasks;
    make_task_graph(&bufs, &num_bufs, &tasks, &num_tasks);
    run(bufs, num_bufs, tasks, num_tasks);

}
