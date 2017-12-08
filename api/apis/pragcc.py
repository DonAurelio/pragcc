from flask import request
from flask_restplus import Namespace, Resource, fields
from pragcc.manager import OpenMPManager
from . import test_data


# Defining the name space for Catt cafile
api = Namespace('pragcc',description='The interface to code annotation directives.')




# Defining cafile json model
Code = api.model('Code',{
    'raw_parallel_file': fields.String(
        required=True,
        description='A description about how the C source should be parallelized or annotated.',
        default=test_data.PARALLEL_FILE
    ),
    'raw_c_code': fields.String(
        required=True,
        description='The C source code to be parallelized or annotated with compiler directives.',
        default=test_data.RAW_C_CODE
    )

})


@api.route('/openmp')
class PragccOpenMP(Resource):
    """Deals with the parallelization of C99 Source code with OpenMP directives."""

    @api.expect(Code)
    def post(self):
        """Returns C99 source code annotated with OpenMP compiler directives."""

        data = request.json
        raw_parallel_file = data['raw_parallel_file']
        raw_c_code = data['raw_c_code']

        manager = OpenMPManager()
        annotated_raw_code = manager.get_annotated_raw_code(
            raw_parallel_file=raw_parallel_file,
            raw_c_code=raw_c_code
        )

        data = {
            'message':'Compilation successfull !',
            'annotated_code': annotated_raw_code
        }

        return data