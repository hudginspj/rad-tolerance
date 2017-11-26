#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <mpi.h>
#include "md4.h"

#define BUFSIZE 128
#define HASHSIZE 33
#define TAG 0
#define TAG_GOT_DATA 1
#define NUM_BUFS 10

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
    buf->p = calloc(buf->size, sizeof(char));
}

void buf_free(BUF *buf) {
    free(buf->p);
    buf->is_filled = 0;
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
    c[a_size-1] = 'X';
    for (int i = 0; i < b_size; i++) {
        c[a_size + i]  = b[i];
    }
}

typedef struct{
    void (*f)(BUF *,BUF *);
    int input_indexes[INPUTS_PER_TASK];
    int num_inputs;
    int output_indexes[OUTPUTS_PER_TASK];
    int num_outputs;
    char is_done;
} TASK;





void exec_task(TASK *task, BUF *bufs){
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
    printf("outputs[0].p: %s\n", (outputs[0]).p);
}

void exec_and_check(TASK *task, BUF *bufs) {
    exec_task(task, bufs);
    for (int i = 0; i < task->num_outputs; i++) {
        int output_i = task->output_indexes[i];
        bufs[output_i].is_filled = 1;
    }
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

TASK *next_task(TASK *tasks, int num_tasks, BUF *bufs) {


    for (int i = 0; i < num_tasks; i++) {
        //char needed = check_needed(tasks + i, bufs);
        char prereqs = check_prereqs(tasks + i, bufs);
        //printf("%i/%i ", needed, prereqs);
        if (!tasks[i].is_done && prereqs) {
            //printf("\n");
            return tasks + i;
        }
    }
    //printf("\n");
    return NULL;
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
        printf(" %i:", tasks[i].is_done);
        if (!tasks[i].is_done){
            for (int j = 0; j < tasks[i].num_inputs; j++){
                int input_j = tasks[i].input_indexes[j];
                printf("%i:", input_j);
                bufs[input_j].needed = 1;
            }
        }
    }
    printf(":done\n");
    for (int i = 0; i < num_bufs; i++) {
        BUF *buf = bufs + i;
        if (buf->is_filled && !buf->needed) {
            //printf("freeing %i\n", i);
            buf_free(bufs + i);
        }
    }
}



void test2() {

    BUF bufs[NUM_BUFS];

    for (int i = 0; i < NUM_BUFS; i++) {
        bufs[i].size = 10;
        bufs[i].is_filled = 0;
        bufs[i].p = NULL;
    }
    bufs[0].size = 5;
    bufs[1].size = 5;
    bufs[2].size = 5;
    bufs[3].size = 10;
    //bufs[4].size = 10;
    bufs[4].size = 5;
    bufs[5].size = 5;

    BUF *a = bufs+0;
    buf_calloc(a);
    sprintf(a->p, "AAAA");
    a->is_filled = 1;
    printf("buf 0: %s\n", a->p);

    int NUM_TASKS = 6;
    TASK tasks[NUM_TASKS];
    tasks[0] = (TASK) {&copy_all, {0}, 1, {1}, 1};
    tasks[1] = (TASK) {&inc_all, {0}, 1, {2}, 1};
    tasks[2] = (TASK) {&combine, {0,2}, 2, {3}, 1};
    // tasks[3] = (TASK) {&inc_all, {3}, 1, {4}, 1};
    // tasks[4] = (TASK) {&inc_all, {4}, 1, {5}, 1};
    tasks[3] = (TASK) {&copy_all, {1}, 1, {4}, 1};
    tasks[4] = (TASK) {&copy_all, {4}, 1, {5}, 1};
    tasks[5] = (TASK) {&copy_all, {5}, 1, {1}, 1};
    

    // exec_task(&tasks[0], bufs);
    // exec_task(&tasks[1], bufs);
    // exec_task(&tasks[2], bufs);
    // exec_task(&tasks[3], bufs);

    set_needed(tasks, NUM_TASKS, bufs);
    TASK *next = next_task(tasks, NUM_TASKS, bufs);
    while (next != NULL) {
        exec_and_check(next, bufs);
        set_needed(tasks, NUM_TASKS, bufs);

        garbage_collect(tasks, NUM_TASKS, bufs, 6);
        next = next_task(tasks, NUM_TASKS, bufs);

        for (int i = 0; i < 6; i++) {
            printf("%i ", bufs[i].needed);
        }
        printf(":needed\n");
        for (int i = 0; i < 6; i++) {
            printf("%i ", bufs[i].is_filled);
        }
        printf(":filled\n");
        
        }
        for (int i = 0; i < NUM_TASKS; i++) {
            printf(" %i:", tasks[i].is_done);
            if (!tasks[i].is_done){
                for (int j = 0; j < tasks[i].num_inputs; j++){
                    int input_j = tasks[i].input_indexes[j];
                    printf("%i:", input_j);
                }
            }
        }
        printf(":is_done\n");

}

// void test() {

//     BUF bufs[NUM_BUFS];

//     for (int i = 0; i < NUM_BUFS; i++) {
//         bufs[i].size = 10;
//     }
//     BUF *a = bufs+2;
//     buf_calloc(a);
//     //buf_calloc(bufs+3);
//     //printf("afefse %d\n", a.p);
//     sprintf(a->p, "AAAb");
//     a->is_filled = 1;
//     printf("a->p: %s\n", a->p);


//     TASK task2 = {&inc_all, {2}, 1, {3}, 1};
    
//     exec_task(&task2, bufs);
// }


// void be_chief(int chief_rank) {

//     MPI_Status stat;
//     printf("%d starting\n", chief_rank);

//     char hash1[HASHSIZE];
//     char hash2[HASHSIZE];
//     MPI_Recv(hash1, HASHSIZE, MPI_CHAR, MPI_ANY_SOURCE, TAG, MPI_COMM_WORLD, &stat);
//     MPI_Recv(hash2, HASHSIZE, MPI_CHAR, MPI_ANY_SOURCE, TAG, MPI_COMM_WORLD, &stat);
//     printf("chief got hashes %s and %s\n", hash1, hash2);
//     char check = (!memcmp(hash1, hash2, HASHSIZE));
//     printf("check: %d\n", check);
// }



// void check(int rank, int chief_rank, char* buff) {
//     int first_res;
//     printf("%d starting\n", rank);

    

//     char hash[HASHSIZE];
//     gen_hash(hash, buff, HASHSIZE);
//     printf("node %d hash: %s\n", rank, hash);
//     MPI_Send(hash, HASHSIZE, MPI_CHAR, chief_rank, TAG, MPI_COMM_WORLD);

// }


void main (int argc, char * argv[])
{
    int i, rank, size;
    char buff[BUFSIZE] = {0};
    
    //test2();

    MPI_Status stat;
    MPI_Init (&argc, &argv);	
    MPI_Comm_rank (MPI_COMM_WORLD, &rank);

    if (rank == 0) test2();
    MPI_Finalize();
    return;

    MPI_Finalize();
}
