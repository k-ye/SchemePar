from __future__ import print_function

from ast.scoped_env import ScopedEnv, ScopedEnvNode
from ast.base import *
from ast.sch_ast import *
from ast.ir_ast import *
from ast.x86_ast import *
import x86_const as x86c
from utils import *


class CompilingError(Exception):
    pass

''' Analyzation pass
There should be an analyzation pass first to verify the correctness
based on static information. i.e. duplicate variable definition in
the *SAME* scope, type matching. We leave that for later excercises.
'''


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

    def VisitIf(self, node):
        SetIfCond(node, self._Visit(GetIfCond(node)))
        SetIfThen(node, self._Visit(GetIfThen(node)))
        SetIfElse(node, self._Visit(GetIfElse(node)))
        return node

    def VisitInt(self, node):
        return node

    def VisitVar(self, node):
        old_var = GetNodeVar(node)
        SetNodeVar(node, self._env.Get(old_var))
        return node

    def VisitBool(self, node):
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
        assert not self.ContainsVar(var), var
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

    def GetStmt(self, index):
        return self._stmt_list[index]

    def ChangeStmt(self, index, stmt):
        self._stmt_list[index] = stmt


''' Flatten pass
This pass flattens an Scheme AST to an equivalent IR AST

- Scheme version: R1
- IR version: C0
'''


class _LowLvPassVarBuilder(object):
    '''
    Base class of the low level language, including IR and X86 assembly.
    '''

    def __init__(self):
        self._var_dict = {}
        # this is to order the variable list
        self._var_name_list = []

    @property
    def var_list(self):
        result = [self._var_dict[name] for name in self._var_name_list]
        return result

    def _CreateVar(self, var):
        # Override this
        raise NotImplementedError("_CreateVar")

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


class _SchToIrVarBuilder(_LowLvPassVarBuilder):

    def __init__(self):
        super(_SchToIrVarBuilder, self).__init__()
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
        self._builder = _SchToIrVarBuilder()

    def _EndVisit(self, node, visit_result):
        assert IsIrProgramNode(visit_result[0])
        return visit_result[0]

    def VisitProgram(self, node):
        ir_expr, stmt_list = self._Visit(GetSchProgram(node))
        assert IsIrArgNode(ir_expr)
        stmt_list.append(MakeIrReturnNode(ir_expr))
        return MakeIrProgramNode(self._builder.var_list, stmt_list), stmt_list

    def _VisitBinLogicalOp(self, node):
        method = GetNodeMethod(node)
        lhs, rhs = GetSchApplyExprList(node)
        translated = None
        if method == 'and':
            inner = MakeSchIfNode(rhs, MakeSchBoolNode(
                '#t'), MakeSchBoolNode('#f'))
            translated = MakeSchIfNode(lhs, inner, MakeSchBoolNode('#f'))
        elif method == 'or':
            inner = MakeSchIfNode(rhs, MakeSchBoolNode(
                '#t'), MakeSchBoolNode('#f'))
            translated = MakeSchIfNode(lhs, MakeSchBoolNode('#t'), inner)
        return self._Visit(translated)

    def VisitApply(self, node):
        method = GetNodeMethod(node)
        if IsBinLogicalOp(method):
            return self._VisitBinLogicalOp(node)

        ir_arg_list, stmt_list = [], []
        for expr in GetSchApplyExprList(node):
            ir_expr, expr_stmt_list = self._Visit(expr)
            assert IsIrArgNode(ir_expr)
            stmt_list += expr_stmt_list
            ir_arg_list.append(ir_expr)
        ir_apply = None
        if IsSchCmpOp(method):
            assert len(ir_arg_list) == 2
            ir_apply = MakeIrCmpNode(method, *ir_arg_list)
        else:
            ir_apply = MakeIrApplyNode(method, ir_arg_list)
        tmp_var = self._builder.AllocateTmpVar()
        stmt_list.append(MakeIrAssignNode(tmp_var, ir_apply))
        return tmp_var, stmt_list

    def VisitLet(self, node):
        ir_var_init = []
        stmt_list = []
        for var, var_init in GetNodeVarList(node):
            ir_init, init_stmt_list = self._Visit(var_init)
            assert IsIrArgNode(ir_init)
            # Cannot add assign stmt yet, cache it in |ir_var_init|
            ir_var_init.append((GetNodeVar(var), ir_init))
            stmt_list += init_stmt_list
        for var_name, ir_init in ir_var_init:
            ir_var = self._builder.AddVar(var_name)
            stmt_list.append(MakeIrAssignNode(ir_var, ir_init))
        ir_body, body_stmt_list = self._Visit(GetSchLetBody(node))
        assert IsIrArgNode(ir_body)
        stmt_list += body_stmt_list
        return ir_body, stmt_list

    def VisitIf(self, node):
        stmt_list = []
        # cond
        ir_cond, cond_stmt_list = self._Visit(GetIfCond(node))
        assert IsIrArgNode(ir_cond)
        stmt_list += cond_stmt_list
        # if_cond_tmp = self._builder.AllocateTmpVar()
        # stmt_list.append(MakeIrAssignNode(
        #     if_cond_tmp, MakeIrCmpNode('eq?', MakeIrBoolNode('#t'), ir_cond)))
        ir_cond = MakeIrCmpNode('eq?', MakeIrBoolNode('#t'), ir_cond)
        # then branch
        if_var = self._builder.AllocateTmpVar()
        ir_then, then_stmt_list = self._Visit(GetIfThen(node))
        then_stmt_list.append(MakeIrAssignNode(if_var, ir_then))
        then_stmt_list = tuple(then_stmt_list)
        # else branch
        ir_else, else_stmt_list = self._Visit(GetIfElse(node))
        else_stmt_list.append(MakeIrAssignNode(if_var, ir_else))
        else_stmt_list = tuple(else_stmt_list)

        ir_if = MakeIrIfNode(ir_cond, then_stmt_list, else_stmt_list)
        stmt_list.append(ir_if)
        return if_var, stmt_list

    def VisitInt(self, node):
        return MakeIrIntNode(GetIntX(node)), []

    def VisitVar(self, node):
        return self._builder.GetVar(GetNodeVar(node)), []

    def VisitBool(self, node):
        return MakeIrBoolNode(GetNodeBool(node)), []


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


