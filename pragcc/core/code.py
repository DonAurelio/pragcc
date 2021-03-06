# -*- encoding: utf-8 -*-

import os
import shutil
import tempfile
from .parser.c99 import parser


class CCode(object):

    @staticmethod
    def copy_file(base_file_path,file_suffix):
        
        dir_path = os.path.dirname(base_file_path)
        file_name = os.path.basename(base_file_path)
        new_file_name = file_suffix + file_name
        new_file_path = os.path.join(dir_path,new_file_name)
        shutil.copyfile(src=base_file_path,dst=new_file_path)
       
        return new_file_path

    @staticmethod
    def load_data_from_file(file_path):
        code_data = parser.get_data_from_cfile(file_path)
        return code_data

    @staticmethod
    def load_data_from_text(text):
        with tempfile.TemporaryDirectory() as dir_path:
            file_path = os.path.join(dir_path,'temp.c')

            with open(file_path,'w') as file:
                file.write(text)
                file.seek(0)

            return CCode.load_data_from_file(file_path)


    def __init__(self,file_suffix='ccode_',file_path=None,raw_code=None):

        self._file_path = file_path
        self._raw_code = raw_code

        if file_path and not raw_code:
            copied_file_path = CCode.copy_file(file_path,file_suffix)
            self._data = CCode.load_data_from_file(copied_file_path)
        elif raw_code and not file_path:
            self._data = CCode.load_data_from_text(raw_code)
        else:
            # When this happend we need to raise and exception
            # The data dict can't be None
            raise ValueError(
                """file_path or raw_code kwargs any of these 
                parameters must be given. but not both."""
            )
            
    @property
    def raw(self):
        raw_code = ''
        raw_code += self._data['include']
        raw_code += self._data['declaration']
        for function in self._data['functions']:
            raw_code += function['raw'] + '\n'

        return raw_code

    @property
    def file_type(self):
        return 'c99'

    def get_function_raw(self,function_name):
        condition = lambda function: function['name'] in function_name
        function = next(filter(condition,self._data['functions']),None)
        function_raw = ''
        if function:
            function_raw = function['raw']     
        return function_raw

    def get_for_loops_scope(self,function_name,loop_nro): 
        condition = lambda function: function['name'] in function_name
        function = next(filter(condition,self._data['functions']),None)

        if function:

            loops = function['for_loops']

            condition = lambda loop: loop['nro'] is loop_nro
            first_loop = next(filter(condition,loops),None)

            if first_loop:
                begin = first_loop['begin']['relative']
                end = first_loop['end']['relative']
            
                return tuple((begin,end))

        return tuple()

    def get_loop_line(self,function_name,loop_nro,relative=True):
        condition = lambda function: function['name'] in function_name
        function = next(filter(condition,self._data['functions']),None)
        loop_line = None
        if function:
            function_loops = function['for_loops']
            condition = lambda loop: loop['nro'] is loop_nro
            loop = next(filter(condition,function_loops),None)

            # If the loop whit the give loop_nro is founded 
            # we return the line on which that loop begins
            # in the source code
            if loop:
                absolute_line = loop['begin']['absolute']
                relative_line = loop['begin']['relative']
                loop_line = relative_line if relative else absolute_line
            
        return loop_line

    def update_function_raw_code(self,function_name,new_raw,commit=True):
        condition = lambda function: function['name'] in function_name
        function = next(filter(condition,self._data['functions']),None)
        function['raw'] = new_raw

        # This functionality needs to be tested, when we read the code 
        # from a file its works, but when we read the code form text
        # the file do not exist, so this function will raise an error.
        # if commit:
        #     self.update_associated_file()

        return new_raw

    def update_associated_file(self):
        new_raw_data = self.raw
        file_path = self._data['file_path']
        with open(file_path,'w') as file:
            file.write(new_raw_data)
        
        if self._file_path:
            self._data = CCode.load_data_from_file(self._file_path)
        elif self._raw_code:
            self._data = CCode.load_data_from_text(self._raw_code)
        else:
            raise ValueError(
                """file_path or raw_code kwargs any of these 
                parameters must be configured"""
            )

