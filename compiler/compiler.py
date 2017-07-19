from __future__ import print_function

from ast.scoped_env import ScopedEnv, ScopedEnvNode
from ast.base import *
from ast.sch_ast import *
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
        return self._local_kv[key]

    def Add(self, key, value):
        # |value| is not used in this function
        count = self._global_count.get(key, 0)
        assert key not in self._local_kv
        self._local_kv[key] = '{}_{}'.format(key, count)
        self._global_count[key] = count + 1


class _UniquifyVisitor(SchAstVisitorBase):

    def __init__(self):
        super(_UniquifyVisitor, self).__init__()

    def _BeginVisit(self):

        class Factory(object):

            def __init__(self):
                self._global_count = {}

            def Build(self):
                return _UniquifyScopedEnvNode(self._global_count)

        self._env = ScopedEnv(Factory())

    def VisitProgram(self, node):
        prg_expr = GetSchProgram(node)
        SetSchProgram(node, self._Visit(prg_expr))
        return node

    def VisitApply(self, node):
        new_expr_list = []
        for app_expr in GetSchApplyExprList(node):
            new_expr_list.append(self._Visit(app_expr))
        SetSchApplyExprList(node, new_expr_list)
        return node

    def VisitLet(self, node):
        var_list1 = [(var, self._Visit(var_init))
                     for var, var_init in GetNodeVarList(node)]
        with self._env.Scope():
            var_list2 = []
            for var, var_init in var_list1:
                assert TypeOf(var) == VAR_NODE_T
                self._env.Add(GetNodeVar(var), None)
                var_list2.append((self._Visit(var), var_init))
            SetNodeVarList(node, var_list2)
            SetSchLetBody(node, self._Visit(GetSchLetBody(node)))
        return node

    def VisitInt(self, node):
        return node

    def VisitVar(self, node):
        old_var = GetNodeVar(node)
        SetNodeVar(node, self._env.Get(old_var))
        return node


def Uniquify(ast):
    '''
    Make variable names globally unique.
    |ast|: An SchNode. In production this should be an SchProgramNode. The
            correctness should already be verified in the analysis pass.
    '''
    visitor = _UniquifyVisitor()
    return visitor.Visit(ast)


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


class _SchToIrBuilder(_LowLvPassBuilder):

    def __init__(self):
        super(_SchToIrBuilder, self).__init__()
        self._next_tmp = 0

    def _CreateVar(self, var):
        return MakeIrVarNode(var)

    def AllocateTmpVar(self):
        tmp_var = 'tmp_{}'.format(self._next_tmp)
        self._next_tmp += 1
        return self.AddVar(tmp_var)


class _FlattenVisitor(SchAstVisitorBase):

    def __init__(self):
        super(_FlattenVisitor, self).__init__()

    def _BeginVisit(self):
        self._builder = _SchToIrBuilder()

    def VisitProgram(self, node):
        ir_expr = self._Visit(GetSchProgram(node))
        ret_var = ir_expr
        builder = self._builder
        if not IsIrArgNode(ir_expr):
            ret_var = builder.AllocateTmpVar()
            builder.AddStmt(MakeIrAssignNode(ret_var, ir_expr))
        builder.AddStmt(MakeIrReturnNode(ret_var))
        return MakeIrProgramNode(builder.var_list, builder.stmt_list)

    def VisitApply(self, node):
        new_arg_list = []
        for expr in GetSchApplyExprList(node):
            ir_expr = self._Visit(expr)
            if IsIrArgNode(ir_expr):
                new_arg_list.append(ir_expr)
            else:
                tmp_var = self._builder.AllocateTmpVar()
                self._builder.AddStmt(MakeIrAssignNode(tmp_var, ir_expr))
                new_arg_list.append(tmp_var)
        return MakeIrApplyNode(GetNodeMethod(node), new_arg_list)

    def VisitLet(self, node):
        ir_var_init = []
        for var, var_init in GetNodeVarList(node):
            ir_init = self._Visit(var_init)
            # Cannot add assign stmt yet, cache it in |ir_var_init|
            ir_var_init.append((GetNodeVar(var), ir_init))
        for var_name, ir_init in ir_var_init:
            ir_var = self._builder.AddVar(var_name)
            self._builder.AddStmt(MakeIrAssignNode(ir_var, ir_init))
        return self._Visit(GetSchLetBody(node))

    def VisitInt(self, node):
        return MakeIrIntNode(GetIntX(node))

    def VisitVar(self, node):
        return self._builder.GetVar(GetNodeVar(node))


