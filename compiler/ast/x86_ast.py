from base import *
from src_code_gen import *
from static_types import *


''' X86 specific
'''
X86_LANG = 'x86'
X86_REG_NODE_T = 'reg'
X86_BYTE_REG_NODE_T = 'byte_reg'
X86_DEREF_NODE_T = 'deref'
X86_INSTR_NODE_T = 'instr'
X86_LABEL_REF_NODE_T = 'label_ref'
X86_LABEL_DEF_NODE_T = 'label_def'
X86_CALLC_NODE_T = 'calling_convention'
X86_SI_RET_NODE_T = 'select_instr_ret'
X86_TMP_IF_NODE_T = 'tmp_if'


_X86_CALLC_P_LOGUE = 'logue_type'
X86_CALLC_PROLOGUE = 'prologue'
X86_CALLC_EPILOGUE = 'epilogue'

_X86_SI_RET_P_FROM_FUNC = 'from_func'
_X86_SI_RET_P_ARG = 'ret_arg'


_X86_P_FORMATTER = 'formatter'
_X86_PROGRAM_P_STACK_SZ = 'stack_sz'
_X86_PROGRAM_P_ROOTSTACK_SZ = 'rootstack_sz'
_X86_PROGRAM_P_INSTR_LIST = 'instr_list'
_X86_PROGRAM_P_LIVE = 'live_afters'
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


def IsX86Node(node):
    return LangOf(node) == X86_LANG


def MakeX86ProgramNode(var_list, instr_list):
    node = _MakeX86Node(PROGRAM_NODE_T, _NODE_TC)
    # stack_sz = stack_sz if stack_sz < 0 else RoundupStackSize(stack_sz)
    SetProperty(node, _X86_PROGRAM_P_STACK_SZ, -1)
    SetProperty(node, _X86_PROGRAM_P_ROOTSTACK_SZ, -1)
    SetProperty(node, P_VAR_LIST, var_list)
    SetProperty(node, _X86_PROGRAM_P_INSTR_LIST, instr_list)
    SetProperty(node, _X86_PROGRAM_P_LIVE, [])
    return node


def IsX86ProgramNode(node):
    return IsX86Node(node) and TypeOf(node) == PROGRAM_NODE_T


def _RoundupStackSize(stack_sz):
    return ((stack_sz + 15) / 16) * 16


def GetX86ProgramStackSize(node):
    assert IsX86ProgramNode(node)
    return GetProperty(node, _X86_PROGRAM_P_STACK_SZ)


def SetX86ProgramStackSize(node, stack_sz):
    assert IsX86ProgramNode(node)
    stack_sz = _RoundupStackSize(stack_sz)
    SetProperty(node, _X86_PROGRAM_P_STACK_SZ, stack_sz)


def GetX86ProgramRootstackSize(node):
    assert IsX86ProgramNode(node)
    return GetProperty(node, _X86_PROGRAM_P_ROOTSTACK_SZ)


def SetX86ProgramRootstackSize(node, rootstack_sz):
    assert IsX86ProgramNode(node)
    rootstack_sz = _RoundupStackSize(rootstack_sz)
    SetProperty(node, _X86_PROGRAM_P_ROOTSTACK_SZ, rootstack_sz)


def GetX86ProgramInstrList(node):
    assert IsX86ProgramNode(node)
    return GetProperty(node, _X86_PROGRAM_P_INSTR_LIST)


def SetX86ProgramInstrList(node, instr_list):
    assert IsX86ProgramNode(node)
    SetProperty(node, _X86_PROGRAM_P_INSTR_LIST, instr_list)


def GetX86ProgramLiveAfters(node):
    assert IsX86ProgramNode(node)
    return GetProperty(node, _X86_PROGRAM_P_LIVE)


def SetX86ProgramLiveAfters(node, live_afters):
    assert IsX86ProgramNode(node)
    SetProperty(node, _X86_PROGRAM_P_LIVE, live_afters)


def MakeX86InstrNode(instr, *operands):
    node = _MakeX86Node(X86_INSTR_NODE_T, _NODE_TC)
    SetProperty(node, _X86_INSTR_P_INSTR, instr)
    SetProperty(node, _X86_INSTR_P_OPERAND_LIST, [o for o in operands])
    return node


