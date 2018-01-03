# -*- encoding: utf-8 -*-

from pragcc.core import parallelizer
from pragcc.core import metadata
from pragcc.core import code
from pragcc.core.parser.c99.pycparser.plyparser import ParseError
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
        self._parallelizer = parallelizer.BaseParallelizer()

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

        new_raw = self._parallelizer.insert_lines(
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

        new_raw = self._parallelizer.insert_lines(
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

        new_raw = self._parallelizer.insert_lines(
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

        new_raw = self._parallelizer.insert_lines(
            empty_raw,
            insertions
        )

        self.assertEqual(new_raw,'')



# class TestOpenMPObject(unittest.TestCase):

#     def setUp(self):
#         self._basic = os.path.join(TEST_DIR,'basic.c')
#         self._complex = os.path.join(TEST_DIR,'complex.c')
#         self._empty = os.path.join(TEST_DIR,'empty.c')
#         self._bool_type_1 = os.path.join(TEST_DIR,'bool_type_1.c')
#         self._bool_type_2 = os.path.join(TEST_DIR,'bool_type_2.c')
#         self._bool_type_3 = os.path.join(TEST_DIR,'bool_type_3.c')

#         parallel_file_path = os.path.join(TEST_DIR,'parallel.yml')
#         self._parallel_metadata = metadata.ParallelFile(
#             file_path=parallel_file_path
#         )

#     def tearDown(self):
#         utils.purge(TEST_DIR,r'^fake_*')
#         utils.purge(TEST_DIR,r'^omp_*')
#         utils.purge(TEST_DIR,r'^ccode_*')
#         utils.purge(TEST_DIR,r'^acc_*')

#     def test_openmp_object_from_basic_code_file(self):
#         """
#             To create a ccode objects , the given code must follow 
#             the following struture

#             #include <...>
#             #include <...>

#             #define ....

            
#             function_1(){
        
#             }

#             int main(){
        
#             }

#             if the given code do not follow this structure it can 
#             not be splited in sections, because the code does not
#             have that sections, then an IndexError takes place.
#         """
#         with self.assertRaises(IndexError):
#             omp = parallelizer.OpenMP(
#                 file_path=self._basic,
#                 metadata=self._parallel_metadata
#             )

#     def test_openmp_object_from_complex_code_file(self):
#         omp = parallelizer.OpenMP(
#             file_path=self._complex,
#             metadata=self._parallel_metadata
#         )

#         self.assertIsInstance(omp,parallelizer.OpenMP)

#     def test_openmp_object_from_empty_code_file(self):
#         """
#             To create a ccode objects , the given code must follow 
#             the following struture

#             #include <...>
#             #include <...>

#             #define ....

            
#             function_1(){
        
#             }

#             int main(){
        
#             }

#             if the given code do not follow this structure it can 
#             not be splited in sections, because the code does not
#             have that sections, then an IndexError takes place.
#         """
#         with self.assertRaises(IndexError):
#             omp = parallelizer.OpenMP(
#                 file_path=self._empty,
#                 metadata=self._parallel_metadata
#             )

#     def test_openmp_object_from_unssupported_type_code_file(self):
#         with self.assertRaises(ParseError):
#             omp = parallelizer.OpenMP(
#                 file_path=self._bool_type_1,
#                 metadata=self._parallel_metadata
#             )

#     def test_openmp_object_from_include_bool_type_file(self):
#         with self.assertRaises(ParseError):
#             omp = parallelizer.OpenMP(
#                 file_path=self._bool_type_2,
#                 metadata=self._parallel_metadata
#             )

#     def test_openmp_object_from_include_bool_type_behind_two_includes_file(self):
#         omp = parallelizer.OpenMP(file_path=self._bool_type_3)
#         self.assertIsInstance(omp,parallelizer.OpenMP)

#     def test_openmp_parallelization_from_complex_code_file(self):
#         omp = parallelizer.OpenMP(
#             file_path=self._complex,
#             metadata=self._parallel_metadata
#         )

#         ccode = omp.parallelize()
#         self.assertIsInstance(ccode,code.CCode)