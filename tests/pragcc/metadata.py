# -*- encoding: utf-8 -*-

from pragcc.core import metadata

from tests.pragcc import test_data

import unittest


class TestParallelFile(unittest.TestCase):

	def setUp(self):
		self._file_path_1 = test_data.PARALLEL_FILE_PATH
	
	def test_parallel_metadata_object_creation(self):
		parallel_metadata = metadata.Parallel(file_path=self._file_path_1)
		self.assertIsInstance(parallel_metadata,metadata.Parallel)
		self.assertIsInstance(parallel_metadata.data,dict)