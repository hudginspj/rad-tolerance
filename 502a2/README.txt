

### Local install of mpi4py ###
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py --user
pip3 install --user mpi4py

### Running mpi solution: ###
mpiexec -n 32 ./tsp_mpi.py

The number of processes can be adjusted by adjusting the SPLIT_DEPTH constant 
and the number of cities can be adjusted using the CITIES constant