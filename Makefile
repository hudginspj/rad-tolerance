todo: md4.o distributed_task tasks.o task_graph_demo
md4.o: md4.c md4.h
	cc -c md4.c
# isend: isend.c
# 	mpicc isend.c -o isend
# check: check.c md4.o
# 	mpicc check.c md4.o -o check	
# check2: check2.c md4.o
# 	mpicc check2.c md4.o -o check2
# check3: check3.c md4.o tasks.o
# 	mpicc check3.c md4.o tasks.o -o check3	
distributed_task: distributed_task.c md4.o tasks.o
	mpicc distributed_task.c md4.o tasks.o -o distributed_task	
task_graph_demo: task_graph_demo.c
	cc task_graph_demo.c -o task_graph_demo	
tasks: tasks.c
	mpicc tasks.c -o tasks	
tasks.o: tasks.c tasks.h
	mpicc -c tasks.c	
clean:
	rm md4.o distributed_task tasks.o task_graph_demo
