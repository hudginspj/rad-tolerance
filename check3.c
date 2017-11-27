#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <mpi.h>
#include <time.h>
#include "md4.h"

#define BUFSIZE 32
#define HASHSIZE 33
#define TAG 0
#define TAG_GOT_DATA 1
#define GREMLIN_RATE 8

#define CHIEF_RANK 0

#define COMMAND_LENGTH 3
#define COMMAND_TYPE MPI_INT

#define COMMAND_FINALIZE 0
#define COMMAND_TASK 1
#define COMMAND_CHECK_BUFFER 2
#define COMMAND_GET_BUFFER 3
#define COMMAND_SEND_BUFFER 4

MPI_Status stat;
int comm_size;

typedef struct{
    int command;
    int arg1;
    int arg2;
} COMMAND;


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
    COMMAND cmd = {COMMAND_CHECK_BUFFER, 1};
    MPI_Send(&cmd, COMMAND_LENGTH, COMMAND_TYPE, 1, TAG, MPI_COMM_WORLD);
    MPI_Send(&cmd, COMMAND_LENGTH, COMMAND_TYPE, 2, TAG, MPI_COMM_WORLD);

    char hash1[HASHSIZE];
    char hash2[HASHSIZE];
    MPI_Recv(hash1, HASHSIZE, MPI_CHAR, MPI_ANY_SOURCE, TAG, MPI_COMM_WORLD, &stat);
    MPI_Recv(hash2, HASHSIZE, MPI_CHAR, MPI_ANY_SOURCE, TAG, MPI_COMM_WORLD, &stat);
    printf("chief got hashes %s and %s\n", hash1, hash2);
    char check = (!memcmp(hash1, hash2, HASHSIZE));
    printf("check: %d\n", check);
}

void check_buffer(int rank, int buffer) {
    srand(time(NULL)+rank);
    printf("First random %d\n", rand());
    MPI_Status stat;

    char buff[BUFSIZE] = {0};
    bit_gremlin(buff, 8);
    printf("%d buffer: %s\n", rank, buff);

    char hash[HASHSIZE];
    gen_hash(hash, buff, BUFSIZE);
    printf("node %d hash: %s\n", rank, hash);
    MPI_Send(hash, HASHSIZE, MPI_CHAR, CHIEF_RANK, TAG, MPI_COMM_WORLD);
}

void node_run(int rank) {
    srand(time(NULL)+rank);
    printf("First random %d\n", rand());
    
    while (1) {
        COMMAND cmd;
        MPI_Recv(&cmd, COMMAND_LENGTH, COMMAND_TYPE, CHIEF_RANK, TAG, MPI_COMM_WORLD, &stat);
        printf("--Node %d recv cmd %d %d %d\n", rank, cmd.command, cmd.arg1, cmd.arg2);

        if (cmd.command == COMMAND_CHECK_BUFFER) {
            check_buffer(rank, cmd.arg1);
        } else if (cmd.command == COMMAND_FINALIZE) {
            break;
        }
    }
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

    chief_check_buffer(1);
    chief_finalize();

    
}


void main (int argc, char * argv[])
{
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
