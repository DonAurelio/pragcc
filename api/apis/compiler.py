from flask import request
from flask_restplus import Namespace, Resource, fields

from compiler.manager import GccManager
from . import data


# Defining the name space for Catt cafile
api = Namespace('compile',description='Annotate code with OpenMP compiler directives.')


# Defining raw code model
Code = api.model('Code',{
    'raw_c_code': fields.String(
        required=True,
        description='The C source code to be compiled.',
        default=data.RAW_C_CODE
    )

})


@api.route('')
class Gcc(Resource):
    """Deals with the parallelization of C99 Source code with OpenMP directives."""

    def head(self):
        """Used for clients to check if the resource is available."""
        data = {}
        return data

    @api.expect(Code)
    def post(self):
        """Returns C99 source code annotated with OpenMP compiler directives."""

        data = request.json
        raw_parallel_file = data['raw_parallel_file']
        raw_c_code = data['raw_c_code']

        manager = GccManager()
        stdout, stderror = manager.get_annotated_code_data(
            raw_parallel_file=raw_parallel_file,
            raw_c_code=raw_c_code
        )

        data = {
            'message':'OpenMP parallelization successfull !',
            'data': code_data
        }

        return data