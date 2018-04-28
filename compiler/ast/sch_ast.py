from base import *
from src_code_gen import *
from static_types import *

''' Scheme specific
'''
SCH_LANG = 'scheme'
SCH_LET_NODE_T = 'let'
SCH_FUNC_DEFINE_NODE_T = 'func_define'
SCH_LAMBDA_NODE_T = 'lambda'

_SCH_LET_P_LET_BODY = 'let_body'
_SCH_PROGRAM_P_FUNC_DEF_LIST = 'prg_func_def_list'
_SCH_PROGRAM_P_BODY = 'prg_body'
_SCH_APPLY_P_EXPR_LIST = 'expr_list'
_SCH_FUNC_P_NAME = 'func_name'
_SCH_FUNC_P_PARAMS = 'func_params'
_SCH_FUNC_P_BODY = 'func_body'

_NODE_TC = TypeChain(NODE_T, None)
_EXPR_TC = TypeChain(EXPR_NODE_T, _NODE_TC)


def _MakeSchNode(type, parent_tc):
  return MakeAstNode(type, parent_tc, SCH_LANG)


def _MakeSchExprNode(type):
  return _MakeSchNode(type, _EXPR_TC)


def MakeSchLambdaNode(params, body):
  assert isinstance(params, list)
  node = _MakeSchExprNode(SCH_LAMBDA_NODE_T)
  SetProperty(node, _SCH_FUNC_P_PARAMS, params)
  SetProperty(node, _SCH_FUNC_P_BODY, body)
  return node


def IsSchLambdaNode(node):
  return LangOf(node) == SCH_LANG and TypeOf(node) == SCH_LAMBDA_NODE_T


def GetSchLambdaParams(node):
  assert IsSchLambdaNode(node)
  return GetProperty(node, _SCH_FUNC_P_PARAMS)


def SetSchLambdaParams(node, params):
  assert IsSchLambdaNode(node)
  SetProperty(node, _SCH_FUNC_P_PARAMS, params)


def GetSchLambdaBody(node):
  assert IsSchLambdaNode(node)
  return GetProperty(node, _SCH_FUNC_P_BODY)


def SetSchLambdaBody(node, body):
  assert IsSchLambdaNode(node)
  SetProperty(node, _SCH_FUNC_P_BODY, body)


def MakeSchFuncDefineNode(name, params, body):
  assert IsSchVarNode(name)
  assert isinstance(params, list), params
  node = _MakeSchNode(SCH_FUNC_DEFINE_NODE_T, _NODE_TC)
  SetProperty(node, _SCH_FUNC_P_NAME, name)
  SetProperty(node, _SCH_FUNC_P_PARAMS, params)
  SetProperty(node, _SCH_FUNC_P_BODY, body)
  return node


def IsSchFuncDefineNode(node):
  return LangOf(node) == SCH_LANG and TypeOf(node) == SCH_FUNC_DEFINE_NODE_T


def GetSchFuncDefineName(node):
  assert IsSchFuncDefineNode(node)
  return GetProperty(node, _SCH_FUNC_P_NAME)


def SetSchFuncDefineName(node, name):
  assert IsSchFuncDefineNode(node)
  SetProperty(node, _SCH_FUNC_P_NAME, name)


def GetSchFuncDefineParams(node):
  assert IsSchFuncDefineNode(node)
  return GetProperty(node, _SCH_FUNC_P_PARAMS)


def SetSchFuncDefineParams(node, params):
  assert IsSchFuncDefineNode(node)
  SetProperty(node, _SCH_FUNC_P_PARAMS, params)


def GetSchFuncDefineBody(node):
  assert IsSchFuncDefineNode(node)
  return GetProperty(node, _SCH_FUNC_P_BODY)


def SetSchFuncDefineBody(node, body):
  assert IsSchFuncDefineNode(node)
  SetProperty(node, _SCH_FUNC_P_BODY, body)


def MakeSchIntNode(x):
  node = _MakeSchExprNode(INT_NODE_T)
  SetProperty(node, INT_P_X, x)
  return node


def IsSchIntNode(node):
  return LangOf(node) == SCH_LANG and TypeOf(node) == INT_NODE_T


def MakeSchVarNode(var):
  node = _MakeSchExprNode(VAR_NODE_T)
  SetProperty(node, NODE_P_VAR, var)
  return node


