from base import *
from src_code_gen import *


''' X86 specific
'''
X86_LANG = 'x86'
X86_REG_NODE_T = 'reg'
X86_DEREF_NODE_T = 'deref'
X86_INSTR_NODE_T = 'instr'
X86_LABEL_NODE_T = 'label'
X86_PROLOGUE_NODE_T = 'prologue'
X86_EPILOGUE_NODE_T = 'epilogue'

_X86_P_FORMATTER = 'formatter'
_X86_PROGRAM_P_STACK_SZ = 'stack_sz'
_X86_PROGRAM_P_INSTR_LIST = 'instr_list'
_X86_INSTR_P_INSTR = 'instr'
_X86_INSTR_P_OPERAND_LIST = 'operand_list'
_X86_P_REG = 'reg'
_X86_DEREF_P_OFFSET = 'offset'
_X86_LABEL_P_LABEL = 'label'

_NODE_TC = TypeChain(NODE_T, None)
_ARG_TC = TypeChain(ARG_NODE_T, _NODE_TC)


def _MakeX86Node(type, parent_tc):
    return MakeAstNode(type, parent_tc, X86_LANG)


def _MakeX86ArgNode(type):
    return _MakeX86Node(type, _ARG_TC)


def MakeX86ProgramNode(stack_sz, var_list, instr_list):
    node = _MakeX86Node(PROGRAM_NODE_T, _NODE_TC)
    stack_sz = stack_sz if stack_sz < 0 else RoundupStackSize(stack_sz)
    SetProperty(node, _X86_PROGRAM_P_STACK_SZ, stack_sz)
    SetProperty(node, P_VAR_LIST, var_list)
    SetProperty(node, _X86_PROGRAM_P_INSTR_LIST, instr_list)
    return node


def GetX86ProgramStackSize(node):
    assert LangOf(node) == X86_LANG and TypeOf(node) == PROGRAM_NODE_T
    return GetProperty(node, _X86_PROGRAM_P_STACK_SZ)


def RoundupStackSize(stack_sz):
    return ((stack_sz + 15) / 16) * 16


def SetX86ProgramStackSize(node, stack_sz):
    assert LangOf(node) == X86_LANG and TypeOf(node) == PROGRAM_NODE_T
    stack_sz = RoundupStackSize(stack_sz)
    SetProperty(node, _X86_PROGRAM_P_STACK_SZ, stack_sz)


def GetX86ProgramInstrList(node):
    assert LangOf(node) == X86_LANG and TypeOf(node) == PROGRAM_NODE_T
    return GetProperty(node, _X86_PROGRAM_P_INSTR_LIST)


def SetX86ProgramInstrList(node, instr_list):
    assert LangOf(node) == X86_LANG and TypeOf(node) == PROGRAM_NODE_T
    SetProperty(node, _X86_PROGRAM_P_INSTR_LIST, instr_list)


def MakeX86InstrNode(instr, *operands):
    node = _MakeX86Node(X86_INSTR_NODE_T, _NODE_TC)
    SetProperty(node, _X86_INSTR_P_INSTR, instr)
    SetProperty(node, _X86_INSTR_P_OPERAND_LIST, [o for o in operands])
    return node


def GetX86Instr(node):
    assert LangOf(node) == X86_LANG and TypeOf(node) == X86_INSTR_NODE_T
    return GetProperty(node, _X86_INSTR_P_INSTR)


def SetX86Instr(node, instr):
    assert LangOf(node) == X86_LANG and TypeOf(node) == X86_INSTR_NODE_T
    SetProperty(node, _X86_INSTR_P_INSTR, instr)


def GetX86InstrOperandList(node):
    assert LangOf(node) == X86_LANG and TypeOf(node) == X86_INSTR_NODE_T
    return GetProperty(node, _X86_INSTR_P_OPERAND_LIST)


def SetX86InstrOperandList(node, operand_list):
    assert LangOf(node) == X86_LANG and TypeOf(node) == X86_INSTR_NODE_T
    SetProperty(node, _X86_INSTR_P_OPERAND_LIST, operand_list)


def GetX86InstrArity(node):
    return len(GetX86InstrOperandList(node))


def MakeX86IntNode(x):
    node = _MakeX86ArgNode(INT_NODE_T)
    SetProperty(node, INT_P_X, x)
    return node


def MakeX86RegNode(reg):
    node = _MakeX86ArgNode(X86_REG_NODE_T)
    SetProperty(node, _X86_P_REG, reg)
    return node


