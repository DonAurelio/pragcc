# -*- encoding: utf-8 -*-

from pragcc.core import metadata, parallelizer

from tests.pragcc import test_data

import unittest


def pragmas_equals(a,b):
    pragma_1 = set(a.split(' '))
    pragma_2 = set(b.split(' '))

    return pragma_1 == pragma_2


class TestDirectiveFactory(unittest.TestCase):

    def setUp(self):
        self._parallel = metadata.Parallel(
            data=test_data.METADATA_FOR_SIMPLE_CODE_FUNCTION_LOOP
        )

        self._directive_factory = parallelizer.DirectiveFactory()

    def test_create_open_mp_parallel_directive(self):
        functions_directives = self._parallel.get_directives('mp')
        function_name, directives = functions_directives[0]
        parallel_directive = directives.get('parallel')
        clauses = parallel_directive.get('clauses')

        pragma = self._directive_factory.create_raw_pragma(
            library_name='omp',
            directive_name='parallel',
            clauses=clauses
        )

        expected_pragma = '#pragma omp parallel num_threads(4) shared(A,B,C) default(none) '

        self.assertTrue(pragmas_equals(pragma,expected_pragma))

    def test_create_open_mp_parallel_directive_no_clauses(self):

        pragma = self._directive_factory.create_raw_pragma(
            library_name='omp',
            directive_name='parallel',
            clauses={}
        )

        expected_pragma = '#pragma omp parallel '

        self.assertTrue(pragmas_equals(pragma,expected_pragma))
