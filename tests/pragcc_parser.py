# -*- encoding: utf-8 -*-

from pragcc.core.parser.c99 import parser

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

	def test_parse_cfile(self):
		ast = parser.parse_cfile(file_path=self._basic)
