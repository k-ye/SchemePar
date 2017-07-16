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
