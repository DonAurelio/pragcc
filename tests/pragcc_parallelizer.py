# -*- encoding: utf-8 -*-

from pragcc.core import parallelizer
from pragcc.core import metadata
from pragcc.core import code
from pragcc.core.parser.c99.pycparser.plyparser import ParseError
from . import utils

from . import utils
import unittest
import os


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DIR = os.path.join(BASE_DIR,'files')


SIMPLE_RAW_CODE = """0
1 int main(){
2    for(int i; i < 10; ++i){
3
4    }
5 }
"""


class TestBaseParallelizer(unittest.TestCase):

    def setUp(self):
        self._base_parallelizer = parallelizer.BaseParallelizer()

    def test_insert_lines_in_raw_code(self):
        """ Test the code insertion function.

        Example:

            Before insertion

            0
            1 int main(){
            2    for(int i; i < 10; ++i){
            3
            4    }
            5 }
            ---------------------------------

            After insertions

            0
            1 First insertion
            2 int main(){
            3 Second insertion
            4    for(int i; i < 10; ++i){
            5
            6    }
            7 }

        """

        insertions = [
            ('First insertion',1),
            ('Second insertion',2)
        ]

        new_raw = self._base_parallelizer.insert_lines(
            SIMPLE_RAW_CODE,
            insertions
        )

        line_1 = new_raw.splitlines()[1]
        line_2 = new_raw.splitlines()[3]

        self.assertEqual(line_1,'First insertion')
        self.assertEqual(line_2,'Second insertion')

    def test_insert_in_invalid_position(self):
        """ 
        When insertions have no valid postions, it means
        no insertions are performed, in that case, an empty
        string is returned.
        """

        insertions = [
            ('First insertion',-1),
            ('Second insertion',-1)
        ]

        new_raw = self._base_parallelizer.insert_lines(
            SIMPLE_RAW_CODE,
            insertions
        )

        self.assertEqual(new_raw,'')


    def test_insert_at_least_one_valid_position(self):
        """ 
        When at least one insertion in the insertions list
        has an invalid position, and empty string is returned.

        This is a good behavior, if the result of the program
        is correct only when all the inserts are carried out
        successfully.
        """

        insertions = [
            ('First insertion',1),
            ('Second insertion',-2)
        ]

        new_raw = self._base_parallelizer.insert_lines(
            SIMPLE_RAW_CODE,
            insertions
        )

        self.assertEqual(new_raw,'')

    def test_insert_in_an_empty_string(self):
        """ 
            Inserting code in and empty string. 
        """

        empty_raw = ''

        insertions = [
            ('First insertion',1),
            ('Second insertion',2)
        ]

        new_raw = self._base_parallelizer.insert_lines(
            empty_raw,
            insertions
        )

        self.assertEqual(new_raw,'')

    def test_not_implemented_methods(self):
        with self.assertRaises(NotImplementedError):
            self._base_parallelizer.get_raw_pragma(
                directive_name='parallel',
                clauses={}
            )
            self._base_parallelizer.insert_directives(
                function_name='some_function',
                directives={}
            )
            self._base_parallelizer.parallelize(metadata=None)