def IsSchVarNode(node):
  return LangOf(node) == SCH_LANG and TypeOf(node) == VAR_NODE_T


def MakeSchBoolNode(b):
  node = _MakeSchExprNode(BOOL_NODE_T)
  SetProperty(node, NODE_P_BOOL, b)
  return node


def MakeSchVoidNode():
  node = _MakeSchExprNode(VOID_NODE_T)
  return node


def IsBinLogicalOp(op):
  return op in {'and', 'or'}


def MakeSchApplyNode(method, expr_list):
  node = _MakeSchExprNode(APPLY_NODE_T)
  SetProperties(node, {P_METHOD: method, _SCH_APPLY_P_EXPR_LIST: expr_list})
  return node


def GetSchApplyExprList(node):
  assert LangOf(node) == SCH_LANG and TypeOf(node) == APPLY_NODE_T
  return GetProperty(node, _SCH_APPLY_P_EXPR_LIST)


def SetSchApplyExprList(node, expr_list):
  assert LangOf(node) == SCH_LANG and TypeOf(node) == APPLY_NODE_T
  SetProperty(node, _SCH_APPLY_P_EXPR_LIST, expr_list)


def IsSchArithop(method):
  return method in {'+', '-'}


def IsSchCmpOp(method):
  return method in {'eq?', '<', '<=', '>', '>='}


def IsSchLogicalOp(method):
  return method in {'and', 'not', 'or'}


def IsSchRtmFn(method):
  # check for builtin runtime function
  return method in {'read', 'read_int', 'read_bool'}


def MakeSchLetNode(var_list, let_body):
  node = _MakeSchExprNode(SCH_LET_NODE_T)
  SetProperty(node, P_VAR_LIST, var_list)
  SetProperty(node, _SCH_LET_P_LET_BODY, let_body)
  return node


def GetSchLetBody(node):
  assert LangOf(node) == SCH_LANG and TypeOf(node) == SCH_LET_NODE_T
  return GetProperty(node, _SCH_LET_P_LET_BODY)


def SetSchLetBody(node, let_body):
  assert LangOf(node) == SCH_LANG and TypeOf(node) == SCH_LET_NODE_T
  SetProperty(node, _SCH_LET_P_LET_BODY, let_body)


def MakeSchProgramNode(func_def_list, body):
  assert isinstance(func_def_list, list)
  assert LangOf(body) == SCH_LANG and \
      ParentOf(body).type == EXPR_NODE_T, ParentOf(body).type
  node = _MakeSchNode(PROGRAM_NODE_T, _NODE_TC)
  SetProperty(node, _SCH_PROGRAM_P_FUNC_DEF_LIST, func_def_list)
  SetProperty(node, _SCH_PROGRAM_P_BODY, body)
  return node


def IsSchProgramNode(node):
  return LangOf(node) == SCH_LANG and TypeOf(node) == PROGRAM_NODE_T


def GetSchProgramFuncDefList(node):
  assert IsSchProgramNode(node)
  return GetProperty(node, _SCH_PROGRAM_P_FUNC_DEF_LIST)


def SetSchProgramFuncDefList(node, func_def_list):
  assert IsSchProgramNode(node)
  SetProperty(node, _SCH_PROGRAM_P_FUNC_DEF_LIST, func_def_list)


def GetSchProgram(node):
  # TODO(k-ye): Renae to GetSchProgramBody
  assert IsSchProgramNode(node)
  return GetProperty(node, _SCH_PROGRAM_P_BODY)


def SetSchProgram(node, body):
  # TODO(k-ye): Renae to SetSchProgramBody
  assert IsSchProgramNode(node)
  assert LangOf(body) == SCH_LANG and \
      ParentOf(body).type == EXPR_NODE_T
  SetProperty(node, _SCH_PROGRAM_P_BODY, body)


def MakeSchIfNode(cond, then, els):
  node = _MakeSchExprNode(IF_NODE_T)
  SetProperty(node, IF_P_COND, cond)
  SetProperty(node, IF_P_THEN, then)
  SetProperty(node, IF_P_ELSE, els)
  return node


def IsSchIfNode(node):
  return LangOf(node) == SCH_LANG and TypeOf(node) == IF_NODE_T


def MakeSchVectorInitNode(arg_list):
  node = _MakeSchExprNode(VECTOR_INIT_NODE_T)
  SetProperty(node, P_ARG_LIST, arg_list)
  return node


