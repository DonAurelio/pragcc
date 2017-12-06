# -*- encoding: utf-8 -*-

import os
import shutil
import pprint


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DIR = os.path.join(BASE_DIR,'tests')


def test_code_parsing():
    from parser.c99 import parser
    file_path = os.path.join(TEST_DIR,'stencil.c')

    code_data = parser.get_data_from_cfile(file_path=file_path)
    print('Code Data')
    pprint.pprint(code_data)

def test_code_object():
    import code

    new_raw_code = """
void evolve(bool * in, bool * out)
{
    struct Neighborhood nbhd;
    bool * temp = in;

    for (int i = 1; i <= Generations; ++i)
    {
        for (int i = 0; i < (RowDim*ColDim); ++i)
        {
            nbhd = neighborhood(in,i);
            out[i] = function(nbhd);
        }

        temp = in;
        in = out;
        out = temp;
    }
}
    """

    file_path = os.path.join(TEST_DIR,'stencil.c')

    ccode = code.CCode(file_path)
    print('CCode Raw')
    print(ccode.raw)

    print('CCode Update')
    ccode.update_function_raw_code('evolve',new_raw_code)
    print(ccode.raw)

def test_parallel_metadata():
    import metadata
    parallelfile = metadata.ParallelFile.create_file(dir_path=TEST_DIR)
    print('File path:',parallelfile.file_path)
    print('Data:')
    pprint.pprint(parallelfile.data)
    return parallelfile

def test_code_parallelizer():
    import parallelizer

    file_path = os.path.join(TEST_DIR,'stencil.c')
    parallelfile = test_parallel_metadata()

    omp = parallelizer.OpenMP(file_path,parallelfile)
    pccode = omp.parallelize()
    print('OPENMP Parallelized Code')
    print(pccode.raw)

    acc = parallelizer.OpenACC(file_path,parallelfile)
    acc_code = acc.parallelize()
    print('OPENACC Parallelized Code')
    print(acc_code.raw)

if __name__ == '__main__':
    # test_code_parsing()
    # test_code_object()
    # test_parallel_metadata()
    test_code_parallelizer()