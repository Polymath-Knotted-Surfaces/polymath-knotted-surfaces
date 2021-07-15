from sympy.combinatorics.free_groups import free_group
from sympy.combinatorics.fp_groups import FpGroup
from itertools import product

def BraidGroup(n):
    generators = str().join([f"s{str(i)}," for i in range(n)])
    F, *_ = free_group(generators)
    relations = \
        [ f's{i}*s{j}*s{i}**(-1)*s{j}**(-1)'
        for i,j in product(range(n),range(n)) if abs(i-j)>1] + \
        [ f's{i}*s{i+1}*s{i}*s{i+1}**(-1)*s{i}**(-1)*s{i+1}**(-1)'
        for i in range(1,n-1) ]
    return FpGroup(F, relations)
