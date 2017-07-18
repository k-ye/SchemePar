from __future__ import print_function

from ast.scoped_env import ScopedEnv, ScopedEnvNode
from ast.ir_ast import *
from ast.x86_ast import *
import x86_const as x86c


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


class _LowLvPassBuilder(object):
    '''
    Base class of the low level language, including IR and X86 assembly.
    '''

    def __init__(self):
        self._var_dict = {}
        # this is to order the variable list
        self._var_name_list = []
        self._stmt_list = []

    def _CreateVar(self, var):
        raise NotImplementedError("_CreateVar")

    @property
    def var_list(self):
        result = [self._var_dict[name] for name in self._var_name_list]
        return result

    @property
    def stmt_list(self):
        return self._stmt_list

    def AddVar(self, var):
        assert not self.ContainsVar(var)
        var_node = self._CreateVar(var)
        self._var_dict[var] = var_node
        self._var_name_list.append(var)
        return var_node

    def GetVar(self, var):
        return self._var_dict[var]

    def ContainsVar(self, var):
        return var in self._var_dict

    def AddStmt(self, stmt):
        self._stmt_list.append(stmt)


''' Flatten pass
This pass flattens an Scheme AST to an equivalent IR AST

- Scheme version: R1
- IR version: C0
'''


class _FlattenBuilder(_LowLvPassBuilder):

    def __init__(self):
        super(_FlattenBuilder, self).__init__()
        self._next_tmp = 0

    def _CreateVar(self, var):
        return IrVarNode(var)

    def AllocateTmpVar(self):
        tmp_var = 'tmp_{}'.format(self._next_tmp)
        self._next_tmp += 1
        return self.AddVar(tmp_var)


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


'''Select-instruction pass

'''


class _SelectInstructionBuilder(_LowLvPassBuilder):

    def _CreateVar(self, var):
        return X86VarNode(var)

    def AddInstr(self, instr):
        assert isinstance(instr, X86InstrNode)
        super(_SelectInstructionBuilder, self).AddStmt(instr)

    @property
    def instr_list(self):
        return self.stmt_list


def _GetX86ArgNodeFromIr(ir_arg, builder):
    assert IsIrArgNode(ir_arg)
    if ir_arg.type == 'int':
        return X86IntNode(ir_arg.x)
    elif ir_arg.type == 'var':
        return builder.GetVar(ir_arg.var)
    # impossible to reach here
    assert False


def _SelectInstrForArg(ir_arg, x86_asn_var, builder):
    assert isinstance(x86_asn_var, X86VarNode), 'x86_asn_var type={}'.format(
        type(x86_asn_var))
    if ir_arg.type == 'var':
        # check that there is no side effect, meaning that assignment like
        # 'x <- x + 42' cannot exist at this point.
        assert ir_arg.var != x86_asn_var.var

    x86_arg = _GetX86ArgNodeFromIr(ir_arg, builder)
    x86_instr = X86InstrNode(x86c.MOVE, x86_arg, x86_asn_var)
    builder.AddInstr(x86_instr)


def _SelectInstrForApply(ir_apply, x86_asn_var, builder):
    assert isinstance(ir_apply, IrApplyNode) and ir_apply.type == 'apply'
    assert isinstance(x86_asn_var, X86VarNode)

    method = ir_apply.method
    ir_operands = ir_apply.arg_list

    if method == 'read':
        # runtime provides read_int function
        x86_instr = X86InstrNode(x86c.CALL, X86LabelNode('read_int'))
        builder.AddInstr(x86_instr)
        x86_instr = X86InstrNode(x86c.MOVE, X86RegNode(x86c.RAX), x86_asn_var)
        builder.AddInstr(x86_instr)
    elif method == '-':
        # TODO: Currently this means negation. Later on subtraction also needs
        # to be handled
        _SelectInstrForArg(ir_operands[0], x86_asn_var, builder)
        x86_instr = X86InstrNode(x86c.NEG, x86_asn_var)
        builder.AddInstr(x86_instr)
    elif method == '+':
        _SelectInstrForArg(ir_operands[0], x86_asn_var, builder)
        x86_instr = X86InstrNode(
            x86c.ADD, _GetX86ArgNodeFromIr(ir_operands[1], builder), x86_asn_var)
        builder.AddInstr(x86_instr)
    else:
        raise CompilingError('Unknown method={} in IrApplyNode'.format(method))


