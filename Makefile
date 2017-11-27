todo: md4.o check check2 check3 tasks
md4.o: md4.c md4.h
	cc -c md4.c
check: check.c md4.o
	mpicc check.c md4.o -o check	
check2: check2.c md4.o
	mpicc check2.c md4.o -o check2
check3: check3.c md4.o
	mpicc check3.c md4.o -o check3	
tasks: tasks.c md4.o
	mpicc tasks.c md4.o -o tasks	
clean:
	rm md4.o check check2 tasks
