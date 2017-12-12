# -*- encoding: utf-8 -*-

import tempfile
from .core import metadata
from .core import parallelizer


class OpenMPManager(object):

    def get_annotated_code_data(self,raw_parallel_file,raw_c_code):

        parallel_meta = metadata.ParallelFile(raw_text=raw_parallel_file)
        openmp_parallelizer = parallelizer.OpenMP(
        	metadata=parallel_meta,
        	raw_code=raw_c_code
        )
        ccode = openmp_parallelizer.parallelize()

        data = {
            'name': 'omp.c',
            'ftype': ccode.file_type,
            'text': ccode.raw
        }

        return data


class OpenACCManager(object):

    def __init__(self):
        pass