# -*- encoding: utf-8 -*-

from pragcc.core import code
from pragcc.core.parser.c99.pycparser.plyparser import ParseError

from . import utils
import unittest
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DIR = os.path.join(BASE_DIR,'files')


class TestCCodeObject(unittest.TestCase):

    def setUp(self):
        self._basic = os.path.join(TEST_DIR,'basic.c')
        self._complex = os.path.join(TEST_DIR,'complex.c')
        self._empty = os.path.join(TEST_DIR,'empty.c')
        self._bool_type_1 = os.path.join(TEST_DIR,'bool_type_1.c')
        self._bool_type_2 = os.path.join(TEST_DIR,'bool_type_2.c')
        self._bool_type_3 = os.path.join(TEST_DIR,'bool_type_3.c')

    def tearDown(self):
        utils.purge(dir=TEST_DIR,pattern=r'^fake_*')
        utils.purge(dir=TEST_DIR,pattern=r'^ccode_*')
    
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

    def test_read_unssupported_type_file(self):
        with self.assertRaises(ParseError):
            ccode = code.CCode(file_path=self._bool_type_1)

    def test_read_include_bool_type_file(self):
        with self.assertRaises(ParseError):
            ccode = code.CCode(file_path=self._bool_type_2)

    def test_read_include_bool_type_behid_two_includes_file(self):
        ccode = code.CCode(file_path=self._bool_type_3)
        self.assertIsInstance(ccode,code.CCode)
