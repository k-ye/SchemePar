from collections import namedtuple

_NODE_STRUCTURE_INDEX = 0
_NODE_DATA_INDEX = 1

_NSTRUCT_TYPE_CHAIN_INDEX = 0
_NSTRUCT_LANG_INDEX = 1

AstNode = namedtuple('AstNode', ['structure', 'data'])
_NodeStructure = namedtuple('_NodeStructure', ['type_chain', 'lang'])


class TypeChain(object):

    def __init__(self, type, parent):
        assert parent is None or isinstance(parent, TypeChain)
        self._type = type
        self._parent = parent

    @property
    def type(self):
        return self._type

    @property
    def parent(self):
        return self._parent


def MakeAstNodeStructure(type, parent_tc, lang):
    '''
    type: a string of the symbol type of the node
    parent_tc: a TypeChain, if |type| has a parent type. Otherwise it is None
    lang: a string of the language of the node
    '''
    return _NodeStructure(TypeChain(type, parent_tc), lang)


def MakeAstNode(type, parent_tc, lang):
    '''
    type: a string of the symbol type of the node
    parent_tc: a TypeChain, if |type| has a parent type. Otherwise it is None
    lang: a string of the language of the node
    '''
    structure = MakeAstNodeStructure(type, parent_tc, lang)
    data = {}
    return AstNode(structure, data)


def MakeAstNodeBase(type, lang):
    return MakeAstNode(type, None, lang)


def StructureOf(node):
    return node[_NODE_STRUCTURE_INDEX]


def TypeChainOf(node):
    return StructureOf(node)[_NSTRUCT_TYPE_CHAIN_INDEX]


def TypeOf(node):
    return TypeChainOf(node).type


def ParentOf(node):
    ''' Returns the parent type chain.
    '''
    return TypeChainOf(node).parent


def LangOf(node):
    return StructureOf(node)[_NSTRUCT_LANG_INDEX]


def DataOf(node):
    return node[_NODE_DATA_INDEX]


def HasProperty(node, p):
    return p in DataOf(node)


def GetProperty(node, p):
    return DataOf(node)[p]


def GetProperties(node, ps):
    return {p: GetProperty(node, p) for p in ps}


def SetProperty(node, p, val):
    DataOf(node)[p] = val


def SetProperties(node, pvs):
    for p, v in pvs.iteritems():
        SetProperty(node, p, v)


''' Common Node Types
'''
NODE_T = 'node'
EXPR_NODE_T = 'expr'
INT_NODE_T = 'int'
VAR_NODE_T = 'var'
ARG_NODE_T = 'arg'
STMT_NODE_T = 'stmt'
APPLY_NODE_T = 'apply'
PROGRAM_NODE_T = 'program'

'''Common Node Property Names
'''
INT_P_X = 'x'
VAR_P_VAR = 'var'
P_METHOD = 'method'
P_ARG_LIST = 'arg_list'
P_VAR_LIST = 'var_list'
P_STMT_LIST = 'stmt_list'

''' Common Node Operations
'''


def GetIntX(node):
    assert TypeOf(node) == INT_NODE_T
    return GetProperty(node, INT_P_X)


def SetIntX(node, x):
    assert TypeOf(node) == INT_NODE_T
    SetProperty(node, INT_P_X, x)


def GetNodeVar(node):
    return GetProperty(node, VAR_NODE_T)


def SetNodeVar(node, var):
    SetProperty(node, VAR_P_VAR, var)


def GetNodeVarList(node):
    return GetProperty(node, P_VAR_LIST)


def SetNodeVarList(node, var_list):
    SetProperty(node, P_VAR_LIST, var_list)


def GetNodeArgList(node):
    return GetProperty(node, P_ARG_LIST)


def SetNodeArgList(node, arg_list):
    SetProperty(node, P_ARG_LIST, arg_list)


def GetNodeStmtList(node):
    return GetProperty(node, P_STMT_LIST)


def SetNodeStmtList(node, stmt_list):
    SetProperty(node, P_STMT_LIST, stmt_list)


def GetNodeMethod(node):
    return GetProperty(node, P_METHOD)


def SetNodeMethod(node, method):
    GetProperty(node, P_METHOD, method)
