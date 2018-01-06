# -*- coding: utf-8 -*-
"""Data used for testing.

This module was created to specify test data.

"""

import os


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DIR = os.path.join(BASE_DIR,'files')


PARALLEL_FILE_PATH = os.path.join(TEST_DIR,'parallel.yml')

# This file contains the basic main function.
# This code is expected to be parsed correctly,
# but it can be splited.
BASIC_FILE_PATH = os.path.join(TEST_DIR,'basic.c')

# This file contains an elaborated code that
# can be parsed and splited correctly. 
COMPLEX_FILE_PATH = os.path.join(TEST_DIR,'complex.c')

# This file contains no code. So this is expected to
# be parsed correctly but it can not be splitted.
EMPTY_FILE_PATH = os.path.join(TEST_DIR,'empty.c')

# On this code is used the bool type that is not supported
# in c99, so this code can not be parsed correctly.
UNSUPPORTED_CODE_FILE_PATH_1 = os.path.join(TEST_DIR,'bool_type_1.c')

# On this code is used the bool type that is not supported
# in c99, so we add the stdbool as the first include, but
# this include in moved out by a preprocessing step (fakeing)
# performed before code parsing. So the parser will not
# recognize the bool type again, as a result this code 
# can not be parsed correctly.
UNSUPPORTED_CODE_FILE_PATH_2 = os.path.join(TEST_DIR,'bool_type_2.c')

# The following code despict a possible fix to the bool type
# error depicted in ERROR_FILE_PATH_1 and ERROR_FILE_PATH_2
SUPPORTED_CODE_FILE_PATH = os.path.join(TEST_DIR,'bool_type_3.c')

# This code can be parsed but it can not be splited 
# because the ccode requires the code must be divided 
# in three sections: includes, definitions, and functions.
SIMPLE_CODE = """
int main(){
    for(int i; i < 10; ++i){
        // code here ...
    }
    return 0;
}
"""

# Includes section can not be empty, and needs at least
# two includes to work properly, the definition section 
# can be empty, and the functions secction need the
# at least the main function.
# On the other hand the following code 
# can be parsed and splitted correctly.
SIMPLE_CODE_ALLOWED_FORMAT_1 = """
/* includes */
#include <stdlib.h>
#include <stdio.h>

/* definitions */

/* functions */
int main(){
    return 0;
}
"""

# This code can be pased and splited 
# correctly.
SIMPLE_CODE_ALLOWED_FORMAT_2 = """
/* includes */
#include <stdlib.h>
#include <stdio.h>

/* definitions */
#define N 10

/* functions */
int main(){
    return 0;
}
"""

# This code can be pased and splited 
# correctly.
SIMPLE_CODE_FUNCTION_LOOP = """
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
"""

# Metadata needed for SIMPLE_CODE_FUNCTION_LOOP code 
# parallelization It is used by OpenMP and OpenACC 
# parallelizers
METADATA_FOR_SIMPLE_CODE_FUNCTION_LOOP = {
    'vesion': 1.0,
    'name': 'Example',
    'description': 'Parallel file example',
    'functs': {
        'all': ['main','some_function'],
        'parallel': {
            'some_function': {
                'mp': {
                    'parallel':{
                        'scope':0,
                        'clauses': {
                            'num_threads': 4,
                            'shared': ['A','B','C'],
                            'default': 'none'
                        }
                    },
                    'parallel_for': [
                        # Directive With clauses 
                        {
                            'nro':0,
                            'clauses': {
                                'private': ['i'],
                                'reduction': '+:sum',
                                'colapse': 3
                            }
                        },
                        {
                            'nro': 2,
                            'clauses': {
                                'private': ['i']
                            }
                        }
                    ]
                },
                'acc': {
                    'data': {
                        'scope': 0,
                        'clauses': {
                            'copy': ['A','B','C']
                        }
                    },
                    'parallel_loop': [
                        {
                            'nro': 0,
                            'clauses': {
                                'num_gangs': 100,
                                'num_workers': 100,
                                'gang': None,
                                'vector': None
                            }
                        }
                    ],
                    'loop': [
                        {
                            'nro': 0,
                            'clauses': {
                                'num_gangs': 100,
                                'num_workers': 100,
                                'vector': None
                            }
                        }
                    ],
                } 
            }
        }
    }
}

METADATA_FOR_SIMPLE_CODE_FUNCTION_LOOP_WITH_ERRORS = {
    'vesion': 1.0,
    'name': 'stencil',
    'description': 'Linealized matrix template with stencil parallel programming pattern. ...',
    'functs': {
        'all': ['main','some_function'],
        'parallel': {
            'some_function': {
                'mp': {
                    'parallel':{
                        # The parallel directive enclose 
                        # the loop given by the scope key.
                        # The first loop in the code
                        # is the loop number 0, then the
                        # loop nro does not exists
                        'scope': 2,
                        'clauses': {
                            'num_threads': 4,
                            'shared': ['A','B','C'],
                            'default': 'none'
                        }
                    }
                } 
            }
        }
    }
}
