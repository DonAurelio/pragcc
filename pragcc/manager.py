# -*- encoding: utf-8 -*-

import tempfile
from . import metadata
from . import parallelizer


class OpenMPManager(object):

	def __init__(self):
		pass

	def get_annotated_code(self,raw_parallel_file,raw_c_source_code):
		parallel_metadata = None
		with tempfile.TemporaryFile() as file:
			file.write(raw_parallel_file)

		openmp = parallel.OpenMP(file_path,parallel_metadata) 


class OpenACCManager(object):

	def __init__(self):
		pass