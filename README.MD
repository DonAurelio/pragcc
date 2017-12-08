# Pragmatic C99 Code (pragcc)

This tool is a Source-to-Source Parallelizing Compiler (or transpiler) which relies on the [pycparser](https://github.com/eliben/pycparser) to annotate a C99 source code with OpenMP and OpenACC directives given a metadata file called **parallel.yml**.

## Example

Suppose we have to parallelize the code of the following function:

```c
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
```

So we create a **parallel.yml** file as shown below.

```yaml
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
          num_threads: '4'
          shared: [C,A,B]
          default: none
        # For directive list of loops to parlellize in the function
        for:
          # Loop, the second lexicographic loop inside the function evolve.
          - nro: 1 
            clauses:
              private: [i,j]
              reduction: '+:sum'
              schedule: ['dynamic','1000']
              colapse: '3'
          # Loop, the first lexicographic loop inside the function evolve. 
          - nro: 0
            clauses:
              private: [i,j]
```

The **pragcc** tool will take the **parallel.yml** and **the source code** to annotate it as shown below:

```c
void evolve(bool * in, bool * out)
{
    struct Neighborhood nbhd;
    bool * temp = in;

    #pragma omp for private(i, j)
    for (int i = 1; i <= Generations; ++i)
    {
        #pragma omp parallel shared(C,A,B) num_threads(4) default(none) 
        {
            #pragma omp for private(i, j) schedule(dynamic, 1000) colapse(3) reduction(+:sum) 
            for (int i = 0; i < (RowDim*ColDim); ++i)
            {
                nbhd = neighborhood(in,i);
                out[i] = function(nbhd);
            }
        }

        temp = in;
        in = out;
        out = temp;
    }
}
```

**Note: The correct paralelization of the program depends of how the file is created.**

# Test Pragcc Module

```bash
pip3 install -r ./pragcc/requirements.txt
python3 -m pragcc.test
```

# Todo

* Since the parallelization of the C99 code is not automatic, i.e, it is necessary for the user to create the **parallel.yml** file, So we can code a **code analyzer** which analyzes the source code and generates the parallel.yml metadata.

# References

[Google Python Style Guide](http://google.github.io/styleguide/pyguide.html)

[Napoleon - Marching toward legible docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/)
