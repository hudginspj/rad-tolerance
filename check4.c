#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <mpi.h>
#include <time.h>
#include "md4.h"
#include "tasks.h"

#define BUFSIZE 32
#define HASHSIZE 33
#define TAG 0
#define TAG_GOT_DATA 1
#define TAG_RESP 2
#define TAG_NOOP_RESP 21
#define TAG_BUFFER 3
#define TAG_RESP_BUFFER 3
#define GREMLIN_RATE 8

#define CHIEF_RANK 0


#define RESP_LENGTH (HASHSIZE + 9)
#define RESP_TYPE MPI_CHAR 

typedef struct{
    char type;
    int arg;
    char hash[HASHSIZE];
} RESPONSE;

#define COMMAND_LENGTH 3
#define COMMAND_TYPE MPI_INT

#define COMMAND_FINALIZE 0
#define COMMAND_TASK 1
#define COMMAND_CHECK_BUFFER 2
#define COMMAND_GET_BUFFER 3
#define COMMAND_SEND_BUFFER 4

typedef struct{
    int command;
    int arg1;
    int arg2;
} COMMAND;

MPI_Status stat;
int comm_size;




#define NUM_BUFS 10
#define NUM_TASKS 6
BUF bufs[NUM_BUFS];
TASK tasks[NUM_TASKS];

void init_tasks_and_bufs() {
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

    tasks[0] = (TASK) {&copy_all, {0}, 1, {1}, 1};
    tasks[1] = (TASK) {&inc_all, {0}, 1, {2}, 1};
    tasks[2] = (TASK) {&combine, {0,2}, 2, {3}, 1};
    // tasks[3] = (TASK) {&inc_all, {3}, 1, {4}, 1};
    // tasks[4] = (TASK) {&inc_all, {4}, 1, {5}, 1};
    tasks[3] = (TASK) {&copy_all, {1}, 1, {4}, 1};
    tasks[4] = (TASK) {&copy_all, {4}, 1, {5}, 1};
    tasks[5] = (TASK) {&copy_all, {5}, 1, {1}, 1};

    buf_fill(bufs+0, "AAAA");
    //printf("rank %d buf %p val %s", -1, bufs+0, bufs[0].p);
    
}


void gen_hash(char* hash_buff, char *data_buff, int len) {  //TODO just copy if less than len
    char *hash;
    hash = MD4(data_buff, len);
    strcpy(hash_buff, hash);
}


void bit_gremlin(char *buff, int size) {
    for (int i = 0; i < size; i++) {
        if (rand()%GREMLIN_RATE == 0) {
            buff[i] = buff[i] ^ 1;
        }
    }
}





void chief_check_buffer(int buffer) {
    COMMAND cmd = {COMMAND_CHECK_BUFFER, buffer};
    MPI_Send(&cmd, COMMAND_LENGTH, COMMAND_TYPE, 1, TAG, MPI_COMM_WORLD);
    MPI_Send(&cmd, COMMAND_LENGTH, COMMAND_TYPE, 2, TAG, MPI_COMM_WORLD);

    // char hash1[HASHSIZE];
    // char hash2[HASHSIZE];
    // MPI_Recv(hash1, HASHSIZE, MPI_CHAR, MPI_ANY_SOURCE, TAG, MPI_COMM_WORLD, &stat);
    // MPI_Recv(hash2, HASHSIZE, MPI_CHAR, MPI_ANY_SOURCE, TAG, MPI_COMM_WORLD, &stat);
    // printf("chief got hashes %s and %s\n", hash1, hash2);
    // char check = (!memcmp(hash1, hash2, HASHSIZE));
    // printf("check: %d\n", check);
}



void noop_resp(int rank) {
    char buff[BUFSIZE] = "blah";
    if (1){//rank == 1 || rank == 2) {
        printf("node %d sending noop\n", rank);

        MPI_Request mpi_req;
        MPI_Isend(buff, RESP_LENGTH, RESP_TYPE, CHIEF_RANK, TAG_NOOP_RESP, MPI_COMM_WORLD, &mpi_req);
        MPI_Wait(&mpi_req, &stat);
    }
}

void send_buffer(int rank) {
    char buff[BUFSIZE] = "blah";
    if (1){//rank == 1 || rank == 2) {
        printf("node %d sending: %s\n", rank, buff);

        MPI_Request mpi_req;
        MPI_Isend(buff, RESP_LENGTH, RESP_TYPE, CHIEF_RANK, TAG_RESP, MPI_COMM_WORLD, &mpi_req);
        MPI_Wait(&mpi_req, &stat);
    }
}

