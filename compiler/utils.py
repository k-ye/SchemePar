import string
import random


def GenerateRandomAlnumString(n):
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(n))


class UGraph(object):

    def __init__(self):
        self._adj_list = {}

    @property
    def num_vertices(self):
        return len(self._adj_list)

    def AddVertex(self, u):
        if self.HasVertex(u):
            raise RuntimeError("vertex={} already exists")
        self._adj_list[u] = set()

    def HasVertex(self, u):
        return u in self._adj_list

    def _AddVertexIfNotExist(self, u):
        if not self.HasVertex(u):
            self.AddVertex(u)

    def AddEdge(self, u, v):
        self._AddVertexIfNotExist(u)
        self._AddVertexIfNotExist(v)
        self._adj_list[u].add(v)
        self._adj_list[v].add(u)

    def HasEdge(self, u, v):
        if not (self.HasVertex(u) and self.HasVertex(v)):
            return False
        result = u in self._adj_list[v]
        assert result == v in self._adj_list[u]
        return result

    def AdjacentVertices(self, u):
        assert self.HasVertex(u)
        for v in self._adj_list[u]:
            yield v
