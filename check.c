#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <mpi.h>
#include "md4.h"

#define BUFSIZE 128
#define TAG 0
#define TAG_GOT_DATA 1



void be_chief(int chief_rank) {

    printf("%d starting\n", chief_rank);

    int first_res;
    char buff[BUFSIZE];
    MPI_Status stat;
    MPI_Recv(buff, BUFSIZE, MPI_CHAR, MPI_ANY_SOURCE, TAG, MPI_COMM_WORLD, &stat);
    first_res = stat.MPI_SOURCE;
    printf("chief got %d first\n", first_res);

    MPI_Bcast (&first_res, 1, MPI_INT, chief_rank, MPI_COMM_WORLD);


}

void check(int rank, int chief_rank, char* buff) {
    int first_res;
    printf("%d starting\n", rank);

    char final_buff[BUFSIZE];

    sprintf(buff, "[Buffer %d data]", rank);
    MPI_Send(buff, BUFSIZE, MPI_CHAR, chief_rank, TAG, MPI_COMM_WORLD);
    printf("%d sent\n", rank);

    MPI_Bcast (&first_res, 1, MPI_INT, chief_rank, MPI_COMM_WORLD);
    printf("Process %d ack %d was first\n", rank, first_res);


    if (first_res == rank) {
        memcpy(final_buff, buff, BUFSIZE);
        //printf("Process %d has final_buff: %s\n", rank, final_buff);
    }


    MPI_Bcast (final_buff, BUFSIZE, MPI_CHAR, first_res, MPI_COMM_WORLD);
    printf("Process %d has final_buff: %s\n", rank, final_buff);
    printf("Testhash: %s\n", MD4(final_buff, 10));
}


void main (int argc, char * argv[])
{
    int i, rank, size;
    char buff[BUFSIZE];
    
    MPI_Status stat;
    MPI_Init (&argc, &argv);	
    MPI_Comm_rank (MPI_COMM_WORLD, &rank);


    // sprintf(buff, "Hello from %d! ", rank);  
    // MPI_Send(buff, BUFSIZE, MPI_CHAR, !rank, TAG, MPI_COMM_WORLD);
    // printf("Message sent by %d: %s\n", rank, buff);
    // MPI_Recv(buff, BUFSIZE, MPI_CHAR, MPI_ANY_SOURCE, TAG, MPI_COMM_WORLD, &stat);
    // printf("Message rccieved by %d from %d: %s\n", rank, stat.MPI_SOURCE, buff);

    // sprintf(buff, "Result from %d! ", rank);
    // MPI_Bcast (buff,BUFSIZE,MPI_CHAR,1,MPI_COMM_WORLD);
    // printf("Common buffer in process %d: %s\n", rank, buff);

    if (rank == 0) {
        be_chief(0);
    } else {
        check(rank, 0, buff);
    }

    MPI_Finalize();
}
