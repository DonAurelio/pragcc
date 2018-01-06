# -*- encoding: utf-8 -*-

from pragcc.core import parallelizer, metadata, code
from pragcc.core.parser.c99.pycparser.plyparser import ParseError

from tests import utils
from tests.pragcc import test_data

import unittest


class TestBaseParallelizer(unittest.TestCase):

    def setUp(self):
        self._raw_code = test_data.SIMPLE_CODE
        self._parallelizer = parallelizer.BaseParallelizer()

    def test_insert_lines_in_raw_code(self):
        """ Test code insertion function.

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
            self._raw_code,
            insertions
        )

        line_1 = new_raw.splitlines()[1]
        line_2 = new_raw.splitlines()[3]

        self.assertEqual(line_1,'First insertion')
        self.assertEqual(line_2,'Second insertion')

    def test_insert_in_invalid_position(self):
        """ 
        When insertions have no valid positions, it means
        no insertions are performed, in that case, an empty
        string is returned.
        """

        insertions = [
            ('First insertion',-1),
            ('Second insertion',-1)
        ]

        new_raw = self._parallelizer.insert_lines(
            self._raw_code,
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
            self._raw_code,
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

    def test_not_implemented_methods(self):
        """Testing methods that needs to be implemented."""
        with self.assertRaises(NotImplementedError):

            self._parallelizer.get_raw_pragma(
                directive_name='parallel',
                clauses={}
            )

            self._parallelizer.insert_directives(
                function_name='some_function',
                directives={}
            )

            self._parallelizer.parallelize(metadata=None)
