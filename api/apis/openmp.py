from flask import request
from flask_restplus import Namespace, Resource, fields
from pragcc.manager import OpenMPManager

# Defining the name space for Catt cafile
api = Namespace('openmp',description='An interface to the openmp code annotation directives.')

# Defining cafile json model
Code = api.model('Code',{
    'parallel_metadata': fields.String(
        required=True,
        description='A description about how the C source should be parallelized or annotated.' 
    ),
    'c_source_code': fields.String(
        required=True,
        description='The C source code to be parallelized or annotated with compiler directives.'
    )

})


@api.route('/parallelize')
class PragccOpenMP(Resource):
    """Deals with the parallelization of C99 Source code with OpenMP directives."""

    @api.expect(Code)
    def post(self):
        """Returns C99 source code annotated with OpenMP compiler directives."""

        data = request.json
        rendered_template = ''
        manager = OpenMPManager()
        parallel_metadata = data['parallel_metadata']
        c_source_code = data['c_source_code']
        rendered_template = manager.get_annotated_code(
            parallel_metadata,c_source_code)

        return data