def IsX86InstrNode(node):
    return IsX86Node(node) and TypeOf(node) == X86_INSTR_NODE_T


def GetX86Instr(node):
    assert IsX86InstrNode(node), TypeOf(node)
    return GetProperty(node, _X86_INSTR_P_INSTR)


def SetX86Instr(node, instr):
    assert IsX86InstrNode(node), TypeOf(node)
    SetProperty(node, _X86_INSTR_P_INSTR, instr)


def GetX86InstrOperandList(node):
    assert IsX86InstrNode(node), TypeOf(node)
    return GetProperty(node, _X86_INSTR_P_OPERAND_LIST)


def SetX86InstrOperandList(node, operand_list):
    assert IsX86InstrNode(node), TypeOf(node)
    SetProperty(node, _X86_INSTR_P_OPERAND_LIST, operand_list)


def GetX86InstrArity(node):
    return len(GetX86InstrOperandList(node))


def MakeX86IntNode(x):
    node = _MakeX86ArgNode(INT_NODE_T)
    SetProperty(node, INT_P_X, x)
    return node


def IsX86IntNode(node):
    return IsX86Node(node) and TypeOf(node) == INT_NODE_T


def MakeX86RegNode(reg):
    node = _MakeX86ArgNode(X86_REG_NODE_T)
    SetProperty(node, _X86_P_REG, reg)
    return node


def IsX86RegNode(node):
    return IsX86Node(node) and TypeOf(node) in {X86_REG_NODE_T, X86_BYTE_REG_NODE_T}


def GetX86Reg(node):
    assert LangOf(node) == X86_LANG and TypeOf(
        node) in {X86_REG_NODE_T, X86_DEREF_NODE_T, X86_BYTE_REG_NODE_T}
    return GetProperty(node, _X86_P_REG)


def SetX86Reg(node, reg):
    assert LangOf(node) == X86_LANG and TypeOf(
        node) in {X86_REG_NODE_T, X86_DEREF_NODE_T, X86_BYTE_REG_NODE_T}
    SetProperty(node, _X86_P_REG, reg)


def MakeX86ByteRegNode(reg):
    node = _MakeX86ArgNode(X86_BYTE_REG_NODE_T)
    SetProperty(node, _X86_P_REG, reg)
    return node


def IsX86ByteRegNode(node):
    return IsX86Node(node) and TypeOf(node) == X86_BYTE_REG_NODE_T


def MakeX86DerefNode(reg, offset):
    node = _MakeX86ArgNode(X86_DEREF_NODE_T)
    SetProperty(node, _X86_P_REG, reg)
    SetProperty(node, _X86_DEREF_P_OFFSET, offset)
    return node


def IsX86DerefNode(node):
    return IsX86Node(node) and TypeOf(node) == X86_DEREF_NODE_T


def GetX86DerefOffset(node):
    assert LangOf(node) == X86_LANG and TypeOf(node) == X86_DEREF_NODE_T
    return GetProperty(node, _X86_DEREF_P_OFFSET)


def SetX86DerefOffset(node, offset):
    assert LangOf(node) == X86_LANG and TypeOf(node) == X86_DEREF_NODE_T
    SetProperty(node, _X86_DEREF_P_OFFSET, offset)


def MakeX86VarNode(var):
    node = _MakeX86ArgNode(VAR_NODE_T)
    SetProperty(node, NODE_P_VAR, var)
    return node


def IsX86VarNode(node):
    return IsX86Node(node) and TypeOf(node) == VAR_NODE_T


def MakeX86GlobalValueNode(name):
    node = _MakeX86ArgNode(INTERNAL_GLOBAL_VALUE_NODE_T)
    SetProperty(node, GLOBAL_VALUE_P_NAME, name)
    SetNodeStaticType(node, StaticTypes.INT)
    return node


def IsX86GlobalValueNode(node):
    return IsX86Node(node) and TypeOf(node) == INTERNAL_GLOBAL_VALUE_NODE_T


