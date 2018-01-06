# -*- encoding: utf-8 -*-

from pragcc.core import parallelizer, metadata, code
from pragcc.core.parser.c99.pycparser.plyparser import ParseError

from tests import utils
from tests.pragcc import test_data

import unittest


class TestOpenACCObject(unittest.TestCase):

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

    def test_open_acc_object_from_basic_file(self):
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
            acc = parallelizer.OpenACC(file_path=self._basic)

    def test_open_acc_object_from_complex_file(self):
        acc = parallelizer.OpenACC(file_path=self._complex)
        self.assertIsInstance(acc,parallelizer.OpenACC)

    def test_open_acc_object_from_empty_code_file(self):
        with self.assertRaises(IndexError):
            acc = parallelizer.OpenACC(file_path=self._empty)

    def test_open_acc_object_from_unsupported_code_1(self):
        """ 
            The C preprocessor used by pycparse for code parsing do not support
            the bool type natively, if the preprocessor find an unknwon type, the
            code parsing cann not take place.
        """
        with self.assertRaises(ParseError):
            acc = parallelizer.OpenACC(file_path=self._unsupported_1)

    def test_open_acc_object_from__unsupported_code_2(self):
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
            acc = parallelizer.OpenACC(file_path=self._unsupported_2)

    def test_open_acc_object_from_supported_code(self):
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
        acc = parallelizer.OpenACC(file_path=self._supported)
        self.assertIsInstance(acc,parallelizer.OpenACC)


