This project requires Python 3, MPI, and the python modules dill and mpi4py.

### Installing prereqs on class server ###
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py --user
pip3 install --user mpi4py dill


The experiments module has four parameters:
    - Task time
    - Half-error time
    - Repititons
    - Redundancy

### Running an experiment ###
mpiexec -n 4 python3 experiments.py 0.1 1.0 30 2




