# -*- encoding: utf-8 -*-

import tempfile
from . import metadata
from . import parallelizer


class OpenMPManager(object):

    def __init__(self):
        pass

    def get_annotated_code(self,raw_parallel_file,c_raw_code):

        parallel_meta = metadata.ParallelFile(raw_text=raw_parallel_file)
        with tempfile.NamedTemporaryFile(mode='w+t') as file:
            file.write(c_raw_code)
            ccode = parallelizer.OpenMP(
                file_path=file.name,
                parallel_metadata=parallel_meta
            ) 


        # file , file_path = tempfile.mkstemp(suffix=None, prefix=None, dir=None, text='w')
        # print("FILE PATH:",file_path)
        # file.close()

        # openmp = parallel.OpenMP(file_path,parallel_metadata)

        return parallel_meta.data


class OpenACCManager(object):

    def __init__(self):
        pass