# -*- encoding: utf-8 -*-

from pragcc.core.parser.c99 import parser
from pragcc.core.parser.c99.pycparser.c_ast import FileAST
from pragcc.core.parser.c99.pycparser.plyparser import ParseError

from . import utils
import unittest
import os



BASE_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DIR = os.path.join(BASE_DIR,'files')


class TestCCodeParsing(unittest.TestCase):
    
    def setUp(self):
        self._basic = os.path.join(TEST_DIR,'basic.c')
        self._complex = os.path.join(TEST_DIR,'complex.c')
        self._empty = os.path.join(TEST_DIR,'empty.c')
        self._bool_type_1 = os.path.join(TEST_DIR,'bool_type_1.c')
        self._bool_type_2 = os.path.join(TEST_DIR,'bool_type_2.c')
        self._bool_type_3 = os.path.join(TEST_DIR,'bool_type_3.c')

    def tearDown(self):
        utils.purge(dir=TEST_DIR,pattern='fake_*')

    def test_parse_basic_cfile(self):
        ast = parser.parse_cfile(file_path=self._basic)
        self.assertIsInstance(ast,FileAST)

    def test_parse_complex_cfile(self):
        ast = parser.parse_cfile(file_path=self._complex)
        self.assertIsInstance(ast,FileAST)

    def test_parse_empty_cfile(self):
        ast = parser.parse_cfile(file_path=self._empty)
        self.assertIsInstance(ast,FileAST)

    def test_parse_unssupported_type_cfile(self):
        # bool type is not supported nativelly in C99
        with self.assertRaises(ParseError):
            ast = parser.parse_cfile(file_path=self._bool_type_1)

    def test_parse_include_bool_type_cfile(self):
        with self.assertRaises(ParseError):
            ast = parser.parse_cfile(file_path=self._bool_type_2)

    def test_parse_include_bool_type_behid_two_includes_cfile(self):
        """This test is the depicts the solution to the pravious two tests.

        test_parse_unssupported_type_cfile and test_parse_include_bool_type_cfile erros.
        Before parse a cfile, two includes are inserted on it replaced the first two 
        includes from the original code, Then to conserve the bool type include, whe need
        to add two includes above it. 
        """
        ast = parser.parse_cfile(file_path=self._bool_type_3)
        self.assertIsInstance(ast,FileAST)


