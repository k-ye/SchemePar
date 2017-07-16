from __future__ import print_function

from ast.scoped_env import ScopedEnv, ScopedEnvNode
from ast.ir_ast import *


class CompilingError(Exception):
    pass

''' Analyzation pass
There should be an analyzation pass first to verify the correctness
based on static information. i.e. duplicate variable definition in
the *SAME* scope, type matching. We leave that for later excercises.
'''


def Analyze(ast):
    '''
    ast: An SchNode.
    '''
    raise NotImplementedError("Analyze")


''' Uniquify pass
This pass uniquifies all the variable names in the Scheme AST. In another word, 
it does an alpha-reduction on the entire AST.

- Scheme version: R1
- IR version: C0
'''


class _UniquifyScopedEnvNode(ScopedEnvNode):

    def __init__(self, global_count):
        super(_UniquifyScopedEnvNode, self).__init__()
        self._global_count = global_count
        self._local_kv = {}

    def Contains(self, key):
        return key in self._local_kv

    def Get(self, key):
        result = self._local_kv.get(key, None)
        if result is None:
            raise KeyError('Cannot find key: {}'.format(key))
        return result

    def Add(self, key, value):
        # |value| is not used
        count = self._global_count.get(key, 0)
        self._local_kv[key] = '{}_{}'.format(key, count)
        self._global_count[key] = count + 1


def _Uniquify(ast, env):
    ast_type = ast.type
    if ast_type == 'program':
        ast.program = _Uniquify(ast.program, env)
    elif ast_type == 'int':
        pass
    elif ast_type == 'var':
        ast.var = env.Get(ast.var)
    elif ast_type == 'apply':
        new_arg_list = []
        for arg in ast.arg_list:
            new_arg_list.append(_Uniquify(arg, env))
        ast.set_arg_list(new_arg_list)
    elif ast_type == 'let':
        var_list1 = []
        for var, var_init in ast.var_list:
            var_list1.append((var, _Uniquify(var_init, env)))

        with env.Scope():
            var_list2 = []
            for var, var_init in var_list1:
                assert var.type == 'var'
                env.Add(var.var, None)
                var_list2.append((_Uniquify(var, env), var_init))
            ast.set_var_list(var_list2)
            ast.body = _Uniquify(ast.body, env)
    return ast


def Uniquify(ast):
    '''
    Make variable names globally unique.
    |ast|: An SchNode. In production this should be an SchProgramNode. The
            correctness should already be verified in the analysis pass.
    '''
    class Builder(object):

        def __init__(self):
            self._global_count = {}

        def Build(self):
            return _UniquifyScopedEnvNode(self._global_count)

    env = ScopedEnv(Builder())
    return _Uniquify(ast, env)


''' Flatten pass
This pass flattens an Scheme AST to an equivalent IR AST

- Scheme version: R1
- IR version: C0
'''


class _FlattenBuilder(object):

    def __init__(self):
        self._var_dict = {}
        self._next_tmp = 0
        self._stmt_list = []

    @property
    def var_list(self):
        return self._var_dict.values()

    @property
    def stmt_list(self):
        return self._stmt_list

    def AddVar(self, var):
        assert not self.ContainsVar(var)
        var_node = IrVarNode(var)
        self._var_dict[var] = var_node
        return var_node

    def AllocateTmpVar(self):
        tmp_var = 'tmp_{}'.format(self._next_tmp)
        self._next_tmp += 1
        return self.AddVar(tmp_var)

    def GetVar(self, var):
        return self._var_dict[var]

    def ContainsVar(self, var):
        return var in self._var_dict

    def AddStmt(self, stmt):
        self._stmt_list.append(stmt)


def _FlattenSchExpr(sch_ast, builder):
    '''
    It is the caller's responsibility to decide whether to create an assign stmt
    for the returned node.

    |sch_ast|: An SchExprNode or its subclass
    Returns: An IrExprNode
    '''
    ir_ast = None
    sch_type = sch_ast.type

    if sch_type == 'int':
        ir_ast = IrIntNode(sch_ast.x)
    elif sch_type == 'var':
        ir_ast = builder.GetVar(sch_ast.var)
    elif sch_type == 'apply':
        new_arg_list = []
        for arg in sch_ast.arg_list:
            ir_expr = _FlattenSchExpr(arg, builder)
            if IsIrArgNode(ir_expr):
                new_arg_list.append(ir_expr)
            else:
                tmp_var = builder.AllocateTmpVar()
                builder.AddStmt(IrAssignNode(tmp_var, ir_expr))
                new_arg_list.append(tmp_var)
        ir_ast = IrApplyNode(sch_ast.method, new_arg_list)
    elif sch_type == 'let':
        ir_var_init = []
        for var, var_init in sch_ast.var_list:
            ir_init = _FlattenSchExpr(var_init, builder)
            # Cannot add assign stmt yet, cache it in |ir_var_init|
            ir_var_init.append((var.var, ir_init))
        for var_name, ir_init in ir_var_init:
            ir_var = builder.AddVar(var_name)
            builder.AddStmt(IrAssignNode(ir_var, ir_init))
        ir_ast = _FlattenSchExpr(sch_ast.body, builder)
    else:
        raise CompilingError(
            'SchNode.type={} is not an "expr"'.format(sch_type))
    return ir_ast


def _Flatten(sch_ast, builder):
    '''
    Returns: An IrNode
    '''
    ir_ast = None
    if sch_ast.type == 'program':
        ir_expr = _FlattenSchExpr(sch_ast.program, builder)
        ret_var = ir_expr
        if not IsIrArgNode(ir_expr):
            ret_var = builder.AllocateTmpVar()
            builder.AddStmt(IrAssignNode(ret_var, ir_expr))
        builder.AddStmt(IrReturnNode(ret_var))
        ir_ast = IrProgramNode(builder.var_list, builder.stmt_list)
    else:
        ir_ast = _FlattenSchExpr(sch_ast, builder)
    return ir_ast


def Flatten(sch_ast):
    '''
    Flatten the Scheme ast to IR ast. This should run after Uniquify
    |sch_ast|: An SchNode. In production this should be an SchProgramNode.
    Returns: An IrNode
    '''
    return _Flatten(sch_ast, _FlattenBuilder())


'''Compile
Calls all the passes on the Scheme AST.
'''


def Compile(ast):
    ast = Uniquify(ast)
    ir_ast = Flatten(ast)
    return ir_ast
