# -*- encoding: utf-8 -*-

from pragcc.core import parallelizer, metadata, code
from pragcc.core.parser.c99.pycparser.plyparser import ParseError

from tests import utils
from tests.pragcc import test_data

import unittest


def pragmas_equals(a,b):
    pragma_1 = set(a.split(' '))
    pragma_2 = set(b.split(' '))

    return pragma_1 == pragma_2


class TestOpenMPObject(unittest.TestCase):

    def setUp(self):

        # Set of files to test code annotation with OpenMP directives
        self._basic = test_data.BASIC_FILE_PATH
        self._complex = test_data.COMPLEX_FILE_PATH
        self._empty = test_data.EMPTY_FILE_PATH
        self._unsupported_1 = test_data.UNSUPPORTED_CODE_FILE_PATH_1
        self._unsupported_2 = test_data.UNSUPPORTED_CODE_FILE_PATH_2
        self._supported = test_data.SUPPORTED_CODE_FILE_PATH

    def tearDown(self):

        # Clean intermediate files created during code annotation
        utils.purge(test_data.TEST_DIR,r'^fake_*')
        utils.purge(test_data.TEST_DIR,r'^mp_*')
        utils.purge(test_data.TEST_DIR,r'^ccode_*')

    def test_open_mp_object_from_basic_file(self):
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

    def test_open_mp_object_from_complex_file(self):
        omp = parallelizer.OpenMP(file_path=self._complex)
        self.assertIsInstance(omp,parallelizer.OpenMP)

    def test_openmp_object_from_empty_code_file(self):
        with self.assertRaises(IndexError):
            omp = parallelizer.OpenMP(file_path=self._empty)

    def test_open_mp_object_from_unsupported_code_1(self):
        """ 
            The C preprocessor used by pycparse for code parsing do not support
            the bool type natively, if the preprocessor find an unknwon type, the
            code parsing cann not take place.
        """
        with self.assertRaises(ParseError):
            omp = parallelizer.OpenMP(file_path=self._unsupported_1)

    def test_open_mp_object_from_unsupported_code_2(self):
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
            omp = parallelizer.OpenMP(file_path=self._unsupported_2)

    def test_openmp_object_from_supported_code(self):
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
        omp = parallelizer.OpenMP(file_path=self._supported)
        self.assertIsInstance(omp,parallelizer.OpenMP)


class TestParallelDirective(unittest.TestCase):

    def setUp(self):
        # Creating the OpenMP parallelizer
        self._omp = parallelizer.OpenMP(
            raw_code=test_data.SIMPLE_CODE_FUNCTION_LOOP
        )

        # Creation paralellization metadata object
        self._parallel = metadata.Parallel(
            data=test_data.METADATA_FOR_SIMPLE_CODE_FUNCTION_LOOP
        )

    def tearDown(self):
        # Clean intermediate files created during code annotation
        utils.purge(test_data.TEST_DIR,r'^fake_*')
        utils.purge(test_data.TEST_DIR,r'^mp_*')
        utils.purge(test_data.TEST_DIR,r'^ccode_*')

    def test_parallel_directive(self):
        """ 
        The follwing is the code thats is intended to be parallelized.
        we will insert the parallel directive to the for loop in
        some_funtion.
        
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

        # Getting the parallelization metadata of the functions that
        # will be parallelized with OpenMP
        functions_directives = self._parallel.get_directives('mp')

        # Getting the metadata of the first function or the only one
        # some_function
        function_name, directives = functions_directives[0]

        # PARALLELIZATION STEPS

        # 1) Creation of the pragma

        # Getting the parallel directive from metadata
        parallel_directive = directives.get('parallel')
        clauses = parallel_directive.get('clauses')

        # Constructing the OpenMP raw pragma with the directive name a clauses
        pragma = self._omp.get_raw_pragma(directive_name='parallel',clauses=clauses)
        expected_pragma = '#pragma omp parallel num_threads(4) shared(A,B,C) default(none) '

        # The generated string conserve the order of '#pragma omp parallel' string
        # but clauses can change order, thus both string pragmas are equivalent if
        # they has the same words. Which is equivalent to saying that the two sets have
        # exactly the same elements

        # ['#pragma', 'omp', 'parallel', 'num_threads(4)', 'default(none)', 'shared(A,B,C)', '']
        # ['#pragma', 'omp', 'parallel', 'default(none)', 'num_threads(4)', 'shared(A,B,C)', '']
        
        self.assertTrue(pragmas_equals(pragma,expected_pragma))

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


class TestOpenMPParallelForDirective(unittest.TestCase):

    def setUp(self):
        # Creating the OpenMP parallelizer
        self._omp = parallelizer.OpenMP(
            raw_code=test_data.SIMPLE_CODE_FUNCTION_LOOP
        )

        # Creation paralellization metadata object
        self._parallel = metadata.Parallel(
            data=test_data.METADATA_FOR_SIMPLE_CODE_FUNCTION_LOOP
        )

        # Creation a parallelization metadata with errors
        self._parallel_with_errors = metadata.Parallel(
            data=test_data.METADATA_FOR_SIMPLE_CODE_FUNCTION_LOOP_WITH_ERRORS
        )


    def tearDown(self):
        # Clean intermediate files created during code annotation
        utils.purge(test_data.TEST_DIR,r'^fake_*')
        utils.purge(test_data.TEST_DIR,r'^mp_*')
        utils.purge(test_data.TEST_DIR,r'^ccode_*')

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
        
        self.assertTrue(pragmas_equals(pragma,expected_pragma))

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

    def test_parallel_for_directive_with_an_incorrect_scope(self):

        # Getting the OpenMP directives of each function from
        # the metadata object. 
        functions_directives = self._parallel_with_errors.get_directives('mp')

        # PARALLELIZATION STEPS

        # 1) Creation of the pragma

        # Getting first function directives
        function_name, directives = functions_directives[0]

        # 2) Creating an insertion to place the pragma in the code.

        # Generating the insertions needed to place the pragma in the source code.
        insertions = self._omp.get_parallel_directive_inserts(
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


class TestOpenMPWholeParallelization(unittest.TestCase):

    def setUp(self):
        # Creating the OpenMP parallelizer
        self._omp = parallelizer.OpenMP(
            raw_code=test_data.SIMPLE_CODE_FUNCTION_LOOP
        )

        # Creation paralellization metadata object
        self._parallel = metadata.Parallel(
            data=test_data.METADATA_FOR_SIMPLE_CODE_FUNCTION_LOOP
        )

    def tearDown(self):
        # Clean intermediate files created during code annotation
        utils.purge(test_data.TEST_DIR,r'^fake_*')
        utils.purge(test_data.TEST_DIR,r'^mp_*')
        utils.purge(test_data.TEST_DIR,r'^ccode_*')

    def test_parallelize_method(self):
        # NOTE: we need to check the paralwllization was
        # driven correctly.
        ccode = self._omp.parallelize(self._parallel)