def Flatten(sch_ast):
    '''
    Flatten the Scheme ast to IR ast. This should run after Uniquify
    |sch_ast|: An SchNode. In production this should be an SchProgramNode.
    Returns: An IrNode
    '''
    visitor = _FlattenVisitor()
    return visitor.Visit(sch_ast)
    # return _Flatten(sch_ast, _FlattenBuilder())


'''Select-instruction pass
'''


class _IrToX86Builder(_LowLvPassBuilder):

    def _CreateVar(self, var):
        return MakeX86VarNode(var)

    def AddInstr(self, instr):
        assert LangOf(instr) == X86_LANG and TypeOf(instr) == X86_INSTR_NODE_T
        super(_IrToX86Builder, self).AddStmt(instr)

    @property
    def instr_list(self):
        return self.stmt_list

    def GetX86Ast(self):
        return MakeX86ProgramNode(-1, self.var_list, self.instr_list)


class _SelectInstructionVisitor(IrAstVisitorBase):

    def __init__(self):
        super(_SelectInstructionVisitor, self).__init__()

    def _BeginVisit(self):
        self._builder = _IrToX86Builder()

    def _EndVisit(self, node, visit_result):
        return self._builder.GetX86Ast()

    def VisitProgram(self, node):
        for stmt in GetNodeStmtList(node):
            self._Visit(stmt)
        assert len(self._builder.var_list) == len(
            GetNodeVarList(node))

    def VisitAssign(self, node):
        var_name = GetNodeVar(GetNodeVar(node))
        x86_asn_var = self._builder.AddVar(var_name)
        ir_expr = GetIrAssignExpr(node)

        if IsIrArgNode(ir_expr):
            # non-standard visitor pattern call
            self._SelectForArg(ir_expr, x86_asn_var)
        elif TypeOf(ir_expr) == APPLY_NODE_T:
            # non-standard visitor pattern call
            self._SelectForApply(ir_expr, x86_asn_var)
        else:
            raise RuntimeError(
                'Unknown type={} in IrAssignNode'.format(expr_type))

    def VisitReturn(self, node):
        x86_arg = self._MakeX86ArgNode(GetIrReturnArg(node))
        # return value goes to %rax
        x86_instr = MakeX86InstrNode(
            x86c.MOVE, x86_arg, MakeX86RegNode(x86c.RAX))
        self._builder.AddInstr(x86_instr)
        self._builder.AddInstr(MakeX86InstrNode(x86c.RET))

    def VisitInt(self, node):
        raise RuntimeError("Shouldn't get called")

    def VisitVar(self, node):
        raise RuntimeError("Shouldn't get called")

    def _MakeX86ArgNode(self, node):
        assert IsIrArgNode(node)
        ndtype = TypeOf(node)
        if ndtype == INT_NODE_T:
            return MakeX86IntNode(GetIntX(node))
        elif ndtype == VAR_NODE_T:
            return self._builder.GetVar(GetNodeVar(node))
        raise RuntimeError('type={}'.format(ndtype))

    def _SelectForArg(self, node, x86_asn_var):
        assert LangOf(x86_asn_var) == X86_LANG
        assert TypeOf(x86_asn_var) == VAR_NODE_T
        if TypeOf(node) == VAR_NODE_T:
            # check that there is no side effect, meaning that assignment like
            # 'x <- x + 42' cannot exist at this point.
            assert GetNodeVar(node) != GetNodeVar(x86_asn_var)

        x86_arg = self._MakeX86ArgNode(node)
        x86_instr = MakeX86InstrNode(x86c.MOVE, x86_arg, x86_asn_var)
        self._builder.AddInstr(x86_instr)

    def VisitApply(self, node):
        raise RuntimeError("Shouldn't get called")

    def _SelectForApply(self, node, x86_asn_var):
        assert LangOf(x86_asn_var) == X86_LANG
        assert TypeOf(x86_asn_var) == VAR_NODE_T

        builder = self._builder
        method = GetNodeMethod(node)
        ir_operands = GetNodeArgList(node)

        if method == 'read':
            # runtime provides read_int function
            x86_instr = MakeX86InstrNode(
                x86c.CALL, MakeX86LabelNode('read_int'))
            builder.AddInstr(x86_instr)
            x86_instr = MakeX86InstrNode(
                x86c.MOVE, MakeX86RegNode(x86c.RAX), x86_asn_var)
            builder.AddInstr(x86_instr)
        elif method == '-':
            # TODO: Currently this means negation. Later on subtraction also needs
            # to be handled
            self._SelectForArg(ir_operands[0], x86_asn_var)
            x86_instr = MakeX86InstrNode(x86c.NEG, x86_asn_var)
            builder.AddInstr(x86_instr)
        elif method == '+':
            self._SelectForArg(ir_operands[0], x86_asn_var)
            x86_instr = MakeX86InstrNode(
                x86c.ADD, self._MakeX86ArgNode(ir_operands[1]), x86_asn_var)
            builder.AddInstr(x86_instr)
        else:
            raise RuntimeError(
                'Unknown method={} in IrApplyNode'.format(method))


