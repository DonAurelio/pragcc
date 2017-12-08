from flask_restplus import Api

from .pragcc import api as pragcc_namespace


api = Api(
    title='Pragcc Api',
    version='1.0',
    description="""Provides an interface to annotate C99 sequential code with
    OpenMP and OpenACC compiler directives."""
)

api.add_namespace(pragcc_namespace)
