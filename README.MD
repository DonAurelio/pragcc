# #pragcc - Pragmatic C99 Source Code

[![Build Status](https://travis-ci.org/DonAurelio/pragcc.svg?branch=master)](https://travis-ci.org/DonAurelio/pragcc)

This tool is an initiative for a [Source-to-Source Parallelizing Compiler](https://en.wikipedia.org/wiki/Automatic_parallelization) that creates human readable paralleization metadata. This tool is  written in **Python** which relies on the [pycparser](https://github.com/eliben/pycparser) to annotate C99 source code with OpenMP and OpenACC directives given a metadata file called **parallel.yml**.

## A Brew Example

Suppose we have to parallelize the code of the following function:

```c
#include <stdlib.h>
#include <stdio.h>

#define N 10

void some_function(){

    int A[N];
    int B[N];
    int C[N];

    for(int i=0; i<N; ++i){
        C[i] = A[i] + B[i];
    }    
}

int main(){
    some_function();
}
```

So we create a **parallel.yml** as shown below.

```yaml
version: 1.0
name: 'example'
description: |
  This is a template of a parallel file. 
functs:
  all: # List the functions available in the source code
    - main
    - some_function
  # Defines just the functions that are paralleizable and how to parallelize them.
  parallel:
    # Function
    evolve:
      # OpenMP direcives
      mp:
        # Parallel directive, apply or enclose the loops defined in the for directive
        parallel_for:
          # Loop, the first lexicographic loop inside the function some_function.
          - nro: 0
            clauses:
              private: [i]
              reduction: '+:sum'
```

**#pragcc** takes the **parallel.yml** and **the source code** to annotate it as shown below:

```c
#include <stdlib.h>
#include <stdio.h>

#define N 10

void some_function(){

    int A[N];
    int B[N];
    int C[N];
    
    #pragma omp parallel for private(i) reduction(+:sum)
    for(int i=0; i<N; ++i){
        C[i] = A[i] + B[i];
    }    
}

int main(){
    some_function();
}
```

**Note: The correct paralelization of the program depends of how the Parallel File is defined.**

## Running the application

### API-REST

To test the **Pragcc API-REST**, install the api module requirements and init the api server as follows:

```bash
pip3 install -r ./api/requirements.txt
python3 api/app.py
```

### Docker Container

Perform the following commands to build the **pragcc** image, then to run the **pragcc** API in a container. These commands need to be performed from the pragcc project root directory.

```sh
docker build -t pragcc .
docker run -d -v ${PWD}:/usr/src/app --name pragcc -p 5001:5001 pragcc
```

## Known Issues

* The is not errors handling.
* If the parallel.yml file has not a correct format the annotation process can fail or the resulted code is not annotated. So the user needs to know what happend.
* The code to parallelize must be c99 source code. which is the version of C supported by **pycpasrer**.
* The code must have at least two **include headers**.
* The code should be organized as follows.

```c
/* Headers */
#include <stdlib.h>         /* Standard Library: malloc, calloc, free, ralloc */
#include <stdbool.h>        /* Bool type libary */

/* Declarations */
#define RowDim 20

/* Functions */
int main(int argc, char const **argv)
{
    return EXIT_SUCCESS;
}
```

## Todo

- [ ] Since the parallelization of the C99 code is not automatic, i.e, it is necessary for the user to create the **parallel.yml** file, So we can code a **code analyzer** which analyzes the source code and generates the parallel.yml metadata.
- [ ] Solve **include headers** issue.
- [ ] Add error handling.

## References

[Structured Parallel Programming: Patterns for Efficient Computation](https://www.amazon.com/Structured-Parallel-Programming-Efficient-Computation/dp/0124159931)

[Designing a RESTful API using Flask-RESTful](https://blog.miguelgrinberg.com/post/designing-a-restful-api-using-flask-restful)

[Flask-RESTful](http://flask-restful.readthedocs.io/en/latest/)

[Designing a RESTful API with Python and Flask](https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask)

[AJAX with jQuery](http://flask.pocoo.org/docs/0.12/patterns/jquery/)

[Flask Examples Github](https://github.com/pallets/flask/tree/master/examples/jqueryexample)

[Google Python Style Guide](http://google.github.io/styleguide/pyguide.html)

[Napoleon - Marching toward legible docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/)
