# -*- encoding: utf-8 -*-

from . import code
from . import metadata


class BaseParallelizer(object):
    """Define a set of functions required on each paralelization method."""

    @staticmethod
    def insert_lines(raw,insertions=[]):
        """Given a raw string, perfonms a set of insertions on it.

        Args:
            raw (str): The string on which some string insertions
                must be performed.
            insertions (List[tuple(str,int,int)]): A list of directives 
                to be inserted in the given section of raw code.

        Returns:
            str, a raw string with some insertions performed on it.
        """
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

    def get_raw_pragma(self,directive_name,clauses):
        """Returns a raw pragma with its clausules.

        Args:
            directive_name (str): An OpenMP directive.
            clauses (dict): OpenMP clauses name an its arguments.

        Returns: 
            A raw OpenMP directive.
        """
        raise NotImplementedError('This method needs to be implemented')

    def insert_directives(self,function_name,directives):
        """Insert a set of directive on the given function.


        Args:
            function_name (str): The name of a given function
                existing in the code to be paralleized.
            directives (dict): Containing the directives to be 
                applied to the given function.

        Example:
            The _code attribute has information about the code 
            to be paralleized, if we perform 
            _code.get_function_raw(function_name) we will get 
            the raw code of the function to be parallelized.


        """
        raise NotImplementedError('This method needs to be implemented')

    def parallelize(self,metadata):
        """Performs the code paralelization.

        Args:
            metadata (metadata.ParallelFile): A file in YML format containing
                information about how to paralleize the given code.
        """
        raise NotImplementedError('This method needs to be implemented')


class OpenMP(BaseParallelizer):

    def __init__(self,file_path=None,raw_code=None):
        """Allow code parallelization with OpenMP compiler directives.

        Args:

            file_suffix (str): The suffix of the intermediate file created. 
            file_path (Optional[str]): A unique path to the file to be parallelized.
            raw_code (Optional[str]): The raw code to be parallelized. 
        """

        #: code.CCode: An instance that contains the information about the ccode.
        self._code = code.CCode(
            file_suffix='omp_',
            file_path=file_path,
            raw_code=raw_code
        )

    def get_raw_pragma(self,directive_name,clauses):
        """Returns a raw pragma with its clausules.

        Args:
            directive_name (str): An OpenMP directive.
            clauses (dict): OpenMP clauses name an its arguments.

        Returns: 
            A raw OpenMP directive.
        """
        raw_pragma = '#pragma omp %s %s'
        raw_clauses = ''

        for clause_name, value in clauses.items():
            raw_clauses += clause_name

            if type(value) is list:
                raw_clauses += '(' + ','.join(value) + ') '

            elif type(value) is int:
                raw_clauses += '(' + str(value) + ') '

            else:
                raw_clauses += '(' + value + ') '

            # raw_clauses = raw_clauses.replace("'","")

        return raw_pragma % (directive_name,raw_clauses)

    def get_parallel_pragma_insertions(self,function_name,directives):
        """Returns a set of insertions to be performed in a given function.

        Returns the inserts that must be made to include the parallel 
        pragma in the body of the function with the given function_name.

        Args:
            function_name (str): The name of te function we want to
                insert the parallel pragma.
            directives (dict): Containing the directives to be 
                applied to the function with the given function_name.

        Example:

            Each insetion is a tuple with the following format:
            (
                raw_code,
                line
            )

            It describes the raw_code to be inserted in the specified
            line in the code. The insetion line number is relative to
            the function line number.

            For example, if the given function_name is **sum**.

            13 void sum(int * A, int * B, int * C)
            14 {
            15    for (int i = 0; i < 1000; ++i)
            15    {
            17       C[i] = A[i] + B[i];
            18    }
            19 }

            And the **directives** as they are in the paralle.yml file:

            ...
            parallel:
                scope: 0
                clauses:
                    num_threads: 4
            ...

            The set of inserts is:

            [
                ('#pragma omp parallel num_threads(4)',14),
                ('{',14),
                ('}',19)
            ]
        
        """
        insertions = []
        if 'parallel' in directives:
            properties = directives.get('parallel','')
            clauses = properties.get('clauses','')
            raw_pragma = self.get_raw_pragma('parallel',clauses)

            # Determining the scope of the parallel pragma
            scope = properties.get('scope','')

            # If in the parallel directive properties is not present 
            # the scope property no insertions are performed
            if scope is not '':
                begin, end = self._code.get_for_loops_scope(function_name,scope)

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
        insertions += self.get_parallel_pragma_insertions(function_name,directives)
        
        # For pragmas directives insertions
        insertions += self.get_for_pragmas(function_name,directives)

        raw_code = self._code.get_function_raw(function_name)
        new_raw_code = self.insert_lines(raw_code,insertions)

        self._code.update_function_raw_code(function_name,new_raw_code)

        return insertions

    def parallelize(self, metadata):
        self._metadata = metadata
        openmp = metadata.ParallelFile.OMP
        functs_directives = self._metadata.get_directives(openmp)
        for funct_name, directives in functs_directives:
            self.insert_directives(funct_name,directives)

        return self._code


class OpenACC(BaseParallelizer):

    _PARALLEL_METHOD = 'acc'

    def __init__(self,metadata=None,file_path=None,raw_code=None):
        """Creates an code annotated with OpenMP Directives."""
        super(OpenACC,self).__init__(
            metadata=metadata,
            file_suffix='acc_',
            file_path=file_path,
            raw_code=raw_code
        )

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

        # Data directive insertions (This must by inserted first)
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