class _IrToX86VarBuilder(_LowLvPassVarBuilder):

    def __init__(self):
        super(_IrToX86VarBuilder, self).__init__()

    def _CreateVar(self, var):
        return MakeX86VarNode(var)


class _SelectInstructionVisitor(IrAstVisitorBase):

    def __init__(self):
        super(_SelectInstructionVisitor, self).__init__()

    def _BeginVisit(self):
        self._builder = _IrToX86VarBuilder()
        self._ast = None

    def _EndVisit(self, node, visit_result):
        return self._ast
        # return self._builder.GetX86Ast()

    def _VisitStmtList(self, stmt_list):
        instr_list = []
        for stmt in stmt_list:
            instr_list += self._Visit(stmt)
        return instr_list

    def VisitProgram(self, node):
        instr_list = []
        # prologue, this should be added later for all function call
        instr_list.append(MakeX86CallCNode(X86_CALLC_PROLOGUE))
        instr_list += self._VisitStmtList(GetNodeStmtList(node))

        # call the runtime PrintPtr
        # movq    %rax, %rdi
        # callq   _PrintPtr
        last_instr = instr_list[-1]
        assert IsX86SiRetNode(last_instr)
        SetX86SiRetFromFunc(last_instr, False)  # return from program
        instr_list[-1] = last_instr

        # epilogue, this should be added later for all function call
        instr_list.append(MakeX86CallCNode(X86_CALLC_EPILOGUE))

        assert len(self._builder.var_list) == len(GetNodeVarList(node))
        self._ast = MakeX86ProgramNode(-1, self._builder.var_list, instr_list)
        return instr_list
        # # prologue, this should be added later for all function call
        # self._builder.AddInstr(MakeX86CallCNode(X86_CALLC_PROLOGUE))
        # self._VisitStmtList(GetNodeStmtList(node))

        # # call the runtime PrintPtr
        # # movq    %rax, %rdi
        # # callq   _PrintPtr
        # last_stmt = self._builder.GetStmt(-1)
        # assert IsX86SiRetNode(last_stmt)
        # SetX86SiRetFromFunc(last_stmt, False)  # return from program
        # self._builder.ChangeStmt(-1, last_stmt)

        # # epilogue, this should be added later for all function call
        # self._builder.AddInstr(MakeX86CallCNode(X86_CALLC_EPILOGUE))

        # assert len(self._builder.var_list) == len(
        #     GetNodeVarList(node))

    def VisitAssign(self, node):
        instr_list = []
        var_name, x86_asn_var = GetNodeVar(GetNodeVar(node)), None
        try:
            x86_asn_var = self._builder.GetVar(var_name)
        except KeyError:
            x86_asn_var = self._builder.AddVar(var_name)
        ir_expr = GetIrAssignExpr(node)

        if IsIrArgNode(ir_expr):
            # non-standard visitor pattern call
            instr_list = self._SelectForArg(ir_expr, x86_asn_var)
        elif IsIrApplyNode(ir_expr):
            # non-standard visitor pattern call
            instr_list = self._SelectForApply(ir_expr, x86_asn_var)
        elif IsIrCmpNode(ir_expr):
            instr_list = self.VisitCmp(ir_expr)
            cmp_op = GetIrCmpOp(ir_expr)
            byte_reg = MakeX86ByteRegNode(x86c.RAX)
            # needs special handling for cmp statement
            x86_set = MakeX86InstrNode(
                EncodeCcIntoInstr(x86c.SET, x86c.CmpOpToCc(cmp_op)), byte_reg)
            instr_list.append(x86_set)
            instr_list.append(MakeX86InstrNode(
                x86c.MOVEZB, byte_reg, x86_asn_var))
        else:
            raise RuntimeError(
                'Unknown type={} in IrAssignNode'.format(expr_type))
        return instr_list

    def VisitReturn(self, node):
        x86_arg = self._MakeX86ArgNode(GetIrReturnArg(node))
        # return value goes to %rax
        from_func = True
        x86_instr = MakeX86SiRetNode(from_func, x86_arg)
        return [x86_instr]
        # self._builder.AddInstr(x86_instr)
        # let the calling convention epilogue handles the actual 'ret'
        # instruction

    def VisitApply(self, node):
        raise RuntimeError("Shouldn't get called")

    def _SelectForApply(self, node, x86_asn_var):
        assert LangOf(x86_asn_var) == X86_LANG
        assert TypeOf(x86_asn_var) == VAR_NODE_T

        builder = self._builder
        method = GetNodeMethod(node)
        ir_operands = GetNodeArgList(node)
        instr_list = []

        if method in SchRtmFns():
            method = 'read_int' if method == 'read' else method
            # runtime provides read_int function
            x86_instr = MakeX86InstrNode(
                x86c.CALL, MakeX86LabelRefNode(method))
            instr_list.append(x86_instr)
            x86_instr = MakeX86InstrNode(
                x86c.MOVE, MakeX86RegNode(x86c.RAX), x86_asn_var)
            instr_list.append(x86_instr)
        elif method == '-':
            # TODO: Currently this means negation. Later on subtraction also needs
            # to be handled
            instr_list = self._SelectForArg(ir_operands[0], x86_asn_var)
            x86_instr = MakeX86InstrNode(x86c.NEG, x86_asn_var)
            instr_list.append(x86_instr)
        elif method == '+':
            instr_list = self._SelectForArg(ir_operands[0], x86_asn_var)
            x86_instr = MakeX86InstrNode(
                x86c.ADD, self._MakeX86ArgNode(ir_operands[1]), x86_asn_var)
            instr_list.append(x86_instr)
        elif method == 'not':
            instr_list = self._SelectForArg(ir_operands[0], x86_asn_var)
            x86_instr = MakeX86InstrNode(
                x86c.XOR, MakeX86IntNode(1), x86_asn_var)
            instr_list.append(x86_instr)
        else:
            raise RuntimeError(
                'Unknown method={} in IrApplyNode'.format(method))
        return instr_list

    def VisitIf(self, node):
        instr_list = self.VisitCmp(GetIfCond(node))
        # the fact that we don't include jump instruction here doesn't make
        # a difference to the live analysis
        then_instr_list = self._VisitStmtList(GetIfThen(node))
        else_instr_list = self._VisitStmtList(GetIfElse(node))
        x86_tmp_if = MakeX86TmpIfNode(then_instr_list, else_instr_list)
        instr_list.append(x86_tmp_if)
        return instr_list

    def VisitCmp(self, node):
        assert IsIrCmpNode(node)
        x86_lhs = self._MakeX86ArgNode(GetIrCmpLhs(node))
        x86_rhs = self._MakeX86ArgNode(GetIrCmpRhs(node))
        # |x86_lhs| and |x86_rhs| are flipped on purpose!
        return [MakeX86InstrNode(x86c.CMP, x86_rhs, x86_lhs)]

    def VisitInt(self, node):
        raise RuntimeError("Shouldn't get called")

    def VisitVar(self, node):
        raise RuntimeError("Shouldn't get called")

    def VisitBool(self, node):
        raise RuntimeError("Shouldn't get called")

    def _MakeX86ArgNode(self, node):
        assert IsIrArgNode(node)
        ndtype = TypeOf(node)
        if ndtype == INT_NODE_T:
            return MakeX86IntNode(GetIntX(node))
        elif ndtype == BOOL_NODE_T:
            bool_to_int = 1 if GetNodeBool(node) == '#t' else 0
            return MakeX86IntNode(bool_to_int)
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
        return [MakeX86InstrNode(x86c.MOVE, x86_arg, x86_asn_var)]