class TestOpenMPObjectCreation(unittest.TestCase):

    def setUp(self):

        # Set of files to test code annotation with OpenMP directives
        self._basic = os.path.join(TEST_DIR,'basic.c')
        self._complex = os.path.join(TEST_DIR,'complex.c')
        self._empty = os.path.join(TEST_DIR,'empty.c')
        self._bool_type_1 = os.path.join(TEST_DIR,'bool_type_1.c')
        self._bool_type_2 = os.path.join(TEST_DIR,'bool_type_2.c')
        self._bool_type_3 = os.path.join(TEST_DIR,'bool_type_3.c')

    def tearDown(self):

        # Clean intermediate files created during code annotation
        utils.purge(TEST_DIR,r'^fake_*')
        utils.purge(TEST_DIR,r'^mp_*')
        utils.purge(TEST_DIR,r'^ccode_*')
        utils.purge(TEST_DIR,r'^acc_*')

    def test_openmp_object_from_basic_code_file(self):
        """
            To create ccode objects , the given code must follow 
            the following struture

            #include <...>
            #include <...>

            #define ....

            
            function_1(){
        
            }

            int main(){
        
            }

            if the given code do not follow this structure it can 
            not be splited in sections, because the code does not
            have that sections, then an IndexError takes place.
        """
        with self.assertRaises(IndexError):
            omp = parallelizer.OpenMP(file_path=self._basic)

    def test_openmp_object_from_complex_code_file(self):
        omp = parallelizer.OpenMP(file_path=self._complex)
        self.assertIsInstance(omp,parallelizer.OpenMP)

    def test_openmp_object_from_empty_code_file(self):
        with self.assertRaises(IndexError):
            omp = parallelizer.OpenMP(file_path=self._empty)

    def test_openmp_object_from_unssupported_type_code_file(self):
        """ 
            The C preprocessor used by pycparse for code parsing do not support
            the bool type natively, if the preprocessor find an unknwon type, the
            code parsing cann not take place.
        """
        with self.assertRaises(ParseError):
            omp = parallelizer.OpenMP(file_path=self._bool_type_1)

    def test_openmp_object_from_include_bool_type_file(self):
        """ 
            We include the stdbool.h header library on which the bool 
            type is defined. Thus, the C preprocessor will recognize
            the bool type.

            But this version of pragcc perform a preprocessing if the
            code called fake_cfile located in pragcc.core.parser.c99.parser
            this step remove the first two headers of the original file.

            #include <stdbool.h>
            #include <stdio.h>

            for fake files

            #include <_fake_defines.h>
            #include <_fake_typedefs.h>

            So, the bool type would not be recognized again. The follwing 
            test show a possible solution.

        """
        with self.assertRaises(ParseError):
            omp = parallelizer.OpenMP(file_path=self._bool_type_2)

    def test_openmp_object_from_include_bool_type_behind_two_includes_file(self):
        """

            We place two includes above the stdbool.h

            #include <stdio.h>
            #include <stdlib.h>
            #include <stdbool.h>

            So the first two includes are faked out

            #include <_fake_defines.h>
            #include <_fake_typedefs.h>
            #include <stdbool.h>

            Then, the bool type will be recognized by the following step,
            The C preprocessing.          

        """
        omp = parallelizer.OpenMP(file_path=self._bool_type_3)
        self.assertIsInstance(omp,parallelizer.OpenMP)


