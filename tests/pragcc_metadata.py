# -*- encoding: utf-8 -*-

from pragcc.core import metadata

import unittest
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DIR = os.path.join(BASE_DIR,'files')


class TestParallelFile(unittest.TestCase):

	def setUp(self):
		self._file_path_1 = os.path.join(TEST_DIR,'parallel.yml')
	
	def test_parallel_metadata_object_creation(self):
		parallel_metadata = metadata.Parallel(file_path=self._file_path_1)
		self.assertIsInstance(parallel_metadata,metadata.Parallel)
		self.assertIsInstance(parallel_metadata.data,dict)