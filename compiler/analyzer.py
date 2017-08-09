from __future__ import print_function

from ast.base import *
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
        return self._Visit(GetSchProgram(node))

    def VisitApply(self, node):
        method = GetNodeMethod(node)
        expr_list = GetSchApplyExprList(node)
        result = None
        if IsSchArithop(method):
            result = self._VisitArithOp(node, method, expr_list)
        elif IsSchCmpOp(method):
            result = self._VisitCmpOp(node, method, expr_list)
        elif IsSchLogicalOp(method):
            result = self._VisitLogicalOp(node, method, expr_list)
        elif IsSchRtmFn(method):
            result = self._VisitRtmFn(node, method, expr_list)
        else:
            raise NotImplementedError(
                'method={} is not yet supported'.format(method))
        return result

    def _CheckFailed(self, msg):
        raise AnalyzeError('Analyzation failed! ' + msg)
        return False

    def _CheckApplyArity(self, method, expected, expr_list):
        actual = len(expr_list)
        if actual != expected:
            msg = 'Arity did not match for method={}, expected={}, actual={}'.format(
                method, expected, actual)
            return self._CheckFailed(msg)
        return True

    def _CheckTypeMatch(self, expected, actual):
        if actual != expected:
            msg = 'Type mismatch, expected={}, actual={}'.format(
                expected, actual)
            return self._CheckFailed(msg)
        return True

    def _VisitArithOp(self, node, method, expr_list):
        expect_map = {'+': 2, '-': 1}
        self._CheckApplyArity(method, expect_map[method], expr_list)
        for e in expr_list:
            e_type = self._Visit(e)
            self._CheckTypeMatch(SchEvalTypes.INT, e_type)
        return SchEvalTypes.INT

    def _VisitCmpOp(self, node, method, expr_list):
        expect_map = {'eq?': 2, '<': 2, '<=': 2, '>': 2, '>=': 2}
        self._CheckApplyArity(method, expect_map[method], expr_list)

        lhs_type = self._Visit(expr_list[0])
        rhs_type = self._Visit(expr_list[1])
        if method == 'eq?':
            self._CheckTypeMatch(lhs_type, rhs_type)
        else:
            self._CheckTypeMatch(SchEvalTypes.INT, lhs_type)
            self._CheckTypeMatch(SchEvalTypes.INT, rhs_type)
        return SchEvalTypes.BOOL

    def _VisitLogicalOp(self, node, method, expr_list):
        expect_map = {'and': 2, 'or': 2, 'not': 1}
        self._CheckApplyArity(method, expect_map[method], expr_list)
        for e in expr_list:
            e_type = self._Visit(e)
            self._CheckTypeMatch(SchEvalTypes.BOOL, e_type)
        return SchEvalTypes.BOOL

    def _VisitRtmFn(self, node, method, expr_list):
        self._CheckApplyArity(method, 0, expr_list)
        return SchEvalTypes.RtmFnType(method)

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
            return self._Visit(GetSchLetBody(node))

    def VisitIf(self, node):
        cond = GetIfCond(node)
        self._CheckTypeMatch(SchEvalTypes.BOOL, self._Visit(cond))
        then, els = GetIfThen(node), GetIfElse(node)
        then_type, else_type = self._Visit(then), self._Visit(els)
        self._CheckTypeMatch(then_type, else_type)
        return then_type

    def VisitInt(self, node):
        return SchEvalTypes.INT

    def VisitVar(self, node):
        return self._env.Get(GetNodeVar(node))

    def VisitBool(self, node):
        return SchEvalTypes.BOOL


def analyze(node):
    analyzer = _SchAnalyzer()
    return analyzer.Visit(node)


if __name__ == '__main__':
    test_data = '''
    ; a test Scheme program using R2 grammar
    (let ([foo 43] [bar (- 1)])
        (if #t (+ foo bar) (read))
    )
    '''
    test_data = lexer.LexPreprocess(test_data)

    lexer = lexer.SchemeLexer()
    parser = SchemeParser()
    ast = parser.parse(test_data, lexer=lexer)
    print(SchSourceCode(ast))
    print(analyze(ast))