def SelectInstruction(ir_ast, formatter=None):
    assert LangOf(ir_ast) == IR_LANG and TypeOf(ir_ast) == PROGRAM_NODE_T
    visitor = _SelectInstructionVisitor()
    return visitor.Visit(ir_ast)


'''Uncover-Live pass
This pass detects the live after set for all the X86 instructions
'''


def _AddVarNamesToSet(var_names, operand_list):
    for op in filter(lambda o: TypeOf(o) == VAR_NODE_T, operand_list):
        var_names.add(GetNodeVar(op))


# The following helper functions only deal with *variables*.
# That is, although a CALL instruction will potentionally pollute
# all the caller-save registers (rax, rdx, ...), these registers
# will not be included in the result set.


def _ReadVariableSet(node):
    if IsX86CallCNode(node):
        return set()
    result, arg_list = set(), []
    if IsX86SiRetNode(node):
        arg_list.append(GetX86SiRetArg(node))
    else:
        operand_list = GetX86InstrOperandList(node)
        arity = GetX86InstrArity(node)
        arg_list.extend(operand_list[:(arity - 1)])
        # Instructions that read *destination*, hence MOVE is not here.
        # TODO: think about whether PUSH should also be here.
        instrs_read_dst = {x86c.ADD, x86c.NEG, x86c.SUB, x86c.XOR}
        if GetX86Instr(node) in instrs_read_dst:
            # must pass in a list
            arg_list.append(operand_list[-1])
    _AddVarNamesToSet(result, arg_list)
    return result


