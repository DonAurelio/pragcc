RAW_PALLEL_FILE_PARALLEL_DIRECTIVE = """
version: 1.0
name: 'Test'
description: |
  This is a template of a parallel file. 
functs:
  all:
    - main
    - initialize
    - function
    - neighborhood
    - evolve
  parallel:
    # Function
    evolve:
      # OpenMP direcives
      omp:
        parallel:
          scope: 1
          clauses:
            num_threads: int
            shared: (list)
            copyin: (list)
            default: (shared|none)
"""