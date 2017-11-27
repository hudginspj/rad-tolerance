todo: md4.o isend check check2 check3 check4 tasks.o
md4.o: md4.c md4.h
	cc -c md4.c
isend: isend.c
	mpicc isend.c -o isend
check: check.c md4.o
	mpicc check.c md4.o -o check	
check2: check2.c md4.o
	mpicc check2.c md4.o -o check2
check3: check3.c md4.o tasks.o
	mpicc check3.c md4.o tasks.o -o check3	
check4: check4.c md4.o tasks.o
	mpicc check4.c md4.o tasks.o -o check4	
tasks: tasks.c
	mpicc tasks.c -o tasks	
tasks.o: tasks.c tasks.h
	mpicc -c tasks.c	
clean:
	rm md4.o check check2 tasks
