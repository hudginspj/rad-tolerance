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

MPI_Status stat;
int comm_size;


void send_buffer(int rank) {
    char buff[BUFSIZE] = "blah";
    if (rank == 1 || rank == 2) {
        printf("node %d sending: %s\n", rank, buff);

        MPI_Request mpi_req;
        MPI_Isend(buff, RESP_LENGTH, RESP_TYPE, CHIEF_RANK, TAG_RESP, MPI_COMM_WORLD, &mpi_req);
        MPI_Wait(&mpi_req, &stat);
    }
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
    printf("chief got response from %d, content %d\n", stat.MPI_SOURCE, resp.type);

    printf("chief got response from %d, type %d\n", stat.MPI_SOURCE, resp.type); 
    
    return 1;
}


void be_chief() {
    MPI_Status stat;
    printf("Starting as chief \n");

    //chief_check_buffer(0);
    while (1) {
        int flag;
        MPI_Request mpi_req;
        RESPONSE resp;
        MPI_Irecv(&resp, RESP_LENGTH, RESP_TYPE, MPI_ANY_SOURCE, TAG_RESP, MPI_COMM_WORLD, &mpi_req);
        MPI_Test(&mpi_req, &flag, &stat);
        printf("flag %d source %d\n", flag, stat.MPI_SOURCE);
        //chief_handle_response(&mpi_req);
        sleep(1);
    }
    //chief_finalize();

    
}


void main (int argc, char * argv[])
{
    //init_tasks_and_bufs();
    int i, rank;
    char buff[BUFSIZE] = {0};
    
    MPI_Init (&argc, &argv);	
    MPI_Comm_rank (MPI_COMM_WORLD, &rank);
    MPI_Comm_size (MPI_COMM_WORLD, &comm_size);  

    if (rank == 0) {
        be_chief();
    } else {
        send_buffer(rank);
    }

    MPI_Finalize();
    //printf("exit %d\n", rank);
}