void check_buffer(int rank, int buf_i) {
    //char buff[BUFSIZE] = {0};
    char *buf_p = bufs[buf_i].p;
    bit_gremlin(buf_p, 8);
    printf("%d buffer: %s\n", rank, buf_p);

    //char hash[HASHSIZE];
    RESPONSE resp;
    gen_hash(resp.hash, buf_p, BUFSIZE);
    
    //MPI_Send(hash, HASHSIZE, MPI_CHAR, CHIEF_RANK, TAG, MPI_COMM_WORLD);
    
    // if (/*rank == 1 || */rank == 2) {
    //     //if (rank == 1) sleep(2);
    //     printf("node %d sending hash: %s\n", rank, resp.hash);

    //     MPI_Request mpi_req;
    //     //MPI_Send(&resp, RESP_LENGTH, RESP_TYPE, CHIEF_RANK, TAG_RESP, MPI_COMM_WORLD);
    //     MPI_Isend(&resp, RESP_LENGTH, RESP_TYPE, CHIEF_RANK, TAG_RESP, MPI_COMM_WORLD, &mpi_req);
    //     MPI_Wait(&mpi_req, &stat);
    // }
}


void chief_exec_task(int task) {
    COMMAND cmd = {COMMAND_TASK, 1};
    MPI_Send(&cmd, COMMAND_LENGTH, COMMAND_TYPE, 1, TAG, MPI_COMM_WORLD);
    MPI_Send(&cmd, COMMAND_LENGTH, COMMAND_TYPE, 2, TAG, MPI_COMM_WORLD);
}



void node_run(int rank) {
    srand(time(NULL)+rank);
    printf("First random %d\n", rand());
    //send_buffer(3);

    // while (1) {
        COMMAND cmd;
        MPI_Recv(&cmd, COMMAND_LENGTH, COMMAND_TYPE, CHIEF_RANK, TAG, MPI_COMM_WORLD, &stat);
        printf("--Node %d recv cmd %d %d %d\n", rank, cmd.command, cmd.arg1, cmd.arg2);
        //send_buffer(rank);
        noop_resp(rank);

        if (cmd.command == COMMAND_CHECK_BUFFER) {
            send_buffer(rank);
            //check_buffer(rank, cmd.arg1);
        } else if (cmd.command == COMMAND_TASK) {
            exec_task(tasks+cmd.arg1, bufs);
        }
    //     } else if (cmd.command == COMMAND_FINALIZE) {
    //         break;
    //     }
    // }
}


int chief_handle_response(MPI_Request *mpi_req) {
    RESPONSE resp;
    //MPI_Request mpi_req;
    int flag;

    //MPI_Irecv(&resp, RESP_LENGTH, RESP_TYPE, MPI_ANY_SOURCE, TAG_RESP, MPI_COMM_WORLD, &mpi_req);
    MPI_Test(mpi_req, &flag, &stat);
    printf("flag %d\n", flag);
    if (!flag) {
        return 0;
    }
    printf("chief got response from %d, type %d\n", stat.MPI_SOURCE, resp.type);

    printf("chief got response from %d, type %d\n", stat.MPI_SOURCE, resp.type); 
    
    return 1;
}



void chief_finalize() {
    printf("Chief finalizing\n");
    for (int i = 1; i < comm_size; i++) {
        COMMAND cmd = {COMMAND_FINALIZE};
        MPI_Send(&cmd, COMMAND_LENGTH, COMMAND_TYPE, i, TAG, MPI_COMM_WORLD);
    }
}

void be_chief() {
    MPI_Status stat;
    printf("Starting as chief \n");

    chief_check_buffer(0);
    while (1) {
        int flag;
        MPI_Request mpi_req;
        RESPONSE resp;
        MPI_Irecv(&resp, RESP_LENGTH, RESP_TYPE, MPI_ANY_SOURCE, MPI_ANY_TAG, MPI_COMM_WORLD, &mpi_req);
        MPI_Test(&mpi_req, &flag, &stat);
        if (flag && stat.MPI_TAG == 2)
            printf("flag %d source %d tag %d\n", flag, stat.MPI_SOURCE, stat.MPI_TAG);
        //chief_handle_response(&mpi_req);
        sleep(1);
    }
    // while (1) {
    //     MPI_Request mpi_req;
    //     RESPONSE resp;
    //     MPI_Irecv(&resp, RESP_LENGTH, RESP_TYPE, MPI_ANY_SOURCE, TAG_RESP, MPI_COMM_WORLD, &mpi_req);
    //     chief_handle_response(&mpi_req);
    //     sleep(1);
    // }
    chief_finalize();

    
}


void main (int argc, char * argv[])
{
    init_tasks_and_bufs();
    int i, rank;
    char buff[BUFSIZE] = {0};
    
    MPI_Init (&argc, &argv);	
    MPI_Comm_rank (MPI_COMM_WORLD, &rank);
    MPI_Comm_size (MPI_COMM_WORLD, &comm_size);  

    if (rank == 0) {
        be_chief();
    } else {
        node_run(rank);
    }

    MPI_Finalize();
    //printf("exit %d\n", rank);
}