def IsSchVectorInitNode(node):
  return LangOf(node) == SCH_LANG and TypeOf(node) == VECTOR_INIT_NODE_T


def GetSchVectorInitNodeLen(node):
  assert IsSchVectorInitNode(node)
  return len(GetNodeArgList(node))


def GetSchVectorInitNodeBytes(node):
  assert IsSchVectorInitNode(node)
  return (len(GetNodeArgList(node)) + 1) * 8


def MakeSchVectorRefNode(vec, idx):
  assert isinstance(idx, int)
  node = _MakeSchExprNode(VECTOR_REF_NODE_T)
  SetProperty(node, VECTOR_P_VEC, vec)
  SetProperty(node, VECTOR_P_INDEX, idx)
  return node


def IsSchVectorRefNode(node):
  return LangOf(node) == SCH_LANG and TypeOf(node) == VECTOR_REF_NODE_T


def MakeSchVectorSetNode(vec, idx, val):
  assert isinstance(idx, int)
  node = _MakeSchExprNode(VECTOR_SET_NODE_T)
  SetProperty(node, VECTOR_P_VEC, vec)
  SetProperty(node, VECTOR_P_INDEX, idx)
  SetProperty(node, VECTOR_SET_P_VAL, val)
  return node


def IsSchVectorSetNode(node):
  return LangOf(node) == SCH_LANG and TypeOf(node) == VECTOR_SET_NODE_T


def MakeSchInternalCollectNode(bytes):
  assert isinstance(bytes, int)
  node = _MakeSchExprNode(INTERNAL_COLLECT_NODE_T)
  SetProperty(node, COLLECT_P_BYTES, bytes)
  SetNodeStaticType(node, StaticTypes.VOID)
  return node


def IsSchInternalCollectNode(node):
  return LangOf(node) == SCH_LANG and TypeOf(node) == INTERNAL_COLLECT_NODE_T


def MakeSchInternalAllocateNode(len, static_type):
  assert isinstance(len, int)
  node = _MakeSchExprNode(INTERNAL_ALLOCATE_NODE_T)
  SetProperty(node, ALLOCATE_P_LEN, len)
  SetNodeStaticType(node, static_type)
  return node


def IsSchInternalAllocateNode(node):
  return LangOf(node) == SCH_LANG and TypeOf(node) == INTERNAL_ALLOCATE_NODE_T


def MakeSchInternalGlobalValueNode(name):
  node = _MakeSchExprNode(INTERNAL_GLOBAL_VALUE_NODE_T)
  SetProperty(node, GLOBAL_VALUE_P_NAME, name)
  SetNodeStaticType(node, StaticTypes.INT)
  return node


def IsSchInternalGlobalValueNode(node):
  return LangOf(node) == SCH_LANG and TypeOf(
      node) == INTERNAL_GLOBAL_VALUE_NODE_T


def SchRtmFns():
  return ['read', 'read_int', 'read_bool', ]


class SchEvalTypes(object):
  _rtm_types = {
      'read': StaticTypes.INT,
      'read_int': StaticTypes.INT,
      'read_bool': StaticTypes.BOOL,
  }

  @staticmethod
  def RtmFnType(method):
    return SchEvalTypes._rtm_types[method]


_SCH_CMP_OPS = {'eq?', '<', '<=', '>', '>='}


def IsSchCmpOp(op):
  return op in _SCH_CMP_OPS

''' Scheme Ast Node Visitor
'''


