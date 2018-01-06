RAW_C_CODE = """

#include <stdbool.h>        /* Bool type libary */
#include <stdbool.h>        /* Bool type libary */

#define RowDim 20
#define ColDim 20
#define Generations 20

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
            out[i] = 1;
        }

        temp = in;
        in = out;
        out = temp;
    }
}

int main(){
  return 0;
}
"""

PARALLEL_FILE = """
version: '1.0'
name: 'example'
description: |
  Example of a parallel file. 
functs:
  all:
    - main
    - initialize
    - function
    - neighborhood
    - evolve
  parallel:
    evolve:
      mp:
        parallel:
          scope: 0
          clauses:
            num_threads: int
            shared: [A,B]
            copyin: [C]
        parallel_for:
          - nro: 0
            clauses:
              private: [i,j]
              firstprivate: [i,j]
              lastprivate: [i,j]
              reduction: '+:sum'
              schedule: ['dynamic','1000']
              colapse: '3'
      acc:
        parallel:
          scope: 0
          clauses:
            num_gangs: 1000
            num_workers: 1000
            vector_length: 1000
            private: [i]
            firstprivate: [j]
            reduction: '+:sum'
            gang: '100' # (Optional) num_gangs
            worker: '100' # (Optional) num_workers
            vector: '100' # (Optional) vector_length
        data:
          create: [A,B,C]
          copy: [A,B,C]
          copyin: [A,B,C]
          copyout: [A,B,C]
"""