def MakeX86LabelDefNode(label):
    node = _MakeX86Node(X86_LABEL_DEF_NODE_T, _NODE_TC)
    SetProperty(node, _X86_LABEL_P_LABEL, label)
    return node


def IsX86LabelDefNode(node):
    return LangOf(node) == X86_LANG and TypeOf(node) == X86_LABEL_DEF_NODE_T


def MakeX86LabelRefNode(label):
    node = _MakeX86ArgNode(X86_LABEL_REF_NODE_T)
    SetProperty(node, _X86_LABEL_P_LABEL, label)
    return node


def GetX86Label(node):
    assert LangOf(node) == X86_LANG
    assert TypeOf(node) in {X86_LABEL_DEF_NODE_T, X86_LABEL_REF_NODE_T}
    return GetProperty(node, _X86_LABEL_P_LABEL)


def SetX86Label(node, label):
    assert LangOf(node) == X86_LANG
    assert TypeOf(node) in {X86_LABEL_DEF_NODE_T, X86_LABEL_REF_NODE_T}
    SetProperty(node, _X86_LABEL_P_LABEL, label)


_X86_TMP_IF_P_THEN = 'then'
_X86_TMP_IF_P_ELSE = 'else'
_X86_TMP_IF_P_THEN_LA = 'then_la'
_X86_TMP_IF_P_ELSE_LA = 'else_la'


def MakeX86TmpIfNode(then, els):
    node = _MakeX86Node(X86_TMP_IF_NODE_T, _NODE_TC)
    SetProperty(node, _X86_TMP_IF_P_THEN, then)
    SetProperty(node, _X86_TMP_IF_P_ELSE, els)
    SetProperty(node, _X86_TMP_IF_P_THEN_LA, None)
    SetProperty(node, _X86_TMP_IF_P_ELSE_LA, None)
    return node


def IsX86TmpIfNode(node):
    return LangOf(node) == X86_LANG and TypeOf(node) == X86_TMP_IF_NODE_T


def GetX86TmpIfThen(node):
    assert IsX86TmpIfNode(node)
    return GetProperty(node, _X86_TMP_IF_P_THEN)


def SetX86TmpIfThen(node, then):
    assert IsX86TmpIfNode(node)
    SetProperty(node, _X86_TMP_IF_P_THEN, then)


def GetX86TmpIfElse(node):
    assert IsX86TmpIfNode(node)
    return GetProperty(node, _X86_TMP_IF_P_ELSE)


def SetX86TmpIfElse(node, els):
    assert IsX86TmpIfNode(node)
    SetProperty(node, _X86_TMP_IF_P_ELSE, els)


def GetX86TmpIfThenLiveAfter(node):
    assert IsX86TmpIfNode(node)
    return GetProperty(node, _X86_TMP_IF_P_THEN_LA)


def SetX86TmpIfThenLiveAfter(node, then_la):
    assert IsX86TmpIfNode(node)
    SetProperty(node, _X86_TMP_IF_P_THEN_LA, then_la)


def GetX86TmpIfElseLiveAfter(node):
    assert IsX86TmpIfNode(node)
    return GetProperty(node, _X86_TMP_IF_P_ELSE_LA)


def SetX86TmpIfElseLiveAfter(node, else_la):
    assert IsX86TmpIfNode(node)
    SetProperty(node, _X86_TMP_IF_P_ELSE_LA, else_la)

# X86 Prologue/Epilogue node are placeholders generated
# during SelectionInstruction pass, because at that
# time we don't know the real stack size yet.


def MakeX86CallCNode(logue):
    assert logue in {X86_CALLC_PROLOGUE, X86_CALLC_EPILOGUE}
    node = _MakeX86Node(X86_CALLC_NODE_T, _NODE_TC)
    SetProperty(node, _X86_CALLC_P_LOGUE, logue)
    return node


def IsX86CallCNode(node):
    return IsX86Node(node) and TypeOf(node) == X86_CALLC_NODE_T


def GetX86CallCLogue(node):
    assert IsX86CallCNode(node)
    return GetProperty(node, _X86_CALLC_P_LOGUE)


