# -*- encoding: utf-8 -*-

import os
import yaml
import shutil
from . import settings

class ParallelFile(object):

    OMP = 'omp'
    OACC = 'acc'

    BLOCK_DIRECTIVES = ['parallel','kernels','data']
    LINE_DIRECTIVES = ['for','loop']

    @staticmethod
    def create_file(dir_path):
        """Creates a parallel.yml file.

        Creates the indicated parallel.yml file given the directory where it 
        should be created.

        Args:
            dir_path (str): An unique location to the dir on which a 
                parallel.yml will be created.

        Returns:
            A ParallelFile instance which contains the parallel.yml data.

        """

        file_path = os.path.join(dir_path,settings.PARALLEL_FILE_NAME)
        base_file_path = os.path.join(settings.PARALLEL_FILE_DIR,
            settings.PARALLEL_FILE_NAME)
        shutil.copyfile(src=base_file_path,dst=file_path)

        return ParallelFile(dir_path) if base_file_path else None

    @staticmethod
    def is_block_directive(directive_name):
        return directive_name in ParallelFile.BLOCK_DIRECTIVES

    def __init__(self, dir_path):
        """Parallel file metadata class.

        The parallel file describes how a code that follows a given cellular 
        automata programming pattern should to be parallelized.

        Args:
            dir_path (str): An unique location to the dir on which a 
                parallel.yml must exists.

        """

        parallel_file_path = os.path.join(dir_path,settings.PARALLEL_FILE_NAME)
        with open(parallel_file_path,'r') as parallelfile:
            self._data = yaml.load(parallelfile)
            self._dir_path = dir_path

    @property
    def file_path(self):
        return os.path.join(self._dir_path,settings.PARALLEL_FILE_NAME)

    @property
    def data(self):
        return self._data
        
    def get_directives(self,dtype):
        # Getting the parallelizable functions metadata.
        parallel = self._data['functs']['parallel']
        
        functs_metadata = []
        for funct_name, data in parallel.items():
            if dtype in data:
                directives = data[dtype]
                functs_metadata.append((funct_name,directives))

        return tuple(functs_metadata)

    @staticmethod
    def get_loop_clauses(loop_metadata):
        return loop_metadata['clauses']

    @staticmethod
    def get_loop_nro(loop_metadata):
        return int(loop_metadata['nro'])


    def __str__(self):
        """Returns a string with the parallelfile object data."""
        raw_code = 'Directory: %s \nData: \n%s'
        return raw_code % (self._dir_path,str(self._data))