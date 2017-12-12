# Pragmatic C99 Code (pragcc)

This tool is a  initiative for a [Source-to-Source Parallelizing Compiler (or transpiler)](https://en.wikipedia.org/wiki/Automatic_parallelization) written in **Python** which relies on the [pycparser](https://github.com/eliben/pycparser) to annotate a C99 source code with OpenMP and OpenACC directives given a metadata file called **Parallel File**.

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

So we create a **Parallel File** called **parallel.yml** as shown below.

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

**Note: The correct paralelization of the program depends of how the Parallel File is defined.**

# Tests

Before performing tests you need to clone [this repository](https://github.com/DonAurelio/pycparser) which is a forked version from the original pycpasrer, copy the content of the **pycparser** folder and place it into the **pragcc/core/parser/c99/pycparser** folder. 

To test the **Pragcc Module**, install its requirements, and perform the tests as follows. Remember to perform the tests form 
the root directory.

```bash
pip3 install -r ./pragcc/requirements.txt
python3 tests/pragcc.py
```

To test the **Pragcc API-REST**, install the api module requirements and init the api server as follows:

```bash
pip3 install -r ./api/requirements.txt
python3 api/app.py
```

The application expose the following endpoints to interact with.

| HTTP Method | URI | Action |
|---|---|---|
| POST | http://[hostname]/pragcc/openmp | Returns a c99 source code annotated with OpenMP directives |


# Deployment with Docker

Perform the following commands to build the **catt** image, then to run the **catt** API in a container. These command need to be 
performed form the catt project root directory.

```sh
docker build -t pragcc .
docker run -d -v ${PWD}:/usr/src/app --name pragcc -p 5001:5001 pragcc
```

# Todo

* Since the parallelization of the C99 code is not automatic, i.e, it is necessary for the user to create the **parallel.yml** file, So we can code a **code analyzer** which analyzes the source code and generates the parallel.yml metadata.

# References

[Structured Parallel Programming: Patterns for Efficient Computation](https://www.amazon.com/Structured-Parallel-Programming-Efficient-Computation/dp/0124159931)

[Designing a RESTful API using Flask-RESTful](https://blog.miguelgrinberg.com/post/designing-a-restful-api-using-flask-restful)

[Flask-RESTful](http://flask-restful.readthedocs.io/en/latest/)

[Designing a RESTful API with Python and Flask](https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask)

[AJAX with jQuery](http://flask.pocoo.org/docs/0.12/patterns/jquery/)

[Flask Examples Github](https://github.com/pallets/flask/tree/master/examples/jqueryexample)

[Google Python Style Guide](http://google.github.io/styleguide/pyguide.html)

[Napoleon - Marching toward legible docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/)
