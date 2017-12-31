from flask import request
from flask_restplus import Namespace, Resource, fields

from pragcc.manager import OpenMPManager
from compiler.manager import GccManager

from . import data


# Defining the name space for Catt cafile
api = Namespace('openmp',description='Annotate code with OpenMP compiler directives.')


# Defining cafile json model
Files = api.model('Files',{
    'raw_parallel_file': fields.String(
        required=True,
        description='A description about how the C source should be parallelized or annotated.',
        default=data.PARALLEL_FILE
    ),
    'raw_c_code': fields.String(
        required=True,
        description='The C source code to be parallelized or annotated with compiler directives.',
        default=data.RAW_C_CODE
    )

})


@api.route('')
class OpenMP(Resource):
    """Deals with the parallelization of C99 Source code with OpenMP directives."""

    def head(self):
        """Used for clients to check if the resource is available."""
        data = {}
        return data

    @api.expect(Files)
    def post(self):
        """Returns C99 source code annotated with OpenMP compiler directives."""

        data = request.json
        raw_parallel_file = data.get('raw_parallel_file','')
        raw_c_code = data.get('raw_c_code','')

        # Checking if the parallel file was given
        if not raw_parallel_file:
            message = 'Parallel file was not provided'
            return message, 400

        # Checking if the C99 source code was given
        if not raw_c_code:
            message = 'C99 source code was not provided'
            return message, 400

        # Checking if source code compiles 
        # manager = GccManager()
        # stdout, stderror = manager.compile_raw_code(raw_c_code)

        # if stderror:
        #     return stderror, 400


        manager = OpenMPManager()
        code_data = manager.get_annotated_code_data(
            raw_parallel_file=raw_parallel_file,
            raw_c_code=raw_c_code
        )

        return code_data