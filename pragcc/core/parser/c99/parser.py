# -*- encoding: utf-8 -*-
"""Parser Module.
This module is an interface to the functionalities of pycpasrer,
a Python implementation of a parser for C99 source code. The 
pycparser implementation used here is a forked version from 
the original one.

.. _Google Python Style Guide:
   https://github.com/DonAurelio/pycparser
"""

import os
import pprint
from . import ast_visitor
from . import pycparser


FAKE_DEFINES = '#include <_fake_defines.h>'
"""str: Definitions headers.
In a given C source code there are words that have a special meaning
for the user and the compiler, for example *NULL*, *false*, *true*. 
Therefore the compiler needs to know that these words have a special
meanning and are not simply text. The *#include <_fake_defines.h>* header
defines those imporant definitions.

Example:
    #define NULL 0
    #define false 0
    #define true 1
"""

FAKE_TYPEDEFS = '#include <_fake_typedefs.h>'
"""str: Type definitions header.
To parse a given C source code, the compiler needs to know 
what is the type of each declared variable.
"""

FAKE_INCLUDES = [FAKE_DEFINES,FAKE_TYPEDEFS]
"""List[str]: .
The docstring may span multiple lines. The type may optionally be specified
on the first line, separated by a colon.
"""

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
"""int: Module level variable documented inline.
The docstring may span multiple lines. The type may optionally be specified
on the first line, separated by a colon.
"""

FAKE_INCLUDES_DIR = os.path.join(BASE_DIR,'utils','fake_libc_include')
"""int: Module level variable documented inline.
The docstring may span multiple lines. The type may optionally be specified
on the first line, separated by a colon.
"""

def fake_cfile(file_path):
    """Include fake include header with the basic C99 type definitions.
    To parce a C99 source code it is not neccesary to get the whole
    Libaries included. Then, to parse the code, we remove those headers
    an include fake headers with the neccesarry dafinitions to allow the 
    parser to parse de code.

    Args:
        file_path (str): Path to the C99 source code file which 
            include heraders needs to be faked.

    Returns:
        A path the facked file, it is to say a file with the suffix
            fake_<filename>.c.

    """
    dir_path = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    new_file_name = 'fake_' + file_name
    faked_file_path = os.path.join(dir_path,new_file_name)

    file_lines = []
    new_lines = []

    with open(file_path,'r') as file:
        file_lines = file.readlines()
        fake_includes = FAKE_INCLUDES[:]

        for line in file_lines:
            if fake_includes and '#include' in line:
                new_lines.append(fake_includes.pop(0) + '\n')

            elif '#include' in line:
                new_lines.append('//include removed' + '\n')
                
            else:
                new_lines.append(line)

        with open(faked_file_path,'w') as fakefile:
            fakefile.write(''.join(new_lines))

    return faked_file_path

def parse_cfile(file_path,preprocesor='cpp'):
    """Parse a C99 source code into a Syntrax Abstract Tree.
    
    Args:
        file_path (str): Path to the file to be parsed.
        preprocesor (str): C preprocessor.

    Returns:
        A Syntrax Abstract Tree.
    """
    faked_file_path = fake_cfile(file_path=file_path)

    ast = pycparser.parse_file(filename=faked_file_path,use_cpp=True,
        cpp_path=preprocesor, cpp_args=['-E', r'-I%s' % FAKE_INCLUDES_DIR])

    return ast


def get_data_from_cfile(file_path,compiler='gcc'):
    """Split a C99 source code in sections.

    Use pycparser to parse a C99 source code and dive it into three sections.
    **include**, **declaration**, **functions**. 

    Example:

        {
            'file_path': '/home/somebody/project/code.c',
            'include': '#include <stdlib.h>\n#include <sdtio.h>',      
            'declaration': '#define PI 3.141516',
            'functions': [
                { 
                    name: 'initilize', 
                    begin: 12, 
                    end: 15: 
                    raw:'void initialize(int i){\n //somebody\n}' 
                },
                ...
            ]
        }
        

        file_path, it is the path to the parsed file. Include, raw inclides 
        sections in the file. Declarations, raw declarations in the file.
        Functions, a list of dict, which contains information about each 
        function, the line on which it begin and end in the code, finally 
        the raw code. 

    Note:
        This function support files that can be parsed by pycparser,
        it is to say, C99 source code.

    Args:
        file_path (str): The path to the C99 source file to be parsed.
        compiler (str): The compiler to preprocess the c99 source code file.


    Returns:
        dict: a dict containing the sections of the C99 source code.
    """

    code_ast = parse_cfile(file_path)
    visitor = ast_visitor.FuncDefVisitor()
    funcdefs = visitor.funcdefs(code_ast)
    fundefs_data = visitor.funcdefs_data(funcdefs)
    
    code_data = {}

    with open(file_path,'r') as file:
        code_lines = file.readlines()
        includes_end_line = [ line + 1 for line, raw in enumerate(code_lines) \
         if '#include' in raw ][-1]
        fundef_init_line = fundefs_data[0]['begin'] - 1

        code_data['file_path'] = file_path
        code_data['include'] = ''.join(code_lines[:includes_end_line])
        code_data['declaration'] = ''.join(code_lines[includes_end_line:fundef_init_line])
        code_data['functions'] = fundefs_data

        for funcdef_data in code_data['functions']:
            begin = funcdef_data['begin'] - 1
            end = funcdef_data['end']
            funcdef_data['raw'] = ''.join(code_lines[begin:end])

    return code_data

# pragcc.core.parser.c99.pycparser.plyparser.ParseError