def GetX86Reg(node):
    assert LangOf(node) == X86_LANG and TypeOf(
        node) in {X86_REG_NODE_T, X86_DEREF_NODE_T}
    return GetProperty(node, _X86_P_REG)


def SetX86Reg(node, reg):
    assert LangOf(node) == X86_LANG and TypeOf(
        node) in {X86_REG_NODE_T, X86_DEREF_NODE_T}
    setProperty(node, _X86_P_REG, reg)


# X86 Prologue/Epilogue node are placeholders generated
# during SelectionInstruction pass, because at that
# time we don't know the real stack size yet.
def MakeX86PrologueNode():
    return _MakeX86Node(X86_PROLOGUE_NODE_T, _NODE_TC)


def MakeX86EpilogueNode():
    return _MakeX86Node(X86_EPILOGUE_NODE_T, _NODE_TC)


def IsX86CallingConventionNode(node):
    types = {X86_PROLOGUE_NODE_T, X86_EPILOGUE_NODE_T}
    return LangOf(node) == X86_LANG and TypeOf(node) in types


def MakeX86DerefNode(reg, offset):
    node = _MakeX86ArgNode(X86_DEREF_NODE_T)
    SetProperty(node, _X86_P_REG, reg)
    SetProperty(node, _X86_DEREF_P_OFFSET, offset)
    return node


def GetX86DerefOffset(node):
    assert LangOf(node) == X86_LANG and TypeOf(node) == X86_DEREF_NODE_T
    return GetProperty(node, _X86_DEREF_P_OFFSET)


def SetX86DerefOffset(node, offset):
    assert LangOf(node) == X86_LANG and TypeOf(node) == X86_DEREF_NODE_T
    SetProperty(node, _X86_DEREF_P_OFFSET, offset)


def MakeX86VarNode(var):
    node = _MakeX86ArgNode(VAR_NODE_T)
    SetProperty(node, VAR_P_VAR, var)
    return node


def MakeX86LabelNode(label):
    node = _MakeX86ArgNode(X86_LABEL_NODE_T)
    SetProperty(node, _X86_LABEL_P_LABEL, label)
    return node


def GetX86Label(node):
    assert LangOf(node) == X86_LANG and TypeOf(node) == X86_LABEL_NODE_T
    return GetProperty(node, _X86_LABEL_P_LABEL)


def SetX86Label(node, label):
    assert LangOf(node) == X86_LANG and TypeOf(node) == X86_LABEL_NODE_T
    SetProperty(node, _X86_LABEL_P_LABEL, label)


''' X86 Ast Node Visitor
'''


class X86AstVisitorBase(object):

    def Visit(self, node):
        self._BeginVisit()
        visit_result = self._Visit(node)
        return self._EndVisit(node, visit_result)

    def _BeginVisit(self):
        pass

    def _EndVisit(self, node, visit_result):
        return visit_result

    def _Visit(self, node):
        assert LangOf(node) == X86_LANG
        ndtype = TypeOf(node)
        result = None
        if ndtype == PROGRAM_NODE_T:
            result = self.VisitProgram(node)
        elif ndtype == X86_INSTR_NODE_T:
            result = self.VisitInstr(node)
        elif ndtype == INT_NODE_T:
            result = self.VisitInt(node)
        elif ndtype == VAR_NODE_T:
            result = self.VisitVar(node)
        elif ndtype == X86_REG_NODE_T:
            result = self.VisitReg(node)
        elif ndtype == X86_DEREF_NODE_T:
            result = self.VisitDeref(node)
        elif ndtype == X86_LABEL_NODE_T:
            result = self.VisitLabel(node)
        elif ndtype == X86_PROLOGUE_NODE_T:
            result = self.VisitPrologue(node)
        elif ndtype == X86_EPILOGUE_NODE_T:
            result = self.VisitEpilogue(node)
        else:
            raise RuntimeError("Unknown X86 node type={}".format(ndtype))
        return result

    def VisitProgram(self, node):
        return node

    def VisitInstr(self, node):
        return node

    def VisitInt(self, node):
        return node

    def VisitVar(self, node):
        return node

    def VisitReg(self, node):
        return node

    def VisitDeref(self, node):
        return node

    def VisitLabel(self, node):
        return node

    def VisitPrologue(self, node):
        return node

    def VisitEpilogue(self, node):
        return node


class _X86SourceCodeVisitor(X86AstVisitorBase):

    def __init__(self, formatter):
        super(_X86SourceCodeVisitor, self).__init__()
        self._formatter = formatter or _X86InternalFormatter()

    def _BeginVisit(self):
        self._builder = AstSourceCodeBuilder()

    def _FakeVisit(self, node, builder):
        assert builder is self._builder
        return self._Visit(node)

    def VisitProgram(self, node):
        self._formatter.FormatProgram(
            node, self._builder, self._FakeVisit)
        return node

    def VisitInstr(self, node):
        instr = GetX86Instr(node)
        operand_list = GetX86InstrOperandList(node)
        self._formatter.AddInstr(
            instr, operand_list, self._builder, self._FakeVisit)
        return node

    def _VisitArg(self, node, val):
        self._formatter.AddArg(TypeOf(node), val, self._builder)
        return node

    def VisitInt(self, node):
        return self._VisitArg(node, GetIntX(node))

    def VisitVar(self, node):
        return self._VisitArg(node, GetNodeVar(node))

    def VisitReg(self, node):
        return self._VisitArg(node, GetX86Reg(node))

    def VisitDeref(self, node):
        val = (GetX86Reg(node), GetX86DerefOffset(node))
        return self._VisitArg(node, val)

    def VisitLabel(self, node):
        return self._VisitArg(node, GetX86Label(node))

    def BuildSourceCode(self):
        return self._builder.Build()

    def VisitPrologue(self, node):
        self._builder.Append('( __prologue__ )')

    def VisitEpilogue(self, node):
        self._builder.Append('( __epilogue__ )')


def X86SourceCode(node, formatter=None):
    visitor = _X86SourceCodeVisitor(formatter)
    visitor.Visit(node)
    return visitor.BuildSourceCode()


class _X86InternalFormatter(object):

    def AddArg(self, t, var, builder):
        if t == X86_DEREF_NODE_T:
            builder.Append('( {} {} {} )'.format(t, var[0], var[1]))
        else:
            builder.Append('( {} {} )'.format(t, var))

    def AddInstr(self, instr, operand_list, builder, src_code_gen):
        GenApplySourceCode(instr, operand_list, builder, src_code_gen)

    def FormatProgram(self, node, builder, src_code_gen):
        program_fmt = DefaultProgramFormatter(stmt_hdr='instructions')
        var_list = GetNodeVarList(node)
        instr_list = GetX86ProgramInstrList(node)
        GenProgramSourceCode(
            var_list, instr_list, builder, src_code_gen, program_fmt)


class MacX86Formatter(object):

    def __init__(self):
        self.AddInstr = self._AddInstrDefault
        # self.AddInstr = self._AddInstrPretty

    def _Reg(self, reg):
        return '%' + reg

    def _Label(self, label):
        return '_' + label

    def AddArg(self, t, var, builder):
        argstr = None
        if t == X86_DEREF_NODE_T:
            reg, offset = var
            argstr = '{1}({0})'.format(self._Reg(reg), offset)
        elif t == INT_NODE_T:
            argstr = '${}'.format(var)
        elif t == X86_REG_NODE_T:
            argstr = self._Reg(var)
        elif t == X86_LABEL_NODE_T:
            argstr = self._Label(var)
        else:
            raise RuntimeError('type={} var={}'.format(t, var))
        builder.Append(argstr, append_whitespace=False)

    def _Instr(self, instr):
        return instr + 'q'

    def _AddInstrDefault(self, instr, operand_list, builder, src_code_gen):
        instr = '{0: <6}'.format(self._Instr(instr))
        builder.Append(instr)
        last_index = len(operand_list) - 1
        for i, op in enumerate(operand_list):
            src_code_gen(op, builder)
            if i < last_index:
                builder.Append(',')

    def FormatProgram(self, node, builder, src_code_gen):
        builder.Reset()
        # beginning
        with builder.Indent(4):
            lines = [
                '.section    __TEXT,__text,regular,pure_instructions',
                '.macosx_version_min 10, 12',
                '.globl  _main',
                '.p2align    4, 0x90',
            ]
            for line in lines:
                builder.NewLine()
                builder.Append(line)
        builder.NewLine()
        builder.Append('_main:')

        # instructions
        program_fmt = DefaultProgramFormatter(stmt_hdr='instructions')
        with builder.Indent(4):
            GenStmtsSourceCode(GetX86ProgramInstrList(
                node), builder, src_code_gen, program_fmt)

        # end
        builder.NewLine()
        builder.Append('.subsections_via_symbols')
