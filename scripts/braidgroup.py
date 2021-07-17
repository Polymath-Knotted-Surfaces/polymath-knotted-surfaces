from sympy.combinatorics.free_groups import free_group
from sympy.combinatorics.fp_groups import FpGroup
import sympy.combinatorics.free_groups as scf
from itertools import product
from cytoolz.curried import map, filter, reduce, pipe, curry, flip
from operator import mul, add, pow
import collections.abc as c

def BraidGroup(n:int) -> FpGroup:
    generators = str().join([f"s{i}," for i in range(1, n)])
    F, *gens= free_group(generators)
    relations = \
        [ gens[i]*gens[j]*gens[i]**(-1)*gens[j]**(-1)
        for i,j in product(range(n-1), repeat=2) if abs(i-j)>1] + \
        [ gens[i]*gens[i+1]*gens[i]*gens[i+1]**(-1)*gens[i]**(-1)*gens[i+1]**(-1)
        for i in range(n-2) ]
    return FpGroup(F, relations)

def braidGens(n:int) -> list[int]:
   return [i for i in range(-n+1,n) if i != 0]

@curry
def words(a:list[str], k:int) -> c.Generator[list[str], None, None]: #generate all words on a of length k
   return product(a, repeat=k)

# @curry
# def wordToBraid( numStrands: int, word: list[int]) -> list[scf.FreeGroupElement]:
@curry
def wordToBraid(group: FpGroup, word: list[int]) -> list[scf.FreeGroupElement]:
    # G = BraidGroup(n)
    gens = group.generators
    return reduce(mul, [gens[i-1] if i>=1 else gens[abs(i)-1]**(-1) for i in word])

def genBraids(numStrands: int, length: int) -> c.Generator[scf.FreeGroupElement, None, None]:
    G = BraidGroup(numStrands)
    return pipe(numStrands,
                braidGens,
                lambda s: words(s, length),
                map(wordToBraid(G))
                )
