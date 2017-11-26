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
    for (int i = 0; i < size; i++) {
        b[i]  = a[i] + 1;
    }
}

typedef struct{
    void (*f)(BUF *,BUF *);
    int inputs_indexes[INPUTS_PER_TASK];
    int num_inputs;
    int output_indexes[OUTPUTS_PER_TASK];
    int num_outputs;
} TASK;





void exec_task(TASK *task, BUF *bufs){

    BUF inputs[INPUTS_PER_TASK];
    for (int i = 0; i < task->num_inputs; i++) {
        inputs[i] = bufs[task->inputs_indexes[i]];
    }

    BUF outputs[OUTPUTS_PER_TASK];
    for (int i = 0; i < task->num_outputs; i++) {
        int output_i = task->inputs_indexes[i];
        buf_calloc(bufs+output_i);
        outputs[i] = bufs[output_i];
    }
    
    void (*f)(BUF *,BUF *);
    f = task->f;
    f(inputs, outputs);
    printf("outputs[0].p: %s\n", (outputs[0]).p);

}



void test() {

    BUF bufs[NUM_BUFS];

    for (int i = 0; i < NUM_BUFS; i++) {
        bufs[i].size = 10;
    }
    BUF *a = bufs+2;
    buf_calloc(a);
    //buf_calloc(bufs+3);
    //printf("afefse %d\n", a.p);
    sprintf(a->p, "AAAb");
    a->is_filled = 1;
    printf("a->p: %s\n", a->p);

    void (*f)(BUF *,BUF *);
    f = &inc_all;

    TASK task2 = {
        f,
        {2},
        1,
        {3},
        1
    };

    
    exec_task(&task2, bufs);

}

void gen_hash(char* hash_buff, char *data_buff, int len) {  //TODO just copy if less than len
    char *hash;
    hash = MD4(data_buff, len);
    strcpy(hash_buff, hash);
}

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
    
    MPI_Status stat;
    MPI_Init (&argc, &argv);	
    MPI_Comm_rank (MPI_COMM_WORLD, &rank);

    if (rank == 0) test();
    MPI_Finalize();
    return;


    // sprintf(buff, "Hello from %d! ", rank);  
    // MPI_Send(buff, BUFSIZE, MPI_CHAR, !rank, TAG, MPI_COMM_WORLD);
    // printf("Message sent by %d: %s\n", rank, buff);
    // MPI_Recv(buff, BUFSIZE, MPI_CHAR, MPI_ANY_SOURCE, TAG, MPI_COMM_WORLD, &stat);
    // printf("Message rccieved by %d from %d: %s\n", rank, stat.MPI_SOURCE, buff);

    
    // MPI_Bcast (buff,BUFSIZE,MPI_CHAR,1,MPI_COMM_WORLD);
    // printf("Common buffer in process %d: %s\n", rank, buff);

    if (rank == 0) {
        be_chief(0);
    } else if (rank == 1){
        sprintf(buff, "AAA");
        check(rank, 0, buff);
    } else {
        sprintf(buff, "AAAb");
        check(rank, 0, buff);
    }

    MPI_Finalize();
}