def SelectInstruction(ir_ast, formatter=None):
    assert LangOf(ir_ast) == IR_LANG and TypeOf(ir_ast) == PROGRAM_NODE_T
    visitor = _SelectInstructionVisitor()
    return visitor.Visit(ir_ast)

'''Assign-Home pass
This might be replaced by register allocation pass in the future
'''


def AssignHome(x86_ast):
    assert LangOf(x86_ast) == X86_LANG and TypeOf(x86_ast) == PROGRAM_NODE_T
    dword_sz = 8
    stack_pos = -2 * dword_sz
    var_stack_map = {}
    instr_list = GetX86ProgramInstrList(x86_ast)
    for i, instr in enumerate(instr_list):
        operand_list = GetX86InstrOperandList(instr)
        for j, operand in enumerate(operand_list):
            if TypeOf(operand) == VAR_NODE_T:
                # replace Var with Deref
                var = GetNodeVar(operand)
                if var not in var_stack_map:
                    var_stack_map[var] = stack_pos
                    stack_pos -= dword_sz
                operand = MakeX86DerefNode(x86c.RBP, var_stack_map[var])
                operand_list[j] = operand
        SetX86InstrOperandList(instr, operand_list)
        instr_list[i] = instr
    SetX86ProgramInstrList(x86_ast, instr_list)
    # the stack size is computed at this time
    SetX86ProgramStackSize(x86_ast, -stack_pos)
    assert len(var_stack_map) == len(GetNodeVarList(x86_ast))
    return x86_ast


'''Patch Instruction pass
Eliminate the cases where the two operands of a binary instruction
are all memory references, or deref nodes.
'''


def PatchInstruction(x86_ast):
    assert LangOf(x86_ast) == X86_LANG and TypeOf(x86_ast) == PROGRAM_NODE_T
    instr_list = GetX86ProgramInstrList(x86_ast)
    # a instruction might be splitted into two, hence we need a new list.
    new_instr_list = []
    for instr in instr_list:
        has_appended = False
        if GetX86InstrArity(instr) == 2:
            op1, op2 = GetX86InstrOperandList(instr)
            if TypeOf(op1) == X86_DEREF_NODE_T and TypeOf(op2) == X86_DEREF_NODE_T:
                tmp_ref = MakeX86RegNode(x86c.RAX)
                new_instr = MakeX86InstrNode(x86c.MOVE, op1, tmp_ref)
                new_instr_list.append(new_instr)
                new_instr = MakeX86InstrNode(GetX86Instr(instr), tmp_ref, op2)
                new_instr_list.append(new_instr)
                has_appended = True
                instr = new_instr  # this is only needed for the check below
            dst_type = TypeOf(GetX86InstrOperandList(instr)[1])
            assert dst_type in {X86_REG_NODE_T, X86_DEREF_NODE_T}, \
                'dst type={} for instr={}'.format(dst_type, GetX86Instr(instr))
        if not has_appended:
            new_instr_list.append(instr)
    SetX86ProgramInstrList(x86_ast, new_instr_list)
    return x86_ast


'''Generate X86 pass
'''


def GenerateX86(x86_ast):
    return X86SourceCode(x86_ast, MacX86Formatter())


'''Compile
Calls all the passes on the Scheme AST.
'''


def Compile(sch_ast):
    sch_ast = Uniquify(sch_ast)
    ir_ast = Flatten(sch_ast)
    x86_ast = SelectInstruction(ir_ast)
    x86_ast = AssignHome(x86_ast)
    x86_ast = PatchInstruction(x86_ast)
    x86_ast = GenerateX86(x86_ast)

    return x86_ast
