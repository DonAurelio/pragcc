from flask_restplus import Api

from .openmp import api as openmp_namespace
# from .openacc import api as openacc_namespace


api = Api(
    title='Pragcc Api',
    version='1.0',
    description="""Provides an interface to annotate C99 sequential code with
    OpenMP and OpenACC compiler directives."""
)

api.add_namespace(openmp_namespace)
# api.add_namespace(openacc_namespace)