def MakeX86SiRetNode(from_func, ret_arg):
    assert ParentOf(ret_arg).type == ARG_NODE_T
    node = _MakeX86Node(X86_SI_RET_NODE_T, _NODE_TC)
    SetProperty(node, _X86_SI_RET_P_FROM_FUNC, from_func)
    SetProperty(node, _X86_SI_RET_P_ARG, ret_arg)
    return node


def IsX86SiRetNode(node):
    return IsX86Node(node) and TypeOf(node) == X86_SI_RET_NODE_T


def GetX86SiRetFromFunc(node):
    assert IsX86SiRetNode(node)
    return GetProperty(node, _X86_SI_RET_P_FROM_FUNC)


def SetX86SiRetFromFunc(node, from_func):
    assert IsX86SiRetNode(node)
    SetProperty(node, _X86_SI_RET_P_FROM_FUNC, from_func)


def GetX86SiRetArg(node):
    assert IsX86SiRetNode(node)
    return GetProperty(node, _X86_SI_RET_P_ARG)


def SetX86SiRetArg(node, ret_arg):
    assert IsX86SiRetNode(node)
    assert ParentOf(ret_arg).type == ARG_NODE_T
    SetProperty(node, _X86_SI_RET_P_ARG, ret_arg)


def IsX86SpecialInstrNode(node):
    return IsX86CallCNode(node) or IsX86SiRetNode(node)


def EncodeCcIntoInstr(instr, cc):
    return '__encode_cc__{}::{}'.format(instr, cc)


def DecodeCcFromInstr(instr):
    hdr = '__encode_cc__'
    if not instr.startswith(hdr):
        raise ValueError("Instruction {} is not CC decodable".format(instr))
    instr = instr[len(hdr):]
    result = instr.split('::')
    if len(result) != 2:
        raise ValueError("Instruction {} is not CC decodable".format(instr))
    return result

''' X86 Ast Node Visitor
'''


class X86AstVisitorBase(object):

    def __init__(self):
        self._allow_tmp_if = False

    def Visit(self, node):
        self._BeginVisit()
        visit_result = self._Visit(node)
        return self._EndVisit(node, visit_result)

    def _BeginVisit(self):
        pass

    def _EndVisit(self, node, visit_result):
        return visit_result

    def _PreVisitNode(self, node):
        pass

    def _PostVisitNode(self, node, visit_result):
        pass

    def _Visit(self, node):
        assert LangOf(node) == X86_LANG, \
            'lang={}, type={}, node={}'.format(
                LangOf(node), TypeOf(node), str(node))
        ndtype = TypeOf(node)
        result = None
        self._PreVisitNode(node)
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
        elif ndtype == X86_BYTE_REG_NODE_T:
            result = self.VisitByteReg(node)
        elif ndtype == X86_DEREF_NODE_T:
            result = self.VisitDeref(node)
        elif ndtype == INTERNAL_GLOBAL_VALUE_NODE_T:
            result = self.VisitGlobalValue(node)
        elif ndtype == X86_LABEL_REF_NODE_T:
            result = self.VisitLabelRef(node)
        elif ndtype == X86_LABEL_DEF_NODE_T:
            result = self.VisitLabelDef(node)
        elif ndtype == X86_CALLC_NODE_T:
            result = self.VisitCallC(node)
        elif ndtype == X86_SI_RET_NODE_T:
            result = self.VisitSiRet(node)
        elif ndtype == X86_TMP_IF_NODE_T and self._allow_tmp_if:
            result = self.VisitTmpIf(node)
        else:
            raise RuntimeError("Unknown X86 node type={}".format(ndtype))
        self._PostVisitNode(node, result)
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

    def VisitByteReg(self, node):
        return node

    def VisitDeref(self, node):
        return node

    def VisitGlobalValue(self, node):
        return node

    def VisitLabelRef(self, node):
        return node

    def VisitLabelDef(self, node):
        return node

    def VisitCallC(self, node):
        return node

    def VisitSiRet(self, node):
        return node

    def VisitTmpIf(self, node):
        return node


# TODO: move this to x86_const.py
def MergeInstrWithCc(instr, cc):
    if instr == 'jmp_if':
        return 'j' + cc
    elif instr == 'set':
        return instr + cc
    raise ValueError('instr={} cannot have a condition code'.format(instr))