class TestOpenACCDataDirective(unittest.TestCase):

    def setUp(self):
        # Creating the OpenMP parallelizer
        self._acc = parallelizer.OpenACC(
            raw_code=test_data.SIMPLE_CODE_FUNCTION_LOOP
        )

        # Creation paralellization metadata object
        self._parallel = metadata.Parallel(
            data=test_data.METADATA_FOR_SIMPLE_CODE_FUNCTION_LOOP
        )

    def tearDown(self):
        # Clean intermediate files created during code annotation
        utils.purge(test_data.TEST_DIR,r'^fake_*')
        utils.purge(test_data.TEST_DIR,r'^acc_*')
        utils.purge(test_data.TEST_DIR,r'^ccode_*')

    def test_open_acc_data_directive(self):
        """ 
        The follwing is the code thats is intended to be parallelized.
        we will insert the data directive to the for loop in
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
        functions_directives = self._parallel.get_directives('acc')

        # Getting the metadata of the first function or the only one
        # some_function
        function_name, directives = functions_directives[0]

        # PARALLELIZATION STEPS

        # 1) Creation of the pragma

        # Getting the parallel directive from metadata
        data_directive = directives.get('data')
        clauses = data_directive.get('clauses')

        # Constructing the OpenMP raw pragma with the directive name a clauses
        pragma = self._acc.get_raw_pragma(directive_name='data',clauses=clauses)
        expected_pragma = '#pragma acc data copy(A,B,C) '

        # The generated string conserve the order of '#pragma omp parallel' string
        # but clauses can change order, thus both string pragmas are equivalent if
        # they has the same words. Which is equivalent to saying that the two sets have
        # exactly the same elements

        # ['#pragma', 'acc', 'data', 'copy(A,B,C)', '']
        # ['#pragma', 'acc', 'data', 'copy(A,B,C)', '']
        
        self.assertEqual(set(pragma.split(' ')) ,set(expected_pragma.split(' ')))

        # 2) Creating an insertion to place the pragma in the code.

        # Generating the insertions needed to place the pragma in the source code.
        insertions = self._acc.get_data_directive_inserts(
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

        raw_code = self._acc.code.get_function_raw(function_name)
        new_raw_code = self._acc.insert_lines(raw_code,insertions)

        # 0  void some_function(){
        # 1
        # 2     int A[N];
        # 3     int B[N];
        # 4     int C[N];
        # 5
        # 6  #pragma acc data copy(A,B,C)
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

class TestOpenACCParallelLoopDirective(unittest.TestCase):

    def setUp(self):
        # Creating the OpenMP parallelizer
        self._acc = parallelizer.OpenACC(
            raw_code=test_data.SIMPLE_CODE_FUNCTION_LOOP
        )

        # Creation paralellization metadata object
        self._parallel = metadata.Parallel(
            data=test_data.METADATA_FOR_SIMPLE_CODE_FUNCTION_LOOP
        )

    def tearDown(self):
        # Clean intermediate files created during code annotation
        utils.purge(test_data.TEST_DIR,r'^fake_*')
        utils.purge(test_data.TEST_DIR,r'^acc_*')
        utils.purge(test_data.TEST_DIR,r'^ccode_*')


    def test_parallel_loop_directive(self):

        # Getting the OpenMP directives of each function from
        # the metadata object. 
        functions_directives = self._parallel.get_directives('acc')

        # PARALLELIZATION STEPS

        # 1) Creation of the pragma

        # Getting first function directives
        function_name, directives = functions_directives[0]

        # Getting a directive from the metadata
        parallel_loops = directives.get('parallel_loop')
        # Getting the clauses of that directive
        first_loop = parallel_loops[0]
        clauses = first_loop.get('clauses')

        # Constructing the OpenMP raw pragma with the directive name a clauses
        pragma = self._acc.get_raw_pragma(directive_name='parallel loop',clauses=clauses)
        expected_pragma = '#pragma acc parallel loop num_gangs(100) num_workers(100) gang vector '

        # The generated string conserve the order of '#pragma omp parallel' string
        # but clauses can change order, thus both string pragmas are equivalent if
        # they has the same words. Which is equivalent to saying f the two sets have
        # exactly the same elements

        # ['#pragma','acc','parallel','loop','num_gangs(100)','num_workers(100)','gang','vector','']
        # ['#pragma','acc','parallel','loop','num_workers(100)','num_gangs(100)','gang','vector','']
        
        self.assertEqual(set(pragma.split(' ')) ,set(expected_pragma.split(' ')))

        # 2) Creating an insertion to place the pragma in the code.

        # Generating the insertions needed to place the pragma in the source code.
        insertions = self._acc.get_parallel_loop_directive_inserts(
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

        raw_code = self._acc.code.get_function_raw(function_name)
        new_raw_code = self._acc.insert_lines(raw_code,insertions)

        # 0  void some_function(){
        # 1
        # 2     int A[N];
        # 3     int B[N];
        # 4     int C[N];
        # 5
        # 6 #pragma acc parallel loop num_gangs(100) num_workers(100) gang vector 
        # 7    for(int i=0; i<N; ++i){
        # 8         C[i] = A[i] + B[i];
        # 9    }    
        # 10
        # 11 }

        new_raw_code_lines = new_raw_code.splitlines()
        pragma_line = new_raw_code_lines[6]

        self.assertEqual(pragma_line,pragma)


class TestOpenACCLoopDirective(unittest.TestCase):

    def setUp(self):
        # Creating the OpenMP parallelizer
        self._acc = parallelizer.OpenACC(
            raw_code=test_data.SIMPLE_CODE_FUNCTION_LOOP
        )

        # Creation paralellization metadata object
        self._parallel = metadata.Parallel(
            data=test_data.METADATA_FOR_SIMPLE_CODE_FUNCTION_LOOP
        )

    def tearDown(self):
        # Clean intermediate files created during code annotation
        utils.purge(test_data.TEST_DIR,r'^fake_*')
        utils.purge(test_data.TEST_DIR,r'^acc_*')
        utils.purge(test_data.TEST_DIR,r'^ccode_*')


    def test_loop_directive(self):

        # Getting the OpenMP directives of each function from
        # the metadata object. 
        functions_directives = self._parallel.get_directives('acc')

        # PARALLELIZATION STEPS

        # 1) Creation of the pragma

        # Getting first function directives
        function_name, directives = functions_directives[0]

        # Getting a directive from the metadata
        loops = directives.get('loop')
        # Getting the clauses of that directive
        first_loop = loops[0]
        clauses = first_loop.get('clauses')

        # Constructing the OpenMP raw pragma with the directive name a clauses
        pragma = self._acc.get_raw_pragma(directive_name='loop',clauses=clauses)
        expected_pragma = '#pragma acc loop num_gangs(100) num_workers(100) vector '

        # The generated string conserve the order of '#pragma omp parallel' string
        # but clauses can change order, thus both string pragmas are equivalent if
        # they has the same words. Which is equivalent to saying f the two sets have
        # exactly the same elements

        # ['#pragma','acc','parallel','loop','num_gangs(100)','num_workers(100)','gang','vector','']
        # ['#pragma','acc','parallel','loop','num_workers(100)','num_gangs(100)','gang','vector','']
        
        self.assertEqual(set(pragma.split(' ')) ,set(expected_pragma.split(' ')))

        # 2) Creating an insertion to place the pragma in the code.

        # Generating the insertions needed to place the pragma in the source code.
        insertions = self._acc.get_loop_directive_inserts(
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

        raw_code = self._acc.code.get_function_raw(function_name)
        new_raw_code = self._acc.insert_lines(raw_code,insertions)

        # 0  void some_function(){
        # 1
        # 2     int A[N];
        # 3     int B[N];
        # 4     int C[N];
        # 5
        # 6 #pragma acc loop num_gangs(100) num_workers(100) vector 
        # 7    for(int i=0; i<N; ++i){
        # 8         C[i] = A[i] + B[i];
        # 9    }    
        # 10
        # 11 }

        new_raw_code_lines = new_raw_code.splitlines()
        pragma_line = new_raw_code_lines[6]

        self.assertEqual(pragma_line,pragma)

class TestOpenACCWholeParallelization(unittest.TestCase):

    def setUp(self):
        # Creating the OpenMP parallelizer
        self._acc = parallelizer.OpenACC(
            raw_code=test_data.SIMPLE_CODE_FUNCTION_LOOP
        )

        # Creation paralellization metadata object
        self._parallel = metadata.Parallel(
            data=test_data.METADATA_FOR_SIMPLE_CODE_FUNCTION_LOOP
        )

    def test_parallelize_method(self):
        # NOTE: we need to check the paralwllization was
        # driven correctly.
        ccode = self._acc.parallelize(self._parallel)