def _WrittenVariableSet(node):
    if IsX86SpecialInstrNode(node):
        return set()

    result = set()
    operand_list = GetX86InstrOperandList(node)
    instrs_write = {x86c.ADD, x86c.NEG, x86c.SUB,
                    x86c.XOR, x86c.MOVE, x86c.MOVEZB}
    instr = GetX86Instr(node)
    if instr in instrs_write:
        # instruction only writes to dst
        _AddVarNamesToSet(result, operand_list[-1:])
    return result


def _UncoverLive(instr_list, last_live_after=None, find_for_first=False):
    num_instr = len(instr_list)
    begin_index = 0 if find_for_first else 1
    live_afters = [set() for _ in xrange(num_instr)]
    live_afters[-1] = last_live_after or set()
    first_instr_lb = None
    for i in reversed(xrange(begin_index, num_instr)):
        instr = instr_list[i]
        # L_a(i)
        la_i = live_afters[i]
        # L_b(i) == L_a(i - 1)
        lb_i = None
        if IsX86TmpIfNode(instr):
            then_instr_list = GetX86TmpIfThen(instr)
            then_la_list, then_first_lb = _UncoverLive(
                then_instr_list, la_i, True)
            else_instr_list = GetX86TmpIfElse(instr)
            else_la_list, else_first_lb = _UncoverLive(
                else_instr_list, la_i, True)
            SetX86TmpIfThenLiveAfter(instr, then_la_list)
            SetX86TmpIfElseLiveAfter(instr, else_la_list)
            lb_i = then_first_lb | else_first_lb | la_i
        else:
            lb_i = (la_i - _WrittenVariableSet(instr)) | _ReadVariableSet(instr)
        if i == 0:
            assert find_for_first
            first_instr_lb = lb_i
        else:
            live_afters[i - 1] = lb_i
    return live_afters, first_instr_lb


