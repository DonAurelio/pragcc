# -*- encoding: utf-8 -*-

from parser.c99.pycparser import pycparser


class FuncDefVisitor(pycparser.c_ast.NodeVisitor):
    """
        Returns:
            A dict corresponing with sections (includes, declarations, function
            definitions) of C99 source file located in ``file_path``. For 
            example:

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
            }
    """

    @staticmethod
    def funcdef_data(funcdef):
        data = {}
        data['name'] = funcdef.decl.name
        data['begin'] = funcdef.decl.coord.line
        data['end'] = funcdef.body.end_coord.line

        for_visitor = ForVisitor()
        loops_data = for_visitor.for_loops_data(funcdef)

        data['for_loops'] = loops_data

        return data

    @staticmethod
    def funcdefs_data(funcdefs):
        funcdefs_data = []
        for funcdef in funcdefs:
            funcdefs_data.append(FuncDefVisitor.funcdef_data(funcdef))

        return funcdefs_data

    def __init__(self):
        self._funcdefs = []

    def visit_FuncDef(self,node):
        self._funcdefs.append(node)

    def funcdefs(self,node):
        self.visit(node)
        funcdefs = self._funcdefs[:]
        del self._funcdefs[:]

        return funcdefs


class ForVisitor(pycparser.c_ast.NodeVisitor):

    @staticmethod
    def _for_loops(node,loop_depth=0):
        loops = []
        new_loop_depth = loop_depth
        if isinstance(node,pycparser.c_ast.For):
            loops += [(loop_depth,node)]
            new_loop_depth = loop_depth + 1
        children_nodes = node.children()
        if children_nodes:
            for name, child_node in children_nodes:
                loops += ForVisitor._for_loops(child_node,new_loop_depth)
        return loops

    @staticmethod
    def _for_loop_data(funcdef,loop,nro):
        data = {}
        depth = loop[0]
        loop_obj = loop[1]

        data['nro'] = nro
        data['depth'] = depth
        data['begin'] = {
            'relative': loop_obj.coord.line - funcdef.decl.coord.line,
            'absolute': loop_obj.coord.line
        }
        data['end'] = {
            'relative': loop_obj.stmt.end_coord.line - funcdef.decl.coord.line,
            'absolute': loop_obj.stmt.end_coord.line
        }

        return data

    @staticmethod
    def for_loops_data(funcdef):
        for_loops = ForVisitor._for_loops(funcdef)
        loops_data = []
        for i ,loop in enumerate(for_loops):
            loops_data.append(ForVisitor._for_loop_data(funcdef,loop,i))

        return loops_data
