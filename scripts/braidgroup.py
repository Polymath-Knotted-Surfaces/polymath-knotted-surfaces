from sympy.combinatorics.free_groups import free_group
from sympy.combinatorics.fp_groups import FpGroup
import sympy.combinatorics.free_groups as scf
from itertools import product
from cytoolz import reduce, pipe, curry, flip, valfilter, get
from operator import mul, add, pow
import collections.abc as c

def dictTranspose(d:dict) -> dict: #returns a dict with keys the (hashed versions of) d.values and values the keys of d matching the (hashed) value.
    new_dict = dict()
    for key, value in d.items():
        if hash(value) in new_dict:
            new_dict[hash(value)].append(key)
        else:
            new_dict[hash(value)]=[key]
    return new_dict


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

#words(A(n)) is a new function w whose input is k, an integer, and it spits out all words of length k on A.


# @curry
# def wordToBraid( numStrands: int, word: list[int]) -> list[scf.FreeGroupElement]:
@curry
def wordToBraid(group: FpGroup, word: list[int]) -> list[scf.FreeGroupElement]:
    # G = BraidGroup(n)
    gens = group.generators
    return reduce(mul, [gens[i-1] if i>=1 else gens[abs(i)-1]**(-1) for i in word]) #this returns the product (mul) of corresponding group.generators for each entry in word.



def genBraids(numStrands: int, length: int) -> c.Generator[list[int], None, None]:
    #G = BraidGroup(numStrands)
    return pipe(numStrands,
                braidGens,
                lambda s: words(s, length)#,
                #map(wordToBraid(G))
                )
                
def elimBraids(numStrands:int, braids: list[list[int]]) -> list[tuple[list[int], scf.FreeGroupElement]]:
    G = BraidGroup(numStrands)
    m = {i:wordToBraid(G, b) for i,b in enumerate(braids)}
    mt = dictTranspose(m)
    r = {k[0]:m[k[0]] for v, k in mt.items()} #keep only one braid word for each braid type.
    # return list(zip(get(list(m.keys()), braids, default=None), list(m.values())#return pairs of braid, braid_as_word
    return [(braids[k], v) for k, v in r.items()] #returns braid_as_tuple, braid_as_word

def braidsNoRepeats(numStrands:int, length:int) ->  list[tuple[list[int], scf.FreeGroupElement]]:
    return elimBraids(numStrands, list(genBraids(numStrands, length)))