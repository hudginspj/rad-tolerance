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


void gen_hash(char* hash_buff, char *data_buff, int len) {  //TODO just copy if less than len
    char *hash;
    hash = MD4(data_buff, len);
    strcpy(hash_buff, hash);
}

void be_chief(int chief_rank) {

    MPI_Status stat;
    printf("%d starting\n", chief_rank);

    // int first_res;
    // char buff[BUFSIZE];
    // MPI_Recv(buff, BUFSIZE, MPI_CHAR, MPI_ANY_SOURCE, TAG, MPI_COMM_WORLD, &stat);
    // first_res = stat.MPI_SOURCE;
    // printf("chief got %d first\n", first_res);
    //MPI_Bcast (&first_res, 1, MPI_INT, chief_rank, MPI_COMM_WORLD);
    // MPI_Recv(buff, HASHSIZE, MPI_CHAR, MPI_ANY_SOURCE, TAG, MPI_COMM_WORLD, &stat);
    // first_res = stat.MPI_SOURCE;
    // printf("chief got %d first\n", first_res);

    char hash1[HASHSIZE];
    char hash2[HASHSIZE];
    MPI_Recv(hash1, HASHSIZE, MPI_CHAR, MPI_ANY_SOURCE, TAG, MPI_COMM_WORLD, &stat);
    MPI_Recv(hash2, HASHSIZE, MPI_CHAR, MPI_ANY_SOURCE, TAG, MPI_COMM_WORLD, &stat);
    printf("chief got hashes %s and %s\n", hash1, hash2);
    char check = (!memcmp(hash1, hash2, HASHSIZE));
    printf("check: %d\n", check);
}


void bit_gremlin(char *buff, int size) {
    for (int i = 0; i < size; i++) {
        if (rand()%GREMLIN_RATE == 0) {
            buff[i] = buff[i] ^ 1;
        }
    }
}


void check(int rank, int chief_rank, char* buff) {
    srand(time(NULL)+rank);
    printf("First random %d\n", rand());


    int first_res;

    bit_gremlin(buff, 8);
    printf("%d buffer: %s\n", rank, buff);

    

    // sprintf(buff, "[Buffer %d data]", rank);
    // MPI_Send(buff, BUFSIZE, MPI_CHAR, chief_rank, TAG, MPI_COMM_WORLD);
    // printf("%d sent\n", rank);

    // MPI_Bcast (&first_res, 1, MPI_INT, chief_rank, MPI_COMM_WORLD);
    // printf("Process %d ack %d was first\n", rank, first_res);


    // if (first_res == rank) {
    //     memcpy(final_buff, buff, BUFSIZE);
    //     //printf("Process %d has final_buff: %s\n", rank, final_buff);
    // }

    // MPI_Bcast (final_buff, BUFSIZE, MPI_CHAR, first_res, MPI_COMM_WORLD);
    // printf("Process %d has final_buff: %s\n", rank, final_buff);
    // printf("Testhash: %s\n", MD4(final_buff, 10));

    char hash[HASHSIZE];
    gen_hash(hash, buff, BUFSIZE);
    printf("node %d hash: %s\n", rank, hash);
    MPI_Send(hash, HASHSIZE, MPI_CHAR, chief_rank, TAG, MPI_COMM_WORLD);

}


void main (int argc, char * argv[])
{
    int i, rank, size;
    char buff[BUFSIZE] = {0};
    
    MPI_Status stat;
    MPI_Init (&argc, &argv);	
    MPI_Comm_rank (MPI_COMM_WORLD, &rank);


    

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
        sprintf(buff, "AAAAAAAAAA");
        check(rank, 0, buff);
    } else {
        sprintf(buff, "AAAAAAAAAA");
        check(rank, 0, buff);
    }

    MPI_Finalize();
}