def UncoverLive(x86_ast):
    assert IsX86ProgramNode(x86_ast)
    instr_list = GetX86ProgramInstrList(x86_ast)
    live_afters, _ = _UncoverLive(instr_list)
    SetX86ProgramLiveAfters(x86_ast, live_afters)
    return x86_ast


''' Build Interference Graph
'''


class _InferenceGraph(object):

    def __init__(self):
        self._ug = UGraph()
        self._var_to_node = {}
        self._var_saturation = {}

    def AddVar(self, node):
        assert IsX86VarNode(node)
        var_name = GetNodeVar(node)
        self._ug.AddVertex(var_name)
        self._var_to_node[var_name] = node
        self._var_saturation[var_name] = set()

    def AddInterference(self, u_name, v_name):
        self._ug.AddEdge(u_name, v_name)

    def Interfered(self, var_name):
        return {a for a in self._ug.AdjacentVertices(var_name)}

    def LocRepr(self, loc):
        assert IsX86RegNode(loc)
        return GetX86Reg(loc)

    def AddSaturation(self, var_name, loc):
        if IsX86DerefNode(loc):
            return
        self._var_saturation[var_name].add(self.LocRepr(loc))


def _ExtendInferenceGraphByInstrList(ig, instr_list, live_afters):
    # precondition: all the variables should be added to |ig|
    assert len(instr_list) == len(live_afters)
    for i, instr in enumerate(instr_list):
        if IsX86CallCNode(instr):
            continue
        la_i = live_afters[i]
        if IsX86SiRetNode(instr):
            for v_name in la_i:
                ig.AddSaturation(v_name, MakeX86RegNode(x86c.RAX))
        elif IsX86TmpIfNode(instr):
            then_instr_list = GetX86TmpIfThen(instr)
            then_la_list = GetX86TmpIfThenLiveAfter(instr)
            _ExtendInferenceGraphByInstrList(ig, then_instr_list, then_la_list)
            else_instr_list = GetX86TmpIfElse(instr)
            else_la_list = GetX86TmpIfElseLiveAfter(instr)
            _ExtendInferenceGraphByInstrList(ig, else_instr_list, else_la_list)
        else:
            method = GetX86Instr(instr)
            if method in {x86c.MOVE, x86c.MOVEZB}:
                src, dst = GetX86InstrOperandList(instr)
                dst_name = GetNodeVar(dst)
                not_interfered = {dst_name}
                if IsX86VarNode(src):
                    not_interfered.add(GetNodeVar(src))
                for v_name in la_i:
                    if v_name not in not_interfered:
                        ig.AddInterference(dst_name, v_name)
            elif method in {x86c.ADD, x86c.SUB, x86c.NEG, x86c.XOR}:
                dst = GetX86InstrOperandList(instr)[-1]
                dst_name = GetNodeVar(dst)
                for v_name in la_i:
                    if v_name != dst_name:
                        ig.AddInterference(dst_name, v_name)
            elif method == x86c.CALL:
                for v_name in la_i:
                    for cs_reg in x86c.CallerSaveRegs():
                        cs_reg = MakeX86RegNode(cs_reg)
                        ig.AddSaturation(v_name, cs_reg)


def _BuildInterferenceGraph(x86_ast):
    ig = _InferenceGraph()
    for var in GetNodeVarList(x86_ast):
        ig.AddVar(var)

    instr_list = GetX86ProgramInstrList(x86_ast)
    live_afters, _ = _UncoverLive(instr_list)
    _ExtendInferenceGraphByInstrList(ig, instr_list, live_afters)
    return ig


class _MoveRelatedGraph(object):

    def __init__(self):
        self._ug = UGraph()
        self._var_to_node = {}

    def AddVar(self, node):
        assert IsX86VarNode(node)
        var_name = GetNodeVar(node)
        self._ug.AddVertex(var_name)
        self._var_to_node[var_name] = node

    def AddMoveRelated(self, u_name, v_name):
        self._ug.AddEdge(u_name, v_name)

    def MoveRelated(self, var_name):
        return {m for m in self._ug.AdjacentVertices(var_name)}


def _BuildMoveRelatedGraph(x86_ast):
    mrg = _MoveRelatedGraph()
    for var in GetNodeVarList(x86_ast):
        mrg.AddVar(var)
    instr_list = GetX86ProgramInstrList(x86_ast)
    for instr in instr_list:
        if TypeOf(instr) == X86_INSTR_NODE_T and \
                GetX86Instr(instr) == x86c.MOVE:
            src, dst = GetX86InstrOperandList(instr)
            assert IsX86VarNode(dst)
            # it could be that |src| is an X86IntNode
            if IsX86VarNode(src):
                src_name, dst_name = GetNodeVar(src), GetNodeVar(dst)
                mrg.AddMoveRelated(src_name, dst_name)
    return mrg


