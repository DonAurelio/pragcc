from flask import request
from flask_restplus import Namespace, Resource
from catt.core.manager import TemplatesFolderManager
from catt.core.manager import TemplateManager
from catt.core.manager import ParallelManager
from .cafile import cafile_model


# Defining the name space for Catt templates
api = Namespace('template',description='Allows to obtain information of the available templates.')

@api.route('/')
class TemplateList(Resource):
    """Deals with templates list tasks."""

    def get(self):
        """Returns a list of the available parallel pattern templates."""
        manager = TemplatesFolderManager()
        data = {
            'template_list': manager.list_available_templates()
        }
        return data


@api.route('/detail/<string:name>')
class TemplateDetail(Resource):
    """Deals with templates detail tasks."""

    def get(self,name):
        """Returns the template info given its name."""
        manager = ParallelManager()
        data = {
            'template_datail': manager.get_template_info(name)
        }
        return data

    @api.expect(cafile_model)
    def post(self,name):
        """Returns c99 source code give a cafile metadata."""

        data = request.json
        manager = TemplateManager()
        rendered_template = manager.get_rendered_template(name,data)

        return rendered_template


# Defining error handlers
from django.template import TemplateDoesNotExist


@api.errorhandler(TemplateDoesNotExist)
def handle_template_does_not_exist(error):
    """Returns a custom message for TemplateDoesNotExist."""
    return {'message':'Some error has ocurred !!','error':error}
