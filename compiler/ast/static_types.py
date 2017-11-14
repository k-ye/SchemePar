from base import *


class StaticTypes(object):
    INT = 'int'
    BOOL = 'bool'
    VOID = 'void'
    VECTOR = 'vector'

    @staticmethod
    def IsPrimitive(st):
        if not isinstance(st, str):
            return False
        return st in {StaticTypes.INT, StaticTypes.BOOL, StaticTypes.VOID}

    @staticmethod
    def Str(st):
        if StaticTypes.IsPrimitive(st):
            return st
        # st is a vector
        result = '(vector: '
        result += ', '.join([StaticTypes.Str(t) for t in st[1]])
        result += ')'
        return result


def IsValidStaticTypeVector(st):
    if len(st) != 2:
        return False
    if st[0] != StaticTypes.VECTOR:
        return False
    for sub_st in st[1]:
        if not IsValidStaticType(sub_st):
            return False
    return True


def IsValidStaticType(st):
    if StaticTypes.IsPrimitive(st):
        return True
    return IsValidStaticTypeVector(st)


def MakeStaticTypeVector(st_list):
    assert len(st_list) > 0
    st = (StaticTypes.VECTOR, st_list)
    assert IsValidStaticTypeVector(st)
    return st


def GetVectorStaticTypeAt(st, i):
    assert IsValidStaticTypeVector(st)
    return st[1][i]

P_STATIC_TYPE = 'static_type'


def GetNodeStaticType(node):
    return GetProperty(node, P_STATIC_TYPE)


def SetNodeStaticType(node, static_type):
    assert IsValidStaticType(static_type)
    SetProperty(node, P_STATIC_TYPE, static_type)