def _SelectInstrForAssign(ir_asn, builder):
    x86_asn_var = builder.AddVar(ir_asn.var.var)
    ir_expr = ir_asn.expr
    expr_type = ir_expr.type

    if IsIrArgNode(ir_expr):
        # 'int' or 'var'
        _SelectInstrForArg(ir_expr, x86_asn_var, builder)
    elif expr_type == 'apply':
        _SelectInstrForApply(ir_expr, x86_asn_var, builder)
    else:
        raise CompilingError(
            'Unknown type={} in IrAssignNode'.format(expr_type))


def _SelectInstrForStmt(ir_ast, builder):
    ir_type = ir_ast.type

    if ir_type == 'assign':
        _SelectInstrForAssign(ir_ast, builder)
    elif ir_type == 'return':
        x86_arg = _GetX86ArgNodeFromIr(ir_ast.arg, builder)
        x86_instr = X86InstrNode(x86c.RET, x86_arg)
        builder.AddInstr(x86_instr)
    else:
        raise CompilingError('Unknown type={} in IrStmtNode'.format(ir_type))


def SelectInstruction(ir_ast):
    assert ir_ast.type == 'program'
    builder = _SelectInstructionBuilder()
    for stmt in ir_ast.stmt_list:
        _SelectInstrForStmt(stmt, builder)

    x86_var_list = builder.var_list
    x86_instr_list = builder.instr_list
    assert len(x86_var_list) == len(ir_ast.var_list)
    return X86ProgramNode(-1, x86_var_list, x86_instr_list)


'''Assign-Home pass
This might be replaced by register allocation pass in the future
'''


def AssignHome(x86_ast):
    assert x86_ast.type == 'program'
    dword_sz = 8
    stack_pos = -dword_sz
    var_stack_map = {}
    instr_list = x86_ast.instr_list
    for i in xrange(len(instr_list)):
        instr = instr_list[i]
        operand_list = instr.operand_list
        for j in xrange(len(operand_list)):
            operand = operand_list[j]
            if operand.type == 'var':
                # replace Var with Deref
                var = operand.var
                if var not in var_stack_map:
                    var_stack_map[var] = stack_pos
                    stack_pos -= dword_sz
                operand = X86DerefNode(x86c.RBP, var_stack_map[var])
                operand_list[j] = operand
        instr.operand_list = operand_list
        instr_list[i] = instr
    x86_ast.instr_list = instr_list
    assert len(var_stack_map) == len(x86_ast.var_list)
    return x86_ast


'''Patch Instruction pass
Eliminate the cases where the two operands of a binary instruction
are all memory references, or deref nodes.
'''


def PatchInstruction(x86_ast):
    assert x86_ast.type == 'program'
    instr_list = x86_ast.instr_list
    # a instruction might be splitted into two, hence
    # we need a new list.
    new_instr_list = []
    for instr in x86_ast.instr_list:
        has_appended = False
        if instr.arity == 2:
            op1, op2 = instr.operand_list
            if op1.type == 'deref' and op2.type == 'deref':
                tmp_ref = X86RegNode(x86c.RAX)
                new_instr = X86InstrNode(x86c.MOVE, op1, tmp_ref)
                new_instr_list.append(new_instr)
                new_instr = X86InstrNode(instr.instr, tmp_ref, op2)
                new_instr_list.append(new_instr)
                has_appended = True
                instr = new_instr  # this is only needed for the check below
            dst_type = instr.operand_list[1].type
            assert dst_type in {'register', 'deref'}, 'dst type={} for instr={}'.format(
                dst_type, instr.instr)
        if not has_appended:
            new_instr_list.append(instr)
    x86_ast.instr_list = new_instr_list
    return x86_ast


'''Compile
Calls all the passes on the Scheme AST.
'''


def Compile(ast):
    ast = Uniquify(ast)
    ir_ast = Flatten(ast)
    x86_ast = SelectInstruction(ir_ast)
    x86_ast = AssignHome(x86_ast)
    x86_ast = PatchInstruction(x86_ast)

    return ir_ast
