# -*- encoding: utf-8 -*-

from pragcc.core.parser.c99 import parser
from pragcc.core.parser.c99.pycparser.c_ast import FileAST
from pragcc.core.parser.c99.pycparser.plyparser import ParseError

from tests import utils
from tests.pragcc import test_data

import unittest


class TestCCodeParsing(unittest.TestCase):
    
    def setUp(self):
        self._basic = test_data.BASIC_FILE_PATH
        self._complex = test_data.COMPLEX_FILE_PATH
        self._empty = test_data.EMPTY_FILE_PATH
        self._unsupported_1 = test_data.UNSUPPORTED_CODE_FILE_PATH_1
        self._unsupported_2 = test_data.UNSUPPORTED_CODE_FILE_PATH_2
        self._supported = test_data.SUPPORTED_CODE_FILE_PATH

    def tearDown(self):
        utils.purge(dir=test_data.TEST_DIR,pattern='fake_*')

    def test_parse_basic_code_file(self):
        ast = parser.parse_cfile(file_path=self._basic)
        self.assertIsInstance(ast,FileAST)

    def test_parse_complex_code_file(self):
        ast = parser.parse_cfile(file_path=self._complex)
        self.assertIsInstance(ast,FileAST)

    def test_parse_empty_code_file(self):
        ast = parser.parse_cfile(file_path=self._empty)
        self.assertIsInstance(ast,FileAST)

    def test_parse_unsupported_code_file_1(self):
        # bool type is not supported nativelly in C99
        with self.assertRaises(ParseError):
            ast = parser.parse_cfile(file_path=self._unsupported_1)

    def test_parse_unsupported_code_file_2(self):
        with self.assertRaises(ParseError):
            ast = parser.parse_cfile(file_path=self._unsupported_2)

    def test_parse_supported_code_file(self):
        """This test is the depicts the solution to the pravious two tests.

        test_parse_unssupported_type_cfile and test_parse_include_bool_type_cfile erros.
        Before parse a cfile, two includes are inserted on it replaced the first two 
        includes from the original code, Then to conserve the bool type include, whe need
        to add two includes above it. 
        """
        ast = parser.parse_cfile(file_path=self._supported)
        self.assertIsInstance(ast,FileAST)