RAW_CODE_SIMPLE_LOOP = """
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


class TestOpenMPParallelization(unittest.TestCase):

    def setUp(self):
        # Creating the OpenMP parallelizer
        self._omp = parallelizer.OpenMP(raw_code=RAW_CODE_SIMPLE_LOOP)

        # Metadata needed for code parallelization
        data = {
            'vesion': 1.0,
            'name': 'stencil',
            'description': 'Linealized matrix template with stencil parallel programming pattern. ...',
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
                                {
                                    'nro':0,
                                    'clauses': {
                                        'private': ['i'],
                                        'reduction': '+:sum',
                                        'colapse': 3
                                    }
                                }
                            ]
                        } 
                    }
                }
            }
        }

        # Creating a parallel metadata object 
        self._parallel = metadata.Parallel(data=data)

        # Metadata needed for code parallelization
        no_valid_data = {
            'vesion': 1.0,
            'name': 'stencil',
            'description': 'Linealized matrix template with stencil parallel programming pattern. ...',
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
                                {
                                    # The first loop in the code
                                    # is the loop number 0, then the
                                    # loop nro does not exists
                                    'nro':1,
                                    'clauses': {
                                        'private': ['i'],
                                        'reduction': '+:sum',
                                        'colapse': 3
                                    }
                                }
                            ]
                        } 
                    }
                }
            }
        }

        # Creating a parallel metadata object 
        self._no_valid_parallel = metadata.Parallel(data=no_valid_data)

    def tearDown(self):

        # Clean intermediate files created during code annotation
        utils.purge(TEST_DIR,r'^fake_*')
        utils.purge(TEST_DIR,r'^mp_*')
        utils.purge(TEST_DIR,r'^ccode_*')
        utils.purge(TEST_DIR,r'^acc_*')

    def test_parallel_directive(self):

        # Getting the OpenMP directives of each function from
        # the metadata object. 
        functions_directives = self._parallel.get_directives('mp')

        # Testing the metadata object has the same data that was
        # given to it.
        function_name, directives = functions_directives[0]

        self.assertEqual(function_name,'some_function')
        self.assertDictEqual(
            directives.get('parallel'),
            {
                'scope':0,
                'clauses': {
                    'num_threads': 4,
                    'shared': ['A','B','C'],
                    'default': 'none'
                }
            }
        )

        # PARALLELIZATION STEPS

        # 1) Creation of the pragma

        # Getting a directive from the metadata
        parallel_directive = directives.get('parallel')
        # Getting the clauses of that directive
        clauses = parallel_directive.get('clauses')

        # Constructing the OpenMP raw pragma with the directive name a clauses
        pragma = self._omp.get_raw_pragma(directive_name='parallel',clauses=clauses)
        expected_pragma = '#pragma omp parallel num_threads(4) shared(A,B,C) default(none) '

        # The generated string conserve the order of '#pragma omp parallel' string
        # but clauses can change order, thus both string pragmas are equivalent if
        # they has the same words. Which is equivalent to saying f the two sets have
        # exactly the same elements

        # ['#pragma', 'omp', 'parallel', 'num_threads(4)', 'default(none)', 'shared(A,B,C)', '']
        # ['#pragma', 'omp', 'parallel', 'default(none)', 'num_threads(4)', 'shared(A,B,C)', '']
        
        self.assertEqual(set(pragma.split(' ')) ,set(expected_pragma.split(' ')))

        # 2) Creating an insertion to place the pragma in the code.

        # Generating the insertions needed to place the pragma in the source code.
        insertions = self._omp.get_parallel_directive_inserts(
            function_name=function_name,
            directives=directives
        )

        # The insertion has the follwing format (raw_code,line_number)
        # the line_number is relative to the function.

        # 0 void some_function(){
        # 1
        # 2     int A[N];
        # 3     int B[N];
        # 4     int C[N];
        # 5
        # 6     for(int i=0; i<N; ++i){
        # 7         C[i] = A[i] + B[i];
        # 8     }    
        # 9 }

        expected_insetions = [
            (pragma,6),
            ('{',6),
            ('}',9)
        ]

        self.assertEqual(insertions,expected_insetions)

        # 3) Code insertion

        raw_code = self._omp.code.get_function_raw(function_name)
        new_raw_code = self._omp.insert_lines(raw_code,insertions)

        # 0  void some_function(){
        # 1
        # 2     int A[N];
        # 3     int B[N];
        # 4     int C[N];
        # 5
        # 6  #pragma omp parallel num_threads(4) shared(A,B,C) default(none)
        # 7  {
        # 8     for(int i=0; i<N; ++i){
        # 9         C[i] = A[i] + B[i];
        # 10    }    
        # 11 }
        # 12 }

        new_raw_code_lines = new_raw_code.splitlines()
        pragma_line = new_raw_code_lines[6]
        left = new_raw_code_lines[7]
        right = new_raw_code_lines[11]

        self.assertEqual(pragma_line,pragma)
        self.assertEqual(left,'{')
        self.assertEqual(right,'}')

    def test_parallel_for_directive(self):

        # Getting the OpenMP directives of each function from
        # the metadata object. 
        functions_directives = self._parallel.get_directives('mp')

        # PARALLELIZATION STEPS

        # 1) Creation of the pragma

        # Getting first function directives
        function_name, directives = functions_directives[0]

        # Getting a directive from the metadata
        parallel_fors = directives.get('parallel_for')
        # Getting the clauses of that directive
        first_for = parallel_fors[0]
        clauses = first_for.get('clauses')

        # Constructing the OpenMP raw pragma with the directive name a clauses
        pragma = self._omp.get_raw_pragma(directive_name='parallel for',clauses=clauses)
        expected_pragma = '#pragma omp parallel for private(i) reduction(+:sum) colapse(3) '

        # The generated string conserve the order of '#pragma omp parallel' string
        # but clauses can change order, thus both string pragmas are equivalent if
        # they has the same words. Which is equivalent to saying f the two sets have
        # exactly the same elements

        # ['#pragma', 'omp', 'parallel', 'num_threads(4)', 'default(none)', 'shared(A,B,C)', '']
        # ['#pragma', 'omp', 'parallel', 'default(none)', 'num_threads(4)', 'shared(A,B,C)', '']
        
        self.assertEqual(set(pragma.split(' ')) ,set(expected_pragma.split(' ')))

        # 2) Creating an insertion to place the pragma in the code.

        # Generating the insertions needed to place the pragma in the source code.
        insertions = self._omp.get_parallel_for_directive_inserts(
            function_name=function_name,
            directives=directives
        )

        # The insertion has the follwing format (raw_code,line_number)
        # the line_number is relative to the function.

        # 0 void some_function(){
        # 1
        # 2     int A[N];
        # 3     int B[N];
        # 4     int C[N];
        # 5
        # 6     for(int i=0; i<N; ++i){
        # 7         C[i] = A[i] + B[i];
        # 8     }    
        # 9 }

        expected_insetions = [
            (pragma,6)
        ]

        self.assertEqual(insertions,expected_insetions)

        # 3) Code insertion

        raw_code = self._omp.code.get_function_raw(function_name)
        new_raw_code = self._omp.insert_lines(raw_code,insertions)

        # 0  void some_function(){
        # 1
        # 2     int A[N];
        # 3     int B[N];
        # 4     int C[N];
        # 5
        # 6 #pragma omp parallel for private(i) reduction(+:sum) colapse(3)
        # 7    for(int i=0; i<N; ++i){
        # 8         C[i] = A[i] + B[i];
        # 9    }    
        # 10
        # 11 }

        new_raw_code_lines = new_raw_code.splitlines()
        pragma_line = new_raw_code_lines[6]

        self.assertEqual(pragma_line,pragma)

    def test_parallel_for_directive_with_a_non_existing_loop(self):

        # Getting the OpenMP directives of each function from
        # the metadata object. 
        functions_directives = self._no_valid_parallel.get_directives('mp')

        # PARALLELIZATION STEPS

        # 1) Creation of the pragma

        # Getting first function directives
        function_name, directives = functions_directives[0]

        # 2) Creating an insertion to place the pragma in the code.

        # Generating the insertions needed to place the pragma in the source code.
        insertions = self._omp.get_parallel_for_directive_inserts(
            function_name=function_name,
            directives=directives
        )

        # The loop nro = 1 does not exist in the example code
        # NO insertions are generated, in this way the list of
        # inserts must be empty.

        # 'parallel_for': [
        #     {
        #         # The first loop in the code
        #         # is the loop number 0, then the
        #         # loop nro does not exists
        #         'nro':1,
        #         'clauses': {
        #             'private': ['i'],
        #             'reduction': '+:sum',
        #             'colapse': 3
        #         }
        #     }
        # ]

        self.assertListEqual(insertions,[])

    @unittest.skip("Needs to be implemented")
    def test_for_directive(self):
        pass