class SchAstVisitorBase(object):

  def Visit(self, node):
    '''Do NOT override
    '''
    self._BeginVisit()
    visit_result = self._Visit(node)
    return self._EndVisit(node, visit_result)

  def _BeginVisit(self):
    '''Optional to override
    '''
    pass

  def _EndVisit(self, node, visit_result):
    '''Optional to override
    '''
    return visit_result

  def _PreVisitNode(self, node):
    '''Optional to override
    '''
    pass

  def _PostVisitNode(self, node, visit_result):
    '''Optional to override
    '''
    pass

  def _Visit(self, node):
    '''Do NOT override
    '''
    assert LangOf(node) == SCH_LANG, LangOf(node)
    ndtype = TypeOf(node)
    result = None
    self._PreVisitNode(node)
    if ndtype == PROGRAM_NODE_T:
      result = self.VisitProgram(node)
    elif ndtype == APPLY_NODE_T:
      result = self.VisitApply(node)
    elif ndtype == SCH_LET_NODE_T:
      result = self.VisitLet(node)
    elif ndtype == IF_NODE_T:
      result = self.VisitIf(node)
    elif ndtype == VECTOR_INIT_NODE_T:
      result = self.VisitVectorInit(node)
    elif ndtype == VECTOR_REF_NODE_T:
      result = self.VisitVectorRef(node)
    elif ndtype == VECTOR_SET_NODE_T:
      result = self.VisitVectorSet(node)
    elif ndtype == INT_NODE_T:
      result = self.VisitInt(node)
    elif ndtype == VAR_NODE_T:
      result = self.VisitVar(node)
    elif ndtype == BOOL_NODE_T:
      result = self.VisitBool(node)
    elif ndtype == VOID_NODE_T:
      result = self.VisitVoid(node)
    elif ndtype == INTERNAL_COLLECT_NODE_T:
      result = self.VisitInternalCollect(node)
    elif ndtype == INTERNAL_ALLOCATE_NODE_T:
      result = self.VisitInternalAllocate(node)
    elif ndtype == INTERNAL_GLOBAL_VALUE_NODE_T:
      result = self.VisitInternalGlobalValue(node)
    elif ndtype == SCH_FUNC_DEFINE_NODE_T:
      result = self.VisitFuncDefine(node)
    elif ndtype == SCH_LAMBDA_NODE_T:
      result = self.VisitLambda(node)
    else:
      raise RuntimeError("Unknown Scheme node type={}".format(ndtype))
    self._PostVisitNode(node, result)
    return result

  def VisitProgram(self, node):
    '''Override
    '''
    return node

  def VisitApply(self, node):
    '''Override
    '''
    return node

  def VisitLet(self, node):
    '''Override
    '''
    return node

  def VisitIf(self, node):
    '''Override
    '''
    return node

  def VisitVectorInit(self, node):
    '''Override
    '''
    return node

  def VisitVectorRef(self, node):
    '''Override
    '''
    return node

  def VisitVectorSet(self, node):
    '''Override
    '''
    return node

  def VisitInt(self, node):
    '''Override
    '''
    return node

  def VisitVar(self, node):
    '''Override
    '''
    return node

  def VisitBool(self, node):
    '''Override
    '''
    return node

  def VisitVoid(self, node):
    '''Override
    '''
    return node

  def VisitInternalCollect(self, node):
    '''Override
    '''
    return node

  def VisitInternalAllocate(self, node):
    '''Override
    '''
    return node

  def VisitInternalGlobalValue(self, node):
    '''Override
    '''
    return node

  def VisitFuncDefine(self, node):
    '''Override
    '''
    return node

  def VisitLambda(self, node):
    '''Override
    '''
    return node


'''Build source code from a Scheme AST
'''


