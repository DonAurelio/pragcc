# -*- encoding: utf-8 -*-

from . import code
from . import metadata

class DirectiveFactory(object):
    """Deals with OpenMP and OpenACC raw pragmas creation."""

    def create_raw_pragma(self,library_name,directive_name,clauses):
        """Return a raw pragma with its clausules.

        Args:
            libary_name (str): omp or acc.
            directive_name (str): the name of the directive 
                to be created.
            clauses (dict): clauses applied to that directive 
                an its arguments.

        Returns: 
            A raw pragma.
        """
        raw_pragma = '#pragma %s %s %s'
        raw_clauses = ''

        for clause_name, value in clauses.items():
            raw_clauses += clause_name

            # Clause with no arguments
            if value is None:
                raw_clauses += ' '

            # Clause witha list of arguments string
            elif type(value) is list:
                raw_clauses += '(' + ','.join(value) + ') '

            # Clause with a single argument int
            elif type(value) is int:
                raw_clauses += '(' + str(value) + ') '

            # Clause with a single argument string
            else:
                raw_clauses += '(' + value + ') '

        return raw_pragma % (library_name,directive_name,raw_clauses)


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
            metadata (metadata.Parallel): A file in YML format containing
                information about how to paralleize the given code.
        """
        raise NotImplementedError('This method needs to be implemented')


class OpenMP(BaseParallelizer):

    def __init__(self,file_path=None,raw_code=None):
        """Allow code parallelization with OpenMP compiler directives.

        Args:
            file_path (Optional[str]): A unique path to the file to be parallelized.
            raw_code (Optional[str]): The raw code to be parallelized. 
        """

        super(OpenMP,self).__init__()

        #: code.CCode: An instance that contains the information about the ccode.
        self._code = code.CCode(
            file_suffix='mp_',
            file_path=file_path,
            raw_code=raw_code
        )

        #: DirectiveFactory: To create OpenMP raw pragmas.
        self._directive_factory = DirectiveFactory()

    @property
    def code(self):
        return self._code

    def get_raw_pragma(self,directive_name,clauses):
        """Return an OpenMP raw pragma.

        Args:
            directive_name (str): An OpenMP directive.
            clauses (dict): OpenMP clauses name an its arguments.

        Returns: 
            A raw OpenMP pragma.
        """

        raw_pragma = self._directive_factory.create_raw_pragma(
            library_name='omp',
            directive_name=directive_name,
            clauses=clauses
        )

        return raw_pragma

    def get_parallel_directive_inserts(self,function_name,directives):
        """Return the inserts needed to include the parallel directive.
        
        Returns the inserts that must be made to include the parallel 
        directivein the body of the function with the given function_name.

        Args:
            function_name (str): The name of te function in which the
                parallel directive will be inserted.
            directives (dict): Directives to be applied to the 
                function with the given function_name.

        Example:

            Each insetion to be performed in a given function
            has the following format.

            (
                raw_code, # Code to be inserted 
                line # Line in which the code will be inserted
            )

            If we want to place the 'parallel' directive on the 
            following code. 

            Given the function 'sum'

            0 void sum(int * A, int * B, int * C)
            1 {
            2    for (int i = 0; i < 1000; ++i)
            3    {
            4       C[i] = A[i] + B[i];
            5    }
            6 }

            And the following parallel 'directive' metadata
            ...
            parallel:
                scope: 0
                clauses:
                    num_threads: 4
            ...

            This function will retunr the follwing list of 
            insertions.

            [
                ('#pragma omp parallel num_threads(4)',2),
                ('{',2),
                ('}',6)
            ]
        
        """
        insertions = []
        if 'parallel' in directives:
            properties = directives.get('parallel',{})
            clauses = properties.get('clauses',{})

            raw_pragma = self.get_raw_pragma('parallel',clauses)

            # Determining the scope of the parallel pragma
            scope = properties.get('scope','')

            # If in the parallel directive properties is not present 
            # the scope property no insertions are performed
            if scope != '':
                directive_scope = self._code.get_for_loops_scope(function_name,scope)
                if directive_scope:
                    begin, end = directive_scope

                    insertions = [
                        (raw_pragma,begin),
                        ('{',begin),
                        ('}',end + 1)
                    ]

        return insertions

    def get_parallel_for_directive_inserts(self,function_name,directives):
        """Return the parallel for directive raw code.

        Returns the inserts that must be made to include the parallel for
        directive in the body of the function with the given function_name.

        Given the function 'sum'

        0 void sum(int * A, int * B, int * C)
        1 {
        2    for (int i = 0; i < 1000; ++i) // loop_nro = 0 
        3    {
        4       C[i] = A[i] + B[i];
        5    }
        6 }

        ...
        parallel_for:
            - nro: 0                # loop_nro = 0
              clauses:
                private:[i]
                reduction: '+:sum'
            - nro: 1                # This loop does not exist.
              clauses:
                private:[j]
        ...

        The algoritm generate a set of insertions for each item in
        the parallel_for list. If there is an item who nro is not in 
        the source code data, that item does not generate insertions.
        Then only one insetion is generated.

        [
            ('#pragma omp parallel for private(i) reduction(+:sum)',2),
        ]
        """

        insertions = []
        if 'parallel_for' in directives:
            loops_directives = directives.get('parallel_for')
            for loop_directive in loops_directives:
                
                loop_nro = loop_directive['nro']
                loop_clauses = loop_directive.get('clauses',{})

                raw_pragma = self.get_raw_pragma('parallel for',loop_clauses)
                loop_line_in_code = self._code.get_loop_line(function_name,loop_nro)

                # If the loop with the given loop_nro is founded
                # in the source code
                if loop_line_in_code:
                    insertions += [(raw_pragma,loop_line_in_code)]

        return insertions

    def get_for_directive_inserts(self,function_name,directives):
        """Returns the parallel for directive raw code."""
        insertions = []
        if 'for' in directives:
            loops_directives = directives['for']
            for loop_directive in loops_directives:
                
                loop_nro = loop_directive['nro']
                loop_clauses = loop_directive('clauses',{})

                raw_pragma = self.get_raw_pragma('for',loop_clauses)
                loop_line_in_code = self._code.get_loop_line(function_name,loop_nro)

                # If the loop with the given loop_nro is founded
                # in the source code
                if loop_line_in_code:
                    insertions += [(raw_pragma,loop_line_in_code)]

        return insertions

    def insert_directives(self,function_name,directives):
        insertions = []

        #  Available directives

        # Parallel directive inserts
        insertions += self.get_parallel_directive_inserts(function_name,directives)
        
        # For directive inserts
        insertions += self.get_for_directive_inserts(function_name,directives)

        # Parallel For directive inserts
        insertions += self.get_parallel_for_directive_inserts(function_name,directives)

        raw_code = self._code.get_function_raw(function_name)
        new_raw_code = self.insert_lines(raw_code,insertions)

        self._code.update_function_raw_code(function_name,new_raw_code)

        return insertions

    def parallelize(self, meta):
        """Return a parallelized cccode object.

        Args:
            meta (metadata.Parallel): The paralleization metadata.

        Returns:
            code.CCode, which raw code is annotated with OpenMP
                compiler directives.
        """
        self._meta = meta
        openmp = metadata.Parallel.OPEN_MP

        functs_directives = self._meta.get_directives(openmp)
        for funct_name, directives in functs_directives:
            self.insert_directives(funct_name,directives)

        return self._code


class OpenACC(BaseParallelizer):

    def __init__(self,file_path=None,raw_code=None):
        """Allow code parallelization with OpenACC compiler directives.

        Note: file_path or raw_code must be given, but not both.

        Args:
            file_path (Optional[str]): A unique path to the file to be parallelized.
            raw_code (Optional[str]): The raw code to be parallelized. 
        """
        
        super(OpenACC,self).__init__()

        #: code.CCode: An instance that contains the information about the ccode.
        self._code = code.CCode(
            file_suffix='mp_',
            file_path=file_path,
            raw_code=raw_code
        )

        #: DirectiveFactory: To create OpenMP raw pragmas.
        self._directive_factory = DirectiveFactory()

    @property
    def code(self):
        return self._code

    def get_raw_pragma(self,directive_name,clauses):
        """Return an OpenACC raw pragma.

        Args:
            directive_name (str): An OpenMP directive.
            clauses (dict): OpenMP clauses name an its arguments.

        Returns: 
            A raw OpenMP pragma.
        """

        raw_pragma = self._directive_factory.create_raw_pragma(
            library_name='acc',
            directive_name=directive_name,
            clauses=clauses
        )

        return raw_pragma

    def get_data_directive_inserts(self,function_name,directives):
        """Return the inserts needed to include the data directive.
        
        Returns the inserts that must be made to include the data 
        directive in the body of the function with the given function_name.

        Args:
            function_name (str): The name of te function in which the
                parallel directive will be inserted.
            directives (dict): Directives to be applied to the 
                body of the function with the given function_name.

        Example:

            Each insetion to be performed in a given function
            has the following format.

            (
                raw_code, # Code to be inserted 
                line # Line in which the code will be inserted
            )

            If we want to place the 'data' directive on the 
            following code. 

            Given the function 'sum'

            0 void sum(int * A, int * B, int * C)
            1 {
            2    for (int i = 0; i < 1000; ++i)
            3    {
            4       C[i] = A[i] + B[i];
            5    }
            6 }

            And the following 'data directive' metadata
            ...
            data:
                scope: 0
                clauses:
                    copy: [A,B,C]
            ...

            This function will return the follwing list of 
            insertions.

            [
                ('#pragma acc data copy(A,B,C) ',2),
                ('{',2),
                ('}',6)
            ]
        
        """

        insertions = []
        if 'data' in directives:
            properties = directives.get('data',{})

            scope = properties.get('scope','')
            clauses = properties.get('clauses',{})
            raw_pragma = self.get_raw_pragma('data',clauses)

            # Determining the scope of the data pragma
            if scope != '':
                directive_scope = self._code.get_for_loops_scope(function_name,scope)

                if directive_scope:
                    begin, end = directive_scope

                    insertions = [
                        (raw_pragma,begin),
                        ('{',begin),
                        ('}',end + 1)
                    ]

        return insertions

    def get_parallel_loop_directive_inserts(self,function_name,directives):
        """Return the parallel loop directive raw code.

        Returns the inserts that must be made to include the parallel for
        directive in the body of the function with the given function_name.

        Given the function 'sum'

        0 void sum(int * A, int * B, int * C)
        1 {
        2    for (int i = 0; i < 1000; ++i) // loop_nro = 0 
        3    {
        4       C[i] = A[i] + B[i];
        5    }
        6 }

        ...
        parallel_loop:
            - nro: 0                # loop_nro = 0
              clauses:
                vector_length: 100
                num_gangs: 100
                gang:
            - nro: 1                # This loop does not exist.
              clauses:
                private:[j]
        ...

        The algoritm generate a set of insertions for each item in
        the parallel_for list. If there is an item who nro is not in 
        the source code data, that item does not generate insertions.
        Then only one insertion generated on this case is.

        [
            ('#pragma acc parallel loop num_gangs(100) vector_lenght(100) gang ',2),
        ]
        """

        insertions = []
        if 'parallel_loop' in directives:
            loops_directives = directives.get('parallel_loop')
            for loop_directive in loops_directives:
                
                loop_nro = loop_directive['nro']
                loop_clauses = loop_directive.get('clauses',{})

                raw_pragma = self.get_raw_pragma('parallel loop',loop_clauses)
                loop_line_in_code = self._code.get_loop_line(function_name,loop_nro)

                # If the loop with the given loop_nro is founded
                # in the source code
                if loop_line_in_code:
                    insertions += [(raw_pragma,loop_line_in_code)]

        return insertions

    def get_loop_directive_inserts(self,function_name,directives):
        """Return the parallel loop directive raw code.

        Returns the inserts that must be made to include the parallel for
        directive in the body of the function with the given function_name.

        Given the function 'sum'

        0 void sum(int * A, int * B, int * C)
        1 {
        2    for (int i = 0; i < 1000; ++i) // loop_nro = 0 
        3    {
        4       C[i] = A[i] + B[i];
        5    }
        6 }

        ...
        loop:
            - nro: 0                # loop_nro = 0
              clauses:
                vector_length: 100
                num_gangs: 100
                vector:
            - nro: 1                # This loop does not exist.
              clauses:
                private:[j]
        ...

        The algoritm generate a set of insertions for each item in
        the parallel_for list. If there is an item who nro is not in 
        the source code data, that item does not generate insertions.
        Then only one insertion generated on this case is.

        [
            ('#pragma acc loop num_gangs(100) vector_lenght(100) vector ',2),
        ]
        """

        insertions = []
        if 'loop' in directives:
            loops_directives = directives.get('loop')
            for loop_directive in loops_directives:
                
                loop_nro = loop_directive['nro']
                loop_clauses = loop_directive.get('clauses',{})

                raw_pragma = self.get_raw_pragma('loop',loop_clauses)
                loop_line_in_code = self._code.get_loop_line(function_name,loop_nro)

                # If the loop with the given loop_nro is founded
                # in the source code
                if loop_line_in_code:
                    insertions += [(raw_pragma,loop_line_in_code)]

        return insertions


    def insert_directives(self,function_name,directives):
        insertions = []

        #  Available directives

        # Data directive inserts
        insertions += self.get_data_directive_inserts(function_name,directives)
        
        # Parallel loop directive inserts
        insertions += self.get_parallel_loop_directive_inserts(function_name,directives)

        # Loop directive inserts
        insertions += self.get_loop_directive_inserts(function_name,directives)

        raw_code = self._code.get_function_raw(function_name)
        new_raw_code = self.insert_lines(raw_code,insertions)

        self._code.update_function_raw_code(function_name,new_raw_code)

        return insertions

    def parallelize(self, meta):
        """Return a parallelized cccode object.

        Args:
            meta (metadata.Parallel): The paralleization metadata.

        Returns:
            code.CCode, which raw code is annotated with OpenMP
                compiler directives.
        """
        self._meta = meta
        openacc = metadata.Parallel.OPEN_ACC

        functs_directives = self._meta.get_directives(openacc)
        for funct_name, directives in functs_directives:
            self.insert_directives(funct_name,directives)

        return self._code