def _AllocateRegisterOrStack(ig, mrg, use_mr):
    # a set the names of the variables not assigned a loc
    unassigned_var_names = set(ig._var_to_node.keys())
    # a mapping from var name to loc X86 node
    var_assigned_loc = {}

    free_regs = {r for r in x86c.FreeRegs()}
    stack_pos, dword_sz = 0, 8

    def TopUnassignedVar():
        curmax, chosen = -1, None
        for uv in unassigned_var_names:
            len_var_sat = len(ig._var_saturation[uv])
            if len_var_sat > curmax:
                curmax, chosen = len_var_sat, uv
        return uv

    def TryMoveRelatedRegister(uv, uv_sat, interfered):
        move_related = mrg.MoveRelated(uv) - interfered
        for mr in move_related:
            if mr in var_assigned_loc:
                maybe_loc = var_assigned_loc[mr]
                if IsX86RegNode(maybe_loc) and \
                        ig.LocRepr(maybe_loc) not in uv_sat:
                    return maybe_loc
        return None

    while len(unassigned_var_names):
        uv = TopUnassignedVar()
        uv_sat = ig._var_saturation[uv]
        interfered = ig.Interfered(uv)
        loc = TryMoveRelatedRegister(
            uv, uv_sat, interfered) if use_mr else None
        if loc is None:
            selectable_regs = list(free_regs - uv_sat)
            if len(selectable_regs):
                # select a register
                reg_name = selectable_regs[0]
                loc = MakeX86RegNode(reg_name)
            else:
                # select a stack position
                stack_pos -= dword_sz
                loc = MakeX86DerefNode(x86c.RBP, stack_pos)
        var_assigned_loc[uv] = loc
        for iv in interfered:
            ig.AddSaturation(iv, loc)
        unassigned_var_names.remove(uv)
    stack_sz = -stack_pos  # be verbose about what is returned.
    return var_assigned_loc, stack_sz


def _ReplaceX86SiRets(x86_ast):
    # Can do nothing about pro/epilogue now because we don't know the
    # stack size yet.
    new_instr_list = []
    for instr in GetX86ProgramInstrList(x86_ast):
        if IsX86SiRetNode(instr):
            from_func = GetX86SiRetFromFunc(instr)
            ret_arg = GetX86SiRetArg(instr)
            if from_func:
                instr = MakeX86InstrNode(
                    x86c.MOVE, ret_arg, MakeX86RegNode(x86c.RAX))
                new_instr_list.append(instr)
            else:
                instr = MakeX86InstrNode(
                    x86c.MOVE, ret_arg, MakeX86RegNode(x86c.RDI))
                new_instr_list.append(instr)
                instr = MakeX86InstrNode(
                    x86c.CALL, MakeX86LabelRefNode('print_ptr'))
                new_instr_list.append(instr)
                instr = MakeX86InstrNode(
                    x86c.MOVE, MakeX86IntNode(0), MakeX86RegNode(x86c.RAX))
                # instr = MakeX86InstrNode(
                #     'xor', MakeX86RegNode(x86c.RAX), MakeX86RegNode(x86c.RAX))
                new_instr_list.append(instr)

        else:
            new_instr_list.append(instr)
    SetX86ProgramInstrList(x86_ast, new_instr_list)
    return x86_ast


def _AssignAllocatedLocByInstrList(instr_list, var_assigned_loc_map):
    for i, instr in enumerate(instr_list):
        if IsX86CallCNode(instr):
            continue
        elif IsX86TmpIfNode(instr):
            then_instr_list = GetX86TmpIfThen(instr)
            then_instr_list = _AssignAllocatedLocByInstrList(
                then_instr_list, var_assigned_loc_map)
            SetX86TmpIfThen(instr, then_instr_list)
            else_instr_list = GetX86TmpIfElse(instr)
            else_instr_list = _AssignAllocatedLocByInstrList(
                else_instr_list, var_assigned_loc_map)
            SetX86TmpIfElse(instr, else_instr_list)
        else:
            operand_list = GetX86InstrOperandList(instr)
            for j, operand in enumerate(operand_list):
                if TypeOf(operand) == VAR_NODE_T:
                    # replace Var with Reg/Deref
                    var_name = GetNodeVar(operand)
                    loc = var_assigned_loc_map[var_name]
                    operand_list[j] = loc
            SetX86InstrOperandList(instr, operand_list)
            instr_list[i] = instr
    return instr_list