class _SchSourceCodeVisitor(SchAstVisitorBase):

  def __init__(self):
    super(_SchSourceCodeVisitor, self).__init__()

  def _BeginVisit(self):
    self._builder = AstSourceCodeBuilder()

  def _EndVisit(self, node, visit_result):
    return self._builder.Build()

  def _PreVisitNode(self, node):
    if NodeHasStaticType(node):
      static_type = GetNodeStaticType(node)
      self._builder.Append('; static_type: {}'.format(
          StaticTypes.Str(static_type)))
      self._builder.NewLine()

  def VisitProgram(self, node):
    # function definitions
    self._builder.Append('(')
    with self._builder.Indent():
      for func_def in GetSchProgramFuncDefList(node):
        self._builder.NewLine()
        self._Visit(func_def)
    self._builder.NewLine()
    self._builder.Append(')')

    # program body, or 'main'
    self._builder.NewLine()
    self._Visit(GetSchProgram(node))
    return node

  def VisitApply(self, node):
    builder = self._builder
    method = GetNodeMethod(node)
    if not isinstance(method, str) and IsSchVarNode(method):
      method = GetNodeVar(method)
    builder.Append('( {}'.format(method))
    with builder.Indent():
      for expr in GetSchApplyExprList(node):
        builder.NewLine()
        self._Visit(expr)
    builder.NewLine()
    builder.Append(')')
    return node

  def VisitLet(self, node):
    builder = self._builder

    builder.Append('( let')
    with builder.Indent():
      builder.NewLine()
      builder.Append('(')
      with builder.Indent():
        for var, var_init in GetNodeVarList(node):
          builder.NewLine()
          builder.Append('[')
          with builder.Indent():
            builder.NewLine()
            self._Visit(var)
            builder.NewLine()
            self._Visit(var_init)
          builder.NewLine()
          builder.Append(']')
      builder.NewLine()
      builder.Append(')')
      builder.NewLine()
      let_body = GetSchLetBody(node)
      self._Visit(let_body)
    builder.NewLine()
    builder.Append(')')
    return node

  def VisitIf(self, node):
    builder = self._builder

    builder.Append('( if')
    with builder.Indent():
      builder.NewLine()
      builder.Append('; cond')
      builder.NewLine()
      self._Visit(GetIfCond(node))

      builder.NewLine()
      builder.Append('; then-branch')
      builder.NewLine()
      self._Visit(GetIfThen(node))

      builder.NewLine()
      builder.Append('; else-branch')
      builder.NewLine()
      self._Visit(GetIfElse(node))

    builder.NewLine()
    builder.Append(')')
    return node

  def VisitVectorInit(self, node):
    builder = self._builder
    builder.Append('( vector')
    with builder.Indent():
      for expr in GetNodeArgList(node):
        builder.NewLine()
        self._Visit(expr)
    builder.NewLine()
    builder.Append(')')
    return node

  def VisitVectorRef(self, node):
    builder = self._builder
    builder.Append('( vector-ref')
    with builder.Indent():
      builder.NewLine()
      self._Visit(GetVectorNodeVec(node))
      builder.NewLine()
      builder.Append(GetVectorNodeIndex(node))
    builder.NewLine()
    builder.Append(')')
    return node

  def VisitVectorSet(self, node):
    builder = self._builder
    builder.Append('( vector-set!')
    with builder.Indent():
      builder.NewLine()
      self._Visit(GetVectorNodeVec(node))
      builder.NewLine()
      builder.Append(GetVectorNodeIndex(node))
      builder.NewLine()
      self._Visit(GetVectorSetVal(node))
    builder.NewLine()
    builder.Append(')')
    return node

  def VisitInt(self, node):
    self._builder.Append(GetIntX(node))
    return node

  def VisitVar(self, node):
    self._builder.Append(GetNodeVar(node))
    return node

  def VisitBool(self, node):
    self._builder.Append(GetNodeBool(node))
    return node

  def VisitVoid(self, node):
    self._builder.Append('( void )')
    return node

  def VisitInternalCollect(self, node):
    bytes = GetInternalCollectNodeBytes(node)
    self._builder.Append('( _collect {} )'.format(bytes))
    return node

  def VisitInternalAllocate(self, node):
    len = GetInternalAllocateNodeLen(node)
    static_type = StaticTypes.Str(GetNodeStaticType(node))
    self._builder.Append('( _allocate {} {} )'.format(len, static_type))
    return node

  def VisitInternalGlobalValue(self, node):
    name = GetInternalGlobalValueNodeName(node)
    self._builder.Append('( global_value "{}" )'.format(name))
    return node

  def VisitFuncDefine(self, node):
    name_node = GetSchFuncDefineName(node)
    self._builder.Append('( define {}'.format(GetNodeVar(name_node)))
    with self._builder.Indent():
      self._builder.NewLine()
      params = GetSchFuncDefineParams(node)
      param_names = ', '.join([GetNodeVar(p) for p in params])
      self._builder.Append('( {} )'.format(param_names))

      self._builder.NewLine()
      self._Visit(GetSchFuncDefineBody(node))
    self._builder.NewLine()
    self._builder.Append(')')
    return node

  def VisitLambda(self, node):
    self._builder.Append('( lambda')
    with self._builder.Indent():
      self._builder.NewLine()
      params = GetSchLambdaParams(node)
      param_names = ', '.join([GetNodeVar(p) for p in params])
      self._builder.Append('( {} )'.format(param_names))

      self._builder.NewLine()
      self._Visit(GetSchLambdaBody(node))
    self._builder.NewLine()
    self._builder.Append(')')
    return node


def SchSourceCode(node):
  visitor = _SchSourceCodeVisitor()
  return visitor.Visit(node)
