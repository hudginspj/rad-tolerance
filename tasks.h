#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <mpi.h>
#include <assert.h>
#include "md4.h"

//#define BUFSIZE 128
#define HASHSIZE 33
//#define TAG 0
//#define TAG_GOT_DATA 1
#define NUM_BUFS 10

#define INPUTS_PER_TASK 8
#define OUTPUTS_PER_TASK 4

typedef struct{
    //MPI_DATATYPE type;
    int size;
    char *p;
    char is_filled;
    char needed;
    char chief_needs;
} BUF;

// void buf_calloc(BUF *buf) {
//     assert(!buf->is_filled);
//     buf->p = calloc(buf->size, sizeof(char));
// }

// void buf_free(BUF *buf) {
//     free(buf->p);
//     buf->is_filled = 0;
//     buf->p = NULL;
// }
void buf_fill(BUF *buf, char *str);

void inc_all(BUF *inputs, BUF *outputs);
void copy_all(BUF *inputs, BUF *outputs);

void combine(BUF *inputs, BUF *outputs);

typedef struct{
    void (*f)(BUF *,BUF *);
    int input_indexes[INPUTS_PER_TASK];
    int num_inputs;
    int output_indexes[OUTPUTS_PER_TASK];
    int num_outputs;
    char is_done;
    char chief_only;
} TASK;


void exec_task(TASK *task, BUF *bufs);


char check_prereqs(TASK *task, BUF *bufs);

char check_needed(TASK *task, BUF *bufs);

TASK *next_task(TASK *tasks, int num_tasks, BUF *bufs);

void set_needed(TASK *tasks, int num_tasks, BUF *bufs);

void garbage_collect(TASK *tasks, int num_tasks, BUF *bufs, int num_bufs);



