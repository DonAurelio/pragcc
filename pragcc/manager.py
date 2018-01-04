# -*- encoding: utf-8 -*-

import tempfile
from .core import metadata
from .core import parallelizer
from .core.parser.c99.pycparser.plyparser import ParseError


class OpenMPManager(object):

    def get_annotated_code_data(self,raw_parallel_file,raw_c_code):

        parallel_meta = metadata.Parallel(raw_text=raw_parallel_file)
        openmp_parallelizer = parallelizer.OpenMP(raw_code=raw_c_code)

        try:
            ccode = openmp_parallelizer.parallelize(parallel_meta)
            data = {
                'name': 'omp.c',
                'ftype': ccode.file_type,
                'text': ccode.raw
            }

            error = None

            return data, error

        except ValueError:
            # Possible reason
            # As parallelization runs having as a reference the parallel file
            # if a function contained in the parallel file is not in the 
            # raw code, it can raise a value error.
            
            data = None
            error = (
                "Probably, the functions specified in the parallel.yml file do not match "
                "the functions that are present in the source code."
            )
            return data, error

        except IndexError:
            # Possible reason
            # The code is splitted in sections to be handled easily during 
            # parallelization, to perform the code splitting, the source code
            # must follow the the following format
            #   
            #   // Include section 
            #   #include <....h>
            #   #include <....h>
            # 
            #   // Defines section
            # 
            #   // Functions sectio
            #   int main () {
            # 
            #   }
            # if this format is not present, an IndexError may occurs during code 
            # splitting. 

            data = None
            error = (
                "Your code must be have at least two '#include' lines, "
                "some contants definitions, finally, function definitions."
            )

            return data, error

        except ParseError:
            # Possible reason
            # This error can occurs when the code does not compile correctly 
            # or the given code is not completely C99 that is the versión supported
            # by 'pycparser'

            data = None
            error = (
                "The code does not compile correctly or "
                "it has syntax that is not supported yet by Pycparser."
            )
            
            return data, error




class OpenACCManager(object):

    def __init__(self):
        pass