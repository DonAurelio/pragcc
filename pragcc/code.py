# -*- encoding: utf-8 -*-

import os
import shutil
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
    def load_data(file_path):
        code_data = parser.get_data_from_cfile(file_path)
        return code_data

    def __init__(self,file_path,file_suffix='ccode_'):
        copied_file_path = CCode.copy_file(file_path,file_suffix)
        self._data = CCode.load_data(copied_file_path)

    @property
    def raw(self):
        raw_code = ''
        raw_code += self._data['include']
        raw_code += self._data['declaration']
        for function in self._data['functions']:
            raw_code += function['raw'] + '\n'

        return raw_code

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

                condition = lambda loop: loop['depth'] is first_loop['depth']
                same_depth_loops = list(filter(condition,loops))
                sorted_loops = sorted(same_depth_loops,key=lambda k: k['nro'])

                if len(sorted_loops) >= 2:
                    scope_begin = sorted_loops[0]['begin']['relative']
                    scope_end = sorted_loops[-1]['end']['relative']

                    # The scope of the loops in the function is determined 
                    return tuple((scope_begin,scope_end))
                
                elif len(sorted_loops) >= 1:
                    scope_begin = sorted_loops[0]['begin']['relative']
                    scope_end = sorted_loops[0]['end']['relative']
                
                    return tuple((scope_begin,scope_end))

        return tuple()

    def get_loop_line(self,function_name,loop_nro,relative=True):
        condition = lambda function: function['name'] in function_name
        function = next(filter(condition,self._data['functions']),None)
        loop_line = -1
        if function:
            function_loops = function['for_loops']
            condition = lambda loop: loop['nro'] is loop_nro
            loop = next(filter(condition,function_loops),None)
            absolute_line = loop['begin']['absolute']
            relative_line = loop['begin']['relative']
            loop_line = relative_line if relative else absolute_line
            
        return loop_line

    def update_function_raw_code(self,function_name,new_raw,commit=True):
        condition = lambda function: function['name'] in function_name
        function = next(filter(condition,self._data['functions']),None)
        function['raw'] = new_raw

        if commit:
            self.update_associated_file()

        return new_raw

    def update_associated_file(self):
        new_raw_data = self.raw
        file_path = self._data['file_path']
        with open(file_path,'w') as file:
            file.write(new_raw_data)
        
        self._data = CCode.load_data(file_path)