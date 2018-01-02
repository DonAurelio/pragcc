# -*- encoding: utf-8 -*-
"""On this module are defined the interfaces to explore a pycparser AST."""

from . import pycparser


class FuncDefVisitor(pycparser.c_ast.NodeVisitor):
    """Interface to function definitions in Syntax Abtract Tree."""

    @staticmethod
    def funcdef_data(funcdef):
        """Extract data from a function definition object.

        It also extract information from the function object like 
        the begin and end line on the code. It also exract information
        of its loops if they are present.

        Args:
            fundef (pycparser.c_ast.FuncDef): A piece of the Syntrax Abstract
                Tree which contains the relevant information of a function 
                definition in a given C99 source code.

        Returns:
            dict: 
            {
                name: 'function name'
                begin: 'function begin line'
                end:    ''function end line
                for_loops:  'function loops data'
            } 
        """
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
        """Extract data from a list of function definition objects.

        Args:
            funcdefs (List[pycparser.c_ast.FuncDef]): A list of 
                pycparser.c_ast.FuncDef objects.

        Returns
            List[dict]: A list containing the dada of each function
                in the C99 source code.
        """
        funcdefs_data = []
        for funcdef in funcdefs:
            funcdefs_data.append(FuncDefVisitor.funcdef_data(funcdef))

        return funcdefs_data

    def __init__(self):
        self._funcdefs = []

    def visit_FuncDef(self,node):
        """Append in a list all function definitions founded in the AST.

        Args:
            node (pycparser.c_ast.FuncDef): A function definition object.
        """
        self._funcdefs.append(node)

    def funcdefs(self,node):
        """Returns a list of pycparser.c_ast.FuncDef objects.
        Visit all function defnitions reachable from the given
        node.

        Note:
            All nodes in the AST inherit from pycparser.c_ast.Node.

        Args: 
            node (pycparser.c_ast.Node): A node from which we want 
                to find function definitions.

        Returns:
            List[pycparser.c_ast.FuncDef]: A List of pycparser.c_ast.FuncDef
                objects.

        """
        self.visit(node)
        funcdefs = self._funcdefs[:]
        del self._funcdefs[:]

        return funcdefs


class ForVisitor(pycparser.c_ast.NodeVisitor):

    @staticmethod
    def _for_loops(node,loop_depth=0):
        """Return a list of pycparser.c_ast.For objects founded in the AST ."""
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
        """Return the data of a single loop inside a function.

        A typical loop consists of 4 parts. an initialization,
        a condition, the next value of an iterator (for example i)
        and the body of the loop called statement (stmt). Then the
        loob body can be presented in two ways, as depicted in the
        ``Example``.

        for (init; cond; next) stmt;

        Example:

            for (int i=0; i < N; ++i) function(); // single statement

            or 

            for (int i=0; i < N; ++i) { // Compound node init
                    
            } // compound node endding 

        Returns:
            dict, the relevant data of the given function loop.

        """
        data = {}
        depth = loop[0]
        loop_obj = loop[1]
        data['nro'] = nro
        data['depth'] = depth
        data['begin'] = {
            'relative': loop_obj.coord.line - funcdef.decl.coord.line,
            'absolute': loop_obj.coord.line
        }

        # If the loop body has the attribite end_coord, it mean that 
        # stmt is a compound object so the loop ends where the compound
        # node ends.
        if hasattr(loop_obj.stmt,'end_coord'):
            data['end'] = {
                'relative': loop_obj.stmt.end_coord.line - funcdef.decl.coord.line,
                'absolute': loop_obj.stmt.end_coord.line
            }

        # Otherwise the loop body has a single statement, that can be 
        # a function call or some operation. Thus the loop ends in the
        # same line where it starts.
        else:
            data['end'] = {
                'relative': loop_obj.coord.line - funcdef.decl.coord.line,
                'absolute': loop_obj.coord.line
            }

        return data

    @staticmethod
    def for_loops_data(funcdef):
        """Return data of loops for a given function.

        Args:
            funcdef (pycparser.c_ast.FuncDef): function from 
                which it is necessary to extract information 
                from the loops.
        Returns:
            List[dict], a list containing relevant information
                about loops in the given function.
        """
        # Getting For loops objects of the given 
        # function definition from the AST
        for_loops = ForVisitor._for_loops(funcdef)

        loops_data = []
        for i ,loop in enumerate(for_loops):
            loops_data.append(ForVisitor._for_loop_data(funcdef,loop,i))

        return loops_data