class _X86SourceCodeVisitor(X86AstVisitorBase):

    def __init__(self, formatter):
        super(_X86SourceCodeVisitor, self).__init__()
        self._formatter = formatter
        self._allow_tmp_if = True

    def _BeginVisit(self):
        self._builder = AstSourceCodeBuilder()

    def _FakeVisit(self, node, builder):
        assert builder is self._builder
        self._Visit(node)

    def VisitProgram(self, node):
        self._formatter.FormatProgram(
            node, self._builder, self._FakeVisit)

    def VisitInstr(self, node):
        instr = GetX86Instr(node)
        operand_list = GetX86InstrOperandList(node)
        self._formatter.AddInstr(
            instr, operand_list, self._builder, self._FakeVisit)

    def _VisitArg(self, node, val):
        self._formatter.AddArg(TypeOf(node), val, self._builder)

    def VisitInt(self, node):
        self._VisitArg(node, GetIntX(node))

    def VisitVar(self, node):
        self._VisitArg(node, GetNodeVar(node))

    def VisitReg(self, node):
        self._VisitArg(node, GetX86Reg(node))

    def VisitByteReg(self, node):
        self._VisitArg(node, GetX86Reg(node))

    def VisitDeref(self, node):
        val = (GetX86Reg(node), GetX86DerefOffset(node))
        self._VisitArg(node, val)

    def VisitGlobalValue(self, node):
        self._VisitArg(node, GetInternalGlobalValueNodeName(node))

    def VisitLabelRef(self, node):
        self._VisitArg(node, GetX86Label(node))

    def VisitLabelDef(self, node):
        self._formatter.AddLabelDef(GetX86Label(node), self._builder)

    def VisitCallC(self, node):
        logue = GetX86CallCLogue(node)
        self._builder.Append('( __{}__ )'.format(logue))

    def VisitSiRet(self, node):
        from_func = GetX86SiRetFromFunc(node)
        hdr = 'si_ret' if from_func else 'program_si_ret'
        self._builder.Append('( __{}__'.format(hdr))
        ret_arg = GetX86SiRetArg(node)
        self._Visit(ret_arg)
        self._builder.Append(')')

    def VisitTmpIf(self, node):
        builder = self._builder
        builder.Append('( __tmp_if__')
        with builder.Indent():
            builder.NewLine()
            builder.Append('# then')
            builder.NewLine()
            then_instr_list = GetX86TmpIfThen(node)
            self._formatter.FormatInstrList(
                then_instr_list, GetX86TmpIfThenLiveAfter(node), builder, self._FakeVisit)

            builder.NewLine()
            builder.Append('# else')
            builder.NewLine()
            else_instr_list = GetX86TmpIfElse(node)
            self._formatter.FormatInstrList(
                else_instr_list, GetX86TmpIfElseLiveAfter(node), builder, self._FakeVisit)
        builder.NewLine()
        builder.Append(')')

    def BuildSourceCode(self):
        return self._builder.Build()


def X86SourceCode(node, formatter):
    visitor = _X86SourceCodeVisitor(formatter)
    visitor.Visit(node)
    return visitor.BuildSourceCode()


