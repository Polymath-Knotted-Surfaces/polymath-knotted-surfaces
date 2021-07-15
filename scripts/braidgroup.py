from sympy.combinatorics.free_groups import free_group
from sympy.combinatorics.fp_groups import FpGroup

def BraidGroup(n):
    generators = ''.join(['s' + str(i) + ',' for i in range(n)])
    F = free_group(generators)[0]
    
    relations = []
    
    # add relation si*sj*si**-1*sj**-1 for all |i - j| > 1
    for i in range(8):
        for j in range(8):
            if abs(i - j) > 1:
                I, J = str(i), str(j)
                relations.append(''.join(['s', I, '*s', J, '*s', I, '**-1*s', J, '**-1']))
    
    # add relation si*s(i + 1)*si*s(i + 1)**-1*si**-1*s(i + 1)**-1 for all 1 <= i < = n - 2
    for i in range(1, 8 - 1):
        I, Ip = str(i), str(i + 1)
        relations.append(''.join(['s', I, '*s', Ip, '*s', I, '*s', Ip, '**-1*s', I, '**-1*s', Ip, '**-1']))
    
    B = FpGroup(F, relations)
    
    return B