def _RemoveSameMov(instr_list):
    def AreSrcDstSame(src, dst):
        stype, dtype = TypeOf(src), TypeOf(dst)
        if stype != dtype:
            return False
        if stype not in {X86_REG_NODE_T, X86_DEREF_NODE_T}:
            return False

        sreg, dreg = GetX86Reg(src), GetX86Reg(dst)
        if sreg != dreg:
            return False
        if stype == X86_DEREF_NODE_T:
            return GetX86DerefOffset(src) == GetX86DerefOffset(dst)
        return True

    new_instr_list = []
    for i, instr in enumerate(instr_list):
        if IsX86InstrNode(instr) and GetX86Instr(instr) in {x86c.MOVE, x86c.MOVEZB}:
            src, dst = GetX86InstrOperandList(instr)
            if AreSrcDstSame(src, dst):
                continue
        elif IsX86TmpIfNode(instr):
            then_instr_list = _RemoveSameMov(GetX86TmpIfThen(instr))
            SetX86TmpIfThen(instr, then_instr_list)
            else_instr_list = _RemoveSameMov(GetX86TmpIfElse(instr))
            SetX86TmpIfElse(instr, else_instr_list)
        new_instr_list.append(instr)
    return new_instr_list


def AllocateRegisterOrStack(x86_ast, use_mr=True, rm_same_mov=True):
    assert IsX86ProgramNode(x86_ast)

    ig = _BuildInterferenceGraph(x86_ast)
    mrg = _BuildMoveRelatedGraph(x86_ast)
    # mrg = None
    x86_ast = _ReplaceX86SiRets(x86_ast)

    var_assigned_loc_map, stack_sz = _AllocateRegisterOrStack(ig, mrg, use_mr)
    assert len(var_assigned_loc_map) == len(GetNodeVarList(x86_ast))
    # for var in GetNodeVarList(x86_ast):
    #     var_name = GetNodeVar(var)
    #     print('{} assinged to {}'.format(
    #         var_name, var_assigned_loc_map[var_name]))

    instr_list = GetX86ProgramInstrList(x86_ast)
    instr_list = _AssignAllocatedLocByInstrList(
        instr_list, var_assigned_loc_map)

    if rm_same_mov:
        instr_list = _RemoveSameMov(instr_list)

    SetX86ProgramInstrList(x86_ast, instr_list)
    # the stack size is computed at this time
    SetX86ProgramStackSize(x86_ast, stack_sz)
    return x86_ast


'''Lower X86TmpIf pass
'''


def _LowerTmpIfByInstrList(instr_list, if_label_allocator):
    new_instr_list = []
    for instr in instr_list:
        if IsX86TmpIfNode(instr):
            t_label, f_label, sink_label = if_label_allocator.Allocate()
            new_instr_list.append(MakeX86InstrNode(EncodeCcIntoInstr(
                x86c.JMP_IF, x86c.CC_EQ), MakeX86LabelRefNode(t_label)))

            new_instr_list.append(MakeX86LabelDefNode(f_label))
            else_instr_list = _LowerTmpIfByInstrList(
                GetX86TmpIfElse(instr), if_label_allocator)
            new_instr_list += else_instr_list
            new_instr_list.append(MakeX86InstrNode(
                x86c.JMP, MakeX86LabelRefNode(sink_label)))

            new_instr_list.append(MakeX86LabelDefNode(t_label))
            then_instr_list = _LowerTmpIfByInstrList(
                GetX86TmpIfThen(instr), if_label_allocator)
            new_instr_list += then_instr_list
            new_instr_list.append(MakeX86LabelDefNode(sink_label))
        else:
            new_instr_list.append(instr)
    return new_instr_list

_INTERNAL_LABEL_HEADER = '@@'


class _IfLabelAllocator(object):

    def __init__(self):
        self._next_label = 0

    def Allocate(self):
        idx = self._next_label
        self._next_label += 1
        t = '{}IF_T_{}'.format(_INTERNAL_LABEL_HEADER, idx)
        f = '{}IF_F_{}'.format(_INTERNAL_LABEL_HEADER, idx)
        s = '{}IF_S_{}'.format(_INTERNAL_LABEL_HEADER, idx)
        return t, f, s


