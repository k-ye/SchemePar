from __future__ import print_function

from ast.base import *
from ast.static_types import *
from ast.sch_ast import *
from ast.scoped_env import ScopedEnv, ScopedEnvNode

import lexer
from parser import SchemeParser


class AnalyzeError(Exception):
    pass


class _AnalyzeScopedEnvNode(ScopedEnvNode):

    def __init__(self):
        super(_AnalyzeScopedEnvNode, self).__init__()
        # maps a variable name to its type
        self._var_type = {}

    def Contains(self, key):
        return key in self._var_type

    def Get(self, key):
        return self._var_type[key]

    def Add(self, key, value):
        assert not self.Contains(key)
        self._var_type[key] = value


# We don't allow for type inference for 'read'. Think about what could happen
# in this case:
#                   `(eq? (read) (read))`
#
# 'read' must return an int. Meanwhile, we provide 'read_int' (alias of 'read')
# and 'read_bool' in runtime.
#
# _TYPE_ANY = 'any'

class _SchAnalyzer(SchAstVisitorBase):

    def __init__(self):
        super(_SchAnalyzer, self).__init__()
        self._env = None

    def _BeginVisit(self):

        class Factory(object):

            def Build(self):
                return _AnalyzeScopedEnvNode()

        self._env = ScopedEnv(Factory())

    def VisitProgram(self, node):
        static_type = self._Visit(GetSchProgram(node))
        SetNodeStaticType(node, static_type)
        return static_type

    def VisitApply(self, node):
        method = GetNodeMethod(node)
        expr_list = GetSchApplyExprList(node)
        static_type = None
        if IsSchArithop(method):
            static_type = self._VisitArithOp(node, method, expr_list)
        elif IsSchCmpOp(method):
            static_type = self._VisitCmpOp(node, method, expr_list)
        elif IsSchLogicalOp(method):
            static_type = self._VisitLogicalOp(node, method, expr_list)
        elif IsSchRtmFn(method):
            static_type = self._VisitRtmFn(node, method, expr_list)
        else:
            raise NotImplementedError(
                'method={} is not yet supported'.format(method))
        SetNodeStaticType(node, static_type)
        return static_type

    def _CheckCondition(self, cond, msg):
        if not cond:
            raise AnalyzeError('Analyzation failed! ' + msg)
        return cond

    def _CheckApplyArity(self, method, expected, expr_list):
        actual = len(expr_list)
        msg = 'Arity did not match for method={}, expected={}, actual={}'.format(
            method, expected, actual)
        return self._CheckCondition(actual == expected, msg)

    def _CheckTypeMatch(self, expected, actual):
        msg = 'Type mismatch, expected={}, actual={}'.format(expected, actual)
        return self._CheckCondition(actual == expected, msg)

    def _VisitArithOp(self, node, method, expr_list):
        expect_map = {'+': 2, '-': 1}
        self._CheckApplyArity(method, expect_map[method], expr_list)
        for e in expr_list:
            e_type = self._Visit(e)
            self._CheckTypeMatch(StaticTypes.INT, e_type)
        static_type = StaticTypes.INT
        SetNodeStaticType(node, static_type)
        return static_type

    def _VisitCmpOp(self, node, method, expr_list):
        expect_map = {'eq?': 2, '<': 2, '<=': 2, '>': 2, '>=': 2}
        self._CheckApplyArity(method, expect_map[method], expr_list)

        lhs_type = self._Visit(expr_list[0])
        rhs_type = self._Visit(expr_list[1])
        if method == 'eq?':
            self._CheckTypeMatch(lhs_type, rhs_type)
        else:
            self._CheckTypeMatch(StaticTypes.INT, lhs_type)
            self._CheckTypeMatch(StaticTypes.INT, rhs_type)

        static_type = StaticTypes.BOOL
        SetNodeStaticType(node, static_type)
        return static_type

    def _VisitLogicalOp(self, node, method, expr_list):
        expect_map = {'and': 2, 'or': 2, 'not': 1}
        self._CheckApplyArity(method, expect_map[method], expr_list)
        for e in expr_list:
            e_type = self._Visit(e)
            self._CheckTypeMatch(StaticTypes.BOOL, e_type)

        static_type = StaticTypes.BOOL
        SetNodeStaticType(node, static_type)
        return static_type

    def _VisitRtmFn(self, node, method, expr_list):
        self._CheckApplyArity(method, 0, expr_list)
        static_type = SchEvalTypes.RtmFnType(method)
        SetNodeStaticType(node, static_type)
        return static_type

    def VisitLet(self, node):
        let_var_types = {}
        for var, var_init in GetNodeVarList(node):
            var_name = GetNodeVar(var)
            var_type = self._Visit(var_init)
            assert var_name not in let_var_types
            let_var_types[var_name] = var_type

        with self._env.Scope():
            for var_name, var_type in let_var_types.iteritems():
                self._env.Add(var_name, var_type)

            static_type = self._Visit(GetSchLetBody(node))
            SetNodeStaticType(node, static_type)
            return static_type

    def VisitIf(self, node):
        cond = GetIfCond(node)
        self._CheckTypeMatch(StaticTypes.BOOL, self._Visit(cond))
        then, els = GetIfThen(node), GetIfElse(node)
        then_type, else_type = self._Visit(then), self._Visit(els)
        self._CheckTypeMatch(then_type, else_type)

        static_type = then_type
        SetNodeStaticType(node, static_type)
        return static_type

    def VisitVectorInit(self, node):
        st_list = []
        for arg in GetNodeArgList(node):
            st_list.append(self._Visit(arg))

        static_type = MakeStaticTypeVector(st_list)
        SetNodeStaticType(node, static_type)
        return static_type

    def VisitVectorRef(self, node):
        vec_static_type = self._Visit(GetVectorNodeVec(node))
        msg = 'Expected a vector static type, actual={}'.format(
            StaticTypes.Str(vec_static_type))
        self._CheckCondition(IsValidStaticTypeVector(vec_static_type), msg)

        idx_node = GetVectorNodeIndex(node)
        self._CheckTypeMatch(StaticTypes.INT, self._Visit(idx_node))
        idx = GetIntX(idx_node)

        static_type = GetVectorStaticTypeAt(vec_static_type, idx)
        SetNodeStaticType(node, static_type)
        return static_type

    def VisitVectorSet(self, node):
        vec_static_type = self._Visit(GetVectorNodeVec(node))
        msg = 'Expected a vector static type, actual={}'.format(
            StaticTypes.Str(vec_static_type))
        self._CheckCondition(IsValidStaticTypeVector(vec_static_type), msg)

        idx_node = GetVectorNodeIndex(node)
        self._CheckTypeMatch(StaticTypes.INT, self._Visit(idx_node))
        idx = GetIntX(idx_node)

        expect_static_type = GetVectorStaticTypeAt(vec_static_type, idx)
        actual_static_type = self._Visit(GetVectorSetVal(node))
        self._CheckTypeMatch(expect_static_type, actual_static_type)

        static_type = StaticTypes.VOID
        SetNodeStaticType(node, static_type)
        return static_type

    def VisitInt(self, node):
        static_type = StaticTypes.INT
        SetNodeStaticType(node, static_type)
        return static_type

    def VisitVar(self, node):
        static_type = self._env.Get(GetNodeVar(node))
        SetNodeStaticType(node, static_type)
        return static_type

    def VisitBool(self, node):
        static_type = StaticTypes.BOOL
        SetNodeStaticType(node, static_type)
        return static_type

    def VisitVoid(self, node):
        static_type = StaticTypes.VOID
        SetNodeStaticType(node, static_type)
        return static_type

    def VisitInternalCollect(self, node):
        raise AnalyzeError('Collect is unexpected in type analysis pass.')

    def VisitInternalAllocate(self, node):
        raise AnalyzeError('Allocate is unexpected in type analysis pass.')

    def VisitInternalGlobalValue(self, node):
        raise AnalyzeError('GlobalValue is unexpected in type analysis pass.')


def analyze(node):
    analyzer = _SchAnalyzer()
    return analyzer.Visit(node)


if __name__ == '__main__':
    test_data = '''
    ; a test Scheme program using R2 grammar
    (let ([foo 43] [bar (- 1)] (x (vector 42 1 #t (vector 5))))
        (if #t (+ foo bar) (vector-ref (vector-ref x 3) 0))
    )
    '''
    test_data = lexer.LexPreprocess(test_data)

    lexer = lexer.SchemeLexer()
    parser = SchemeParser()
    ast = parser.parse(test_data, lexer=lexer)

    analyze(ast)
    print(SchSourceCode(ast))
