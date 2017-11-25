todo: check check2 md4.o
md4.o: md4.c md4.h
	cc -c md4.c
check: check.c md4.o
	mpicc check.c md4.o -o check	
check2: check2.c md4.o
	mpicc check2.c md4.o -o check2	
clean:
	rm hello hello2 hello3 nonblocking scatter gather gather2 reduce checkin
