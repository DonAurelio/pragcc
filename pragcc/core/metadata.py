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

    # This function looks for give and example of a paralell file format.
    # in a given directory.
    # @staticmethod
    # def create_file(dir_path):
    #     """Creates a parallel.yml file.
    #     Creates the indicated parallel.yml file given the directory where it 
    #     should be created.
    #     Args:
    #         dir_path (str): An unique location to the dir on which a 
    #             parallel.yml will be created.
    #     Returns:
    #         A ParallelFile instance which contains the parallel.yml data.
    #     """

    #     file_path = os.path.join(dir_path,settings.PARALLEL_FILE_NAME)
    #     base_file_path = os.path.join(settings.PARALLEL_FILE_DIR,
    #         settings.PARALLEL_FILE_NAME)
    #     shutil.copyfile(src=base_file_path,dst=file_path)

    #     return ParallelFile(dir_path) if base_file_path else None

    @staticmethod
    def _load_from_text(text):
        data = yaml.load(text)
        return data

    @staticmethod
    def _load_from_file(file_path):
        with open(file_path,'r') as file:
            data = yaml.load(file)
            return data

    def __init__(self,raw_text=None,file_path=None, data=None):
        """Parallel file metadata class.

        The parallel file describes how a code that follows a given cellular 
        automata programming pattern should to be parallelized.

        Args:
            dir_path (str): An unique location to the dir on which a 
                parallel.yml must exists.

        """

        if raw_text:
            self._data = self._load_from_text(raw_text)
        elif file_path:
            self._data = self._load_from_file(file_path)
        elif data:
            self._data = data
        else:
            self._data = None

    @property
    def data(self):
        return self._data


    # DIRECIVES BASED METHODS
    @staticmethod
    def is_block_directive(directive_name):
        return directive_name in ParallelFile.BLOCK_DIRECTIVES

    @staticmethod
    def get_loop_clauses(loop_metadata):
        return loop_metadata['clauses']

    @staticmethod
    def get_loop_nro(loop_metadata):
        return int(loop_metadata['nro'])

    def get_directives(self,dtype):
        # Getting the parallelizable functions metadata.
        parallel = self._data['functs']['parallel']
        
        functs_metadata = []
        for funct_name, data in parallel.items():
            if dtype in data:
                directives = data[dtype]
                functs_metadata.append((funct_name,directives))

        return tuple(functs_metadata)