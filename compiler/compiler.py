from __future__ import print_function

from contextlib import contextmanager


class ScopedEnvNode(object):
    '''Abstract class representing one scope in the environment
    '''

    def __init__(self):
        self._parent = None

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, p):
        self._parent = p

    def Contains(self, key):
        # returns a Boolean
        raise NotImplementedError("Contains")

    def Get(self, key):
        # returns the value associated with |key|
        raise NotImplementedError("Get")

    def Add(self, key, value):
        raise NotImplementedError("Add")


class ScopedEnv(object):

    def __init__(self, builder):
        self._builder = builder
        self._top = builder.Build()

    def Contains(self, key):
        cur = self._top
        while cur is not None:
            if cur.Contains(key):
                return True
            cur = cur.parent
        return False

    def Get(self, key):
        cur = self._top
        while cur is not None:
            if cur.Contains(key):
                return cur.Get(key)
            cur = cur.parent
        raise KeyError('Cannot find key: {}'.format(key))

    def Add(self, key, value):
        # add to the top node
        self._top.Add(key, value)

    def Push(self):
        new_top = self._builder.Build()
        new_top.parent = self._top
        self._top = new_top

    def Pop(self):
        old_top = self._top.parent
        self._top = old_top
        if self._top is None:
            raise RuntimeError("Empty stack")

    @contextmanager
    def Scope(self):
        self.Push()
        try:
            yield
        finally:
            self.Pop()


# There should be an analyzation pass first to verify the correctness
# based on static information. i.e. duplicate variable definition in
# the *SAME* scope, type matching. We leave that for later excercises.


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
    |ast|: An SchNode. Its correctness should already be verified
            in the analysis pass.
    '''
    class Builder(object):

        def __init__(self):
            self._global_count = {}

        def Build(self):
            return _UniquifyScopedEnvNode(self._global_count)

    env = ScopedEnv(Builder())
    return _Uniquify(ast, env)


def Compile(ast):
    ast = Uniquify(ast)
    return ast