class X86InternalFormatter(object):

    def __init__(self, include_live_afters=False):
        self.include_live_afters = include_live_afters

    def AddArg(self, t, arg, builder):
        if t == X86_DEREF_NODE_T:
            builder.Append('( {} {} {} )'.format(t, arg[0], arg[1]))
        elif t == INTERNAL_GLOBAL_VALUE_NODE_T:
            builder.Append('( global_value "{}" )'.format(arg))
        else:
            builder.Append('( {} {} )'.format(t, arg))

    def AddLabelDef(self, label, builder):
        builder.Append('label {}:'.format(label))

    def AddInstr(self, instr, operand_list, builder, src_code_gen):
        GenApplySourceCode(instr, operand_list, builder, src_code_gen)

    def FormatProgram(self, node, builder, src_code_gen):
        # variable definitions
        builder.NewLine()
        builder.Append('# variables')
        var_list = GetNodeVarList(node)
        for var in var_list:
            builder.NewLine()
            builder.Append('# ')
            src_code_gen(var, builder)
            builder.Append(', static_type: {}'.format(
                StaticTypes.Str(GetNodeStaticType(var))))

        # instructions + live afters
        builder.NewLine()
        builder.NewLine()

        builder.Append('# instructions')
        builder.NewLine()
        instr_list = GetX86ProgramInstrList(node)
        live_afters = GetX86ProgramLiveAfters(node)
        self.FormatInstrList(instr_list, live_afters, builder, src_code_gen)

    def FormatInstrList(self, instr_list, live_afters, builder, src_code_gen):
        builder.Append('(')

        with builder.Indent():
            len_live_afters = 0
            if live_afters is not None:
                len_live_afters = len(live_afters)

            for i, instr in enumerate(instr_list):
                builder.NewLine()
                src_code_gen(instr, builder)
                if live_afters is not None and self.include_live_afters and i < len_live_afters:
                    la = live_afters[i]
                    la_str = ', '.join(la)
                    builder.Append(' # live_after: ( { %s } )' % la_str)
        builder.NewLine()
        builder.Append(')')


class MacX86Formatter(object):

    def __init__(self):
        self.AddInstr = self._AddInstrDefault
        # self.AddInstr = self._AddInstrPretty
        self._allow_tmp_if = False

    def _Reg(self, reg):
        return '%' + reg

    def _LabelRef(self, label):
        # TODO: make this shared between x86_ast.py and compiler.py
        INTERNAL_LABEL_HEADER = '@@'
        if label.startswith(INTERNAL_LABEL_HEADER):
            return label[len(INTERNAL_LABEL_HEADER):]
        return '_' + label

    def _Reg64BitToLow8Bit(self, reg):
        # https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/x64-architecture
        reg_map = {'rax': 'al', }
        return reg_map[reg]

    def AddArg(self, t, var, builder):
        argstr = None
        if t == X86_DEREF_NODE_T:
            reg, offset = var
            argstr = '{1}({0})'.format(self._Reg(reg), offset)
        elif t == INT_NODE_T:
            argstr = '${}'.format(var)
        elif t == X86_REG_NODE_T:
            argstr = self._Reg(var)
        elif t == X86_BYTE_REG_NODE_T:
            argstr = self._Reg(self._Reg64BitToLow8Bit(var))
        elif t == INTERNAL_GLOBAL_VALUE_NODE_T:
            argstr = '{1}({0})'.format(self._Reg('rip'), self._LabelRef(var))
            # builder.Append('( global_value "{}" )'.format(arg))
        elif t == X86_LABEL_REF_NODE_T:
            argstr = self._LabelRef(var)
        else:
            raise RuntimeError('type={} var={}'.format(t, var))
        builder.Append(argstr, append_whitespace=False)

    def AddLabelDef(self, label, builder):
        builder.ClearIndent()
        builder.Append('{}:'.format(self._LabelRef(label)))

    def _Instr(self, instr):
        instrs_64bit = {'add', 'sub', 'neg', 'xor', 'cmp',
                        'mov', 'movzb', 'call', 'push', 'pop', 'ret', }

        if instr in instrs_64bit:
            return instr + 'q'
        return instr

    def _AddInstrDefault(self, instr, operand_list, builder, src_code_gen):
        try:
            instr, cc = DecodeCcFromInstr(instr)
            instr = MergeInstrWithCc(instr, cc)
        except ValueError:
            pass
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
                '',
                '.globl  {}'.format(self._LabelRef('main')),
                '.p2align    4, 0x90',
            ]
            for line in lines:
                builder.NewLine()
                builder.Append(line)
        builder.NewLine()
        self.AddLabelDef('main', builder)

        # instructions
        program_fmt = DefaultProgramFormatter(stmt_hdr='instructions')
        with builder.Indent(4):
            GenStmtsSourceCode(GetX86ProgramInstrList(
                node), builder, src_code_gen, program_fmt)

        # end
        builder.NewLine()
        builder.NewLine()
        builder.Append('.subsections_via_symbols')
