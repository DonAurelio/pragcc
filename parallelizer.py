# -*- encoding: utf-8 -*-

import code
import metadata


class BaseParallelizer(object):

    _PARALLEL_METHOD = 'no method'

    def __init__(self,file_path,parallel_metadata,file_suffix):
        """Parallelizer class.

        This class deals with code parallelization given a CCode instance
        and a ParallelFile instance.

        Note:
            OpenMP instaces should not modify the state of any the 
            CCcode instante and the ParallelFile instance. The OpenMP
            instance just can check the state of them to perform the
            parallelization.

        Args:
            file_path (str): A unique path to the file to be parallelized.

        """

        #: code.CCode: An instance that contains the information about the code
        self._code = code.CCode(file_path,file_suffix)
        #: metadata.ParallelFIle: A the parallel file data
        self._metadata = parallel_metadata


    def get_raw_pragma(self,directive_name,clauses):
        raw_pragma = '#pragma %s %s %s'
        raw_clauses = ''

        for clause, value in clauses.items():
            raw_clauses += clause

            if type(value) is list:
                raw_clauses +=  str(tuple(value)) + ' '
            else:
                raw_clauses += '(' + value + ') '

            raw_clauses = raw_clauses.replace("'","")

        return raw_pragma % (self._PARALLEL_METHOD,directive_name,raw_clauses)

    @staticmethod
    def insert_lines(raw,insertions=[]):
        lines = raw.splitlines()
        numbered_lines = list(enumerate(lines))
        fake_line = -1

        new_numbered_lines = []
        for new_raw, insertion_line in insertions:
            for list_index, code in enumerate(numbered_lines):
                line_in_code = code[0]
                if line_in_code is insertion_line:
                    new_numbered_lines += numbered_lines[:list_index]
                    new_numbered_lines += [(fake_line,new_raw)]
                    new_numbered_lines += numbered_lines[list_index:]

            numbered_lines = new_numbered_lines
            new_numbered_lines = []

        return '\n'.join([code[1] for code in numbered_lines])

    def insert_directives(self,function_name,directives):
        pass

    def parallelize(self):
        pass


class OpenMP(BaseParallelizer):

    _PARALLEL_METHOD = 'omp'

    def __init__(self,file_path,parallel_metadata):
        super(OpenMP,self).__init__(
            file_path,parallel_metadata,file_suffix='omp_')

    def get_parallel_pragma(self,function_name,directives):
        insertions = []
        if 'parallel' in directives:
            clauses = directives['parallel']
            raw_pragma = self.get_raw_pragma('parallel',clauses)

            loops_directives = directives['for']

            if loops_directives:
                first_loop = loops_directives[0]
                first_loop_nro = self._metadata.get_loop_nro(first_loop)

                begin, end = self._code.get_for_loops_scope(
                    function_name,first_loop_nro)

                insertions = [
                    (raw_pragma,begin),
                    ('{',begin),
                    ('}',end + 1)
                ]

        return insertions

    def get_for_pragmas(self,function_name,directives):
        insertions = []
        if 'for' in directives:
            loops_directives = directives['for']
            for loop_directive in loops_directives:
                
                loop_nro = loop_directive['nro']
                loop_clauses = loop_directive['clauses']

                raw_pragma = self.get_raw_pragma('for',loop_clauses)
                loop_line_in_code = self._code.get_loop_line(function_name,loop_nro)

                insertions += [(raw_pragma,loop_line_in_code)]

        return insertions

    def insert_directives(self,function_name,directives):
        insertions = []

        #  Available directives

        # Parallel directive insetions (THIS FEATURE DO NOT WORK PROPERLY)
        insertions += self.get_parallel_pragma(function_name,directives)
        
        # For pragmas directives insertions
        insertions += self.get_for_pragmas(function_name,directives)

        raw_code = self._code.get_function_raw(function_name)
        new_raw_code = self.insert_lines(raw_code,insertions)

        self._code.update_function_raw_code(function_name,new_raw_code)

        return insertions

    def parallelize(self):
        openmp = metadata.ParallelFile.OMP
        functs_directives = self._metadata.get_directives(openmp)
        for funct_name, directives in functs_directives:
            self.insert_directives(funct_name,directives)

        return self._code


class OpenACC(BaseParallelizer):

    _PARALLEL_METHOD = 'acc'

    def __init__(self,file_path,parallel_metadata):
        super(OpenACC,self).__init__(
            file_path,parallel_metadata,file_suffix='acc_')

    def get_data_pragma(self,function_name,directives):
        insertions = []
        if 'data' in directives:
            clauses = directives['data']
            raw_pragma = self.get_raw_pragma('data',clauses)

            loops_directives = directives['loop']

            if loops_directives:
                first_loop = loops_directives[0]
                first_loop_nro = self._metadata.get_loop_nro(first_loop)

                begin, end = self._code.get_for_loops_scope(
                    function_name,first_loop_nro)

                insertions = [
                    (raw_pragma,begin),
                    ('{',begin),
                    ('}',end + 1)
                ]

        return insertions

    def get_loop_pragmas(self,function_name,directives):
        insertions = []
        if 'loop' in directives:
            loops_directives = directives['loop']
            for loop_directive in loops_directives:
                
                loop_nro = loop_directive['nro']
                loop_clauses = loop_directive['clauses']

                raw_pragma = self.get_raw_pragma('loop',loop_clauses)
                loop_line_in_code = self._code.get_loop_line(function_name,loop_nro)

                insertions += [(raw_pragma,loop_line_in_code)]

        return insertions

    def insert_directives(self,function_name,directives):
        insertions = []

        #  Available directives

        # Data directive insetions (This must by inserted first)
        insertions += self.get_data_pragma(function_name,directives)
        
        # Loops pragmas directives insertions
        insertions += self.get_loop_pragmas(function_name,directives)

        raw_code = self._code.get_function_raw(function_name)
        new_raw_code = self.insert_lines(raw_code,insertions)

        self._code.update_function_raw_code(function_name,new_raw_code)

        return insertions

    def parallelize(self):
        openacc = metadata.ParallelFile.OACC
        functs_directives = self._metadata.get_directives(openacc)
        for funct_name, directives in functs_directives:
            self.insert_directives(funct_name,directives)

        return self._code