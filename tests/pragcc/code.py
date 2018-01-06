# -*- encoding: utf-8 -*-

from pragcc.core import code
from pragcc.core.parser.c99.pycparser.plyparser import ParseError

from tests import utils
from tests.pragcc import test_data

import unittest

class TestCCodeObject(unittest.TestCase):

    def setUp(self):
        self._basic = test_data.BASIC_FILE_PATH
        self._complex = test_data.COMPLEX_FILE_PATH
        self._empty = test_data.EMPTY_FILE_PATH
        self._unsupported_1 = test_data.UNSUPPORTED_CODE_FILE_PATH_1
        self._unsupported_2 = test_data.UNSUPPORTED_CODE_FILE_PATH_2
        self._supported = test_data.SUPPORTED_CODE_FILE_PATH

    def tearDown(self):
        utils.purge(dir=test_data.TEST_DIR,pattern=r'^fake_*')
        utils.purge(dir=test_data.TEST_DIR,pattern=r'^ccode_*')
    
    def test_read_basic_code_from_file(self):
        """
            To create a ccode objects , the given code must follow 
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
            ccode = code.CCode(file_path=self._basic)

    def test_read_complex_code_from_file(self):
        ccode = code.CCode(file_path=self._complex)
        self.assertIsInstance(ccode,code.CCode)

    def test_read_empty_code_from_file(self):
        """
            To create a ccode objects , the given code must follow 
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
            ccode = code.CCode(file_path=self._empty)

    def test_read_unssupported_code_file_1(self):
        with self.assertRaises(ParseError):
            ccode = code.CCode(file_path=self._unsupported_1)

    def test_read_unssupported_code_file_2(self):
        with self.assertRaises(ParseError):
            ccode = code.CCode(file_path=self._unsupported_2)

    def test_read_supported_code_file(self):
        ccode = code.CCode(file_path=self._supported)
        self.assertIsInstance(ccode,code.CCode)
