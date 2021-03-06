from base import *


class StaticTypes(object):
    INT = 'int'
    BOOL = 'bool'
    VOID = 'void'
    VECTOR = 'vector'

    @staticmethod
    def IsPrimitive(static_type):
        if not isinstance(static_type, str):
            return False
        return static_type in {StaticTypes.INT, StaticTypes.BOOL, StaticTypes.VOID}

    @staticmethod
    def Str(static_type):
        if StaticTypes.IsPrimitive(static_type):
            return static_type
        # st is a vector
        result = '(vector: '
        result += ', '.join([StaticTypes.Str(t) for t in static_type[1]])
        result += ')'
        return result


def IsValidStaticTypeVector(static_type):
    try:
        iter(static_type)
    except TypeError:
        return False

    if len(static_type) != 2:
        return False
    if static_type[0] != StaticTypes.VECTOR:
        return False
    for sub_st in static_type[1]:
        if not IsValidStaticType(sub_st):
            return False
    return True


def IsValidStaticType(static_type):
    if StaticTypes.IsPrimitive(static_type):
        return True
    return IsValidStaticTypeVector(static_type)


def MakeStaticTypeVector(st_list):
    assert len(st_list) > 0
    st = (StaticTypes.VECTOR, st_list)
    assert IsValidStaticTypeVector(st)
    return st


def GetVectorStaticTypeAt(static_type, i):
    assert IsValidStaticTypeVector(static_type), static_type
    return static_type[1][i]


def GetVectorStaticTypeList(static_type):
    assert IsValidStaticTypeVector(static_type), static_type
    return static_type[1]


def ComputeVectorTag(static_type):
    # copied flag, not copied yet
    tag = 1

    # length segment
    st_list = GetVectorStaticTypeList(static_type)
    st_len = len(st_list)
    assert st_len <= 50
    tag |= (st_len << 1)

    # tuple pointer segment
    tuple_pointer_tag = 0
    for i in xrange(st_len):
        if IsValidStaticTypeVector(st_list[i]):
            tuple_pointer_tag |= (1 << i)
    tag |= (tuple_pointer_tag << 7)

    return tag


P_STATIC_TYPE = 'static_type'


def GetNodeStaticType(node):
    return GetProperty(node, P_STATIC_TYPE)


def SetNodeStaticType(node, static_type):
    assert IsValidStaticType(static_type)
    SetProperty(node, P_STATIC_TYPE, static_type)


def NodeHasStaticType(node):
    return HasProperty(node, P_STATIC_TYPE)