def LowerTmpIf(x86_ast):
    assert IsX86ProgramNode(x86_ast)
    if_label_allocator = _IfLabelAllocator()
    instr_list = GetX86ProgramInstrList(x86_ast)
    instr_list = _LowerTmpIfByInstrList(instr_list, if_label_allocator)
    SetX86ProgramInstrList(x86_ast, instr_list)
    return x86_ast


'''Patch Instruction pass
Eliminate the cases where the two operands of a binary instruction
are all memory references, or deref nodes.
'''


def PatchInstruction(x86_ast):
    assert LangOf(x86_ast) == X86_LANG and TypeOf(x86_ast) == PROGRAM_NODE_T
    instr_list = GetX86ProgramInstrList(x86_ast)
    stack_sz = GetX86ProgramStackSize(x86_ast)
    # a instruction might be splitted into two, hence we need a new list.
    new_instr_list = []
    for instr in instr_list:
        has_appended = False
        if IsX86CallCNode(instr):
            logue = GetX86CallCLogue(instr)
            if logue == X86_CALLC_PROLOGUE:
                # pushq   %rbp
                # movq    %rsp, %rbp
                # subq    $16, %rsp
                instr = MakeX86InstrNode(x86c.PUSH, MakeX86RegNode(x86c.RBP))
                new_instr_list.append(instr)
                instr = MakeX86InstrNode(x86c.MOVE, MakeX86RegNode(
                    x86c.RSP), MakeX86RegNode(x86c.RBP))
                new_instr_list.append(instr)
                if stack_sz > 0:
                    instr = MakeX86InstrNode(x86c.SUB, MakeX86IntNode(
                        stack_sz), MakeX86RegNode(x86c.RSP))
                    new_instr_list.append(instr)
                has_appended = True
            else:
                assert logue == X86_CALLC_EPILOGUE
                # addq    $16, %rsp
                # popq    %rbp
                # retq
                if stack_sz > 0:
                    instr = MakeX86InstrNode(x86c.ADD, MakeX86IntNode(
                        stack_sz), MakeX86RegNode(x86c.RSP))
                    new_instr_list.append(instr)
                instr = MakeX86InstrNode(x86c.POP, MakeX86RegNode(x86c.RBP))
                new_instr_list.append(instr)
                instr = MakeX86InstrNode(x86c.RET)
                new_instr_list.append(instr)
                has_appended = True
        elif IsX86InstrNode(instr) and GetX86InstrArity(instr) == 2:
            method = GetX86Instr(instr)
            op1, op2 = GetX86InstrOperandList(instr)
            if method == x86c.CMP and IsX86IntNode(op2):
                tmp_ref = MakeX86RegNode(x86c.RAX)
                new_instr = MakeX86InstrNode(x86c.MOVE, op2, tmp_ref)
                new_instr_list.append(new_instr)
                new_instr = MakeX86InstrNode(x86c.CMP, op1, tmp_ref)
                new_instr_list.append(new_instr)
                has_appended = True
                instr = new_instr  # this is only needed for the check below
            if TypeOf(op1) == X86_DEREF_NODE_T and \
                    TypeOf(op2) == X86_DEREF_NODE_T:
                tmp_ref = MakeX86RegNode(x86c.RAX)
                new_instr = MakeX86InstrNode(x86c.MOVE, op1, tmp_ref)
                new_instr_list.append(new_instr)
                new_instr = MakeX86InstrNode(method, tmp_ref, op2)
                new_instr_list.append(new_instr)
                has_appended = True
                instr = new_instr  # this is only needed for the check below
            dst_type = TypeOf(GetX86InstrOperandList(instr)[1])
            assert dst_type in {X86_REG_NODE_T, X86_DEREF_NODE_T,
                                X86_BYTE_REG_NODE_T}, \
                'dst type={} for instr={}'.format(dst_type, method)
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
    x86_ast = UncoverLive(x86_ast)
    x86_ast = AllocateRegisterOrStack(x86_ast)
    x86_ast = LowerTmpIf(x86_ast)
    x86_ast = PatchInstruction(x86_ast)
    x86_ast = GenerateX86(x86_ast)

    return x86_ast
