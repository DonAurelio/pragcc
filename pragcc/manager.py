# -*- encoding: utf-8 -*-

import tempfile
from . import metadata
from . import parallelizer


class OpenMPManager(object):

    def __init__(self):
        pass

    def get_annotated_code(self,raw_parallel_file,raw_c_source_code):
        parallel_metadata = None
        ccode
        with tempfile.NamedTemporaryFile(mode='w+t') as file:
            file.write(raw_parallel_file)
            print("FILE NAME:",file.name)
            parallel_metadata = metadata.ParallelFile.create_file(file.name)

        # file , file_path = tempfile.mkstemp(suffix=None, prefix=None, dir=None, text='w')
        # print("FILE PATH:",file_path)
        # file.close()

        # openmp = parallel.OpenMP(file_path,parallel_metadata) 


class OpenACCManager(object):

    def __init__(self):
        pass