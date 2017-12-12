RAW_C_CODE = """

#include <stdbool.h>        /* Bool type libary */
#include <stdbool.h>        /* Bool type libary */

#define RowDim 20
struct Neighborhood
{
    
    bool left;
    
    bool right;
    
    bool up;
    
    bool down;
    
};

void evolve(bool * in, bool * out)
{
    struct Neighborhood nbhd;
    bool * temp = in;

    for (int i = 1; i <= Generations; ++i)
    {
        for (int i = 0; i < (RowDim*ColDim); ++i)
        {
            nbhd = neighborhood(in,i);
            out[i] = function(nbhd);
        }

        temp = in;
        in = out;
        out = temp;
    }
}
"""

PARALLEL_FILE = """
# Note
# The suggested syntax for YAML files is to use 2 spaces for indentation, but YAML will follow whatever indentation system that the individual file uses.
name: 'Name to this parallel file'
description: |
  This is a template of a parallel file. 
functs:
  all: # List the functions available in the source code
    - main
    - initialize
    - function
    - neighborhood
    - evolve
  # Defines just the functions that are paralleizable and how to parallelize them.
  parallel:
    # Function
    evolve:
      # OpenMP direcives
      omp:
        # Parallel directive, apply or enclose the loops defined in the for directive
        parallel:
          # Parallel directive clauses
          num_threads: int
          shared: (A,B)
          copyin: (C)
        # For directive list of loops to parlellize in the function
        for:
          # Loop, the second lexicographic loop inside the function evolve.
          - nro: 1 
            clauses:
              private: [i,j]
              firstprivate: [i,j]
              lastprivate: [i,j]
              reduction: '+:sum'
              schedule: ['dynamic','1000']
              colapse: '3'
          # Loop, the first lexicographic loop inside the function evolve. 
          - nro: 0
            clauses:
              private: [i,j]
      acc:
        # #pragma acc parallel [clause [[,] clause]...] new-line 
        # { structured block }
        parallel: # Parallel and kernels regios can live together
          num_gangs: (expression) # how many parallel gangs are created
          num_workers: (expression) # how many workers are created on each gang
          vector_length: (expression) # Controls the vector length of each worker
          private: (list)
          firstprivate: (list)
          reduction: (operator:list)
          # Clauses unique to openacc parallel region.
          gang: '100' # (Optional) num_gangs
          worker: '100' # (Optional) num_workers
          vector: '100' # (Optional) vector_length
        # #pragma acc kernels [clause [[,] clause]...] new-line 
        # { structured block }
        kernels: # Parallel and kernels regios can live together
        # any data clause is allowed
        data:
          create: [A,B,C] # Data variables must contain the range of information to bring to the GPU A[0:100]
          copy: [A,B,C]
          copyin: [A,B,C]
          copyout: [A,B,C]
        loop:
         - nro: 0
           # parallel: true
           clauses:
             colapse: '3'
             private: [i,j,k]
             reduction: '+:sum'
             # indepedent: True
"""