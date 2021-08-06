from sympy.combinatorics.free_groups import free_group
from sympy.combinatorics.fp_groups import FpGroup
import sympy.combinatorics.free_groups as scf
from itertools import product
from cytoolz import reduce, pipe, curry, flip, valfilter, get, filter
from operator import mul, add, pow
import collections.abc as c
import csv
import os
from typing import NewType, List, Tuple, Dict, Generator



def dictTranspose(d:dict) -> dict: #returns a dict with keys the (hashed versions of) d.values and values the keys of d matching the (hashed) value.
    new_dict = dict()
    temp = {k: v if type(v) is not list else tuple(v) for k,v in d.items()}
    for key, value in temp.items():
        if value in new_dict:
            new_dict[value].append(key)
        else:
            new_dict[value]=[key]
    return new_dict


def myBraidGroup(n:int) -> FpGroup:
    generators = str().join([f"s{i}," for i in range(1, n)])
    F, *gens= free_group(generators)
    relations = \
        [ gens[i]*gens[j]*gens[i]**(-1)*gens[j]**(-1)
        for i,j in product(range(n-1), repeat=2) if abs(i-j)>1] + \
        [ gens[i]*gens[i+1]*gens[i]*gens[i+1]**(-1)*gens[i]**(-1)*gens[i+1]**(-1) 
        for i in range(n-2) ]
    #the first comprehension generates the commutator relators; the second comprehension generates the adjacency relators
    return FpGroup(F, relations)

def braidGens(n:int) -> List[int]:
   return [i for i in range(-n+1,n) if i != 0] #this function generates the list -n+1, -n+2, ..., -1, 1, 2, ..., n-1

@curry
def words(a:List[str], k:int) -> Generator[List[str], None, None]: #generate all words on a of length k
   return product(a, repeat=k)

#words(A(n)) is a new function w whose input is k, an integer, and it spits out all words of length k on A.

@curry
def wordToBraid(group: FpGroup, word: List[int]) -> List[scf.FreeGroupElement]:
    # G = BraidGroup(n)
    gens = group.generators
    return reduce(mul, [gens[i-1] if i>=1 else gens[abs(i)-1]**(-1) for i in word]) #this returns the product (mul) of corresponding group.generators for each entry in word.



def genBraids(numStrands: int, length: int) -> Generator[List[int], None, None]:
    #G = BraidGroup(numStrands)
    return pipe(numStrands,
                braidGens, #generates the braids
                lambda s: words(s, length)#, #changes each tuple to a word
                #map(wordToBraid(G))
                )
                
def elimBraids(numStrands:int, braids: List[List[int]]) -> List[List[int]]: #formerly -> List[Tuple[List[int], scf.FreeGroupElement]]:
    G = myBraidGroup(numStrands)
    m = {i:wordToBraid(G, b) for i,b in enumerate(braids)} #generates a dictionary with integer keys and values words in G.
    mt = dictTranspose(m) #transposes m so that each braid word corresponds to a bunch of indices.
    r = {k[0]:list(m[k[0]]) for v, k in mt.items()} #keep only one braid word for each braid type. here k is a list, so get the first entry.
    # return list(zip(get(list(m.keys()), braids, default=None), list(m.values())#return pairs of braid, braid_as_word
    #return [(braids[k], v) for k, v in r.items()] #returns braid_as_tuple, braid_as_word
    newBraids = [braids[k] for k in r.keys()]
    bstrings = list(map(lambda b: ','.join(map(str,b)), newBraids))
    newbstrings = list(filter(lambda s: all([bool(f'{j},{-j}' not in s) for j in braidGens(numStrands)]), bstrings))
    #looks for ANY occurance of the pattern 'j,-j' or '-j,j' and if it occurs, throws out the word.
    result = list(map(lambda s: list(map(int, s.split(','))), newbstrings)) #converts each braid-as-string back to braid-as-list
    return result
     
    #return [(braids[k], v) for k, v in r.items()] #returns braid_as_tuple, braid_as_word

# creates a file with a standard way of naming and writes reduced_braids to it
# mainly just here to unclutter braidsNoRepeats()
def createFile(numStrands:int, length:int, reduced_braids:List[List[int]]) -> List[List[int]]:
    with open(f'../braid_lists/b{numStrands}_k{length}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(reduced_braids)
    return reduced_braids

def braidsFromFile(numStrands:int, length:int) -> List[Tuple[int]]:
    try:
        with open(f'../braid_lists/b{numStrands}_k{length}.csv', 'r', newline='') as file:
            return parseBraidFile(file)
    except FileNotFoundError:
        return braidsNoRepeats(numStrands, length)

def parseBraidFile(file) -> List[List[int]]: #reads a file and returns the correctly formatted list of list of integers.
    reader = csv.reader(file, delimiter = ',') #read the csv file, delimited by commas.
    return [[int(j) for j in row] for row in reader] #iterates row-by-row and cell-by-cell, converting everything to ints.

# returns a list of all braids on a given number of strands of a given length
# no repeats within the list for the given length, but there are definitely repeats between lengths
def braidsNoRepeats(numStrands:int, length:int, recalculate:bool=False) ->  List[List[int]]:
    if numStrands < 0:
        raise ValueError('numStrands must be a positive number')
    try:
        if recalculate:
            raise ValueError('recalculate = True') # go to the except block
        with open(f'../braid_lists/b{numStrands}_k{length}.csv', 'r', newline='') as file:
            return parseBraidFile(file) #returns original braids.
    except:
        if length == 0: # this 'if' instead of storing an empty file
            return [[]]
        
        braid_gens = braidGens(numStrands)
        
        if length == 1: # will only run the first time braidsNoRepeats is called for a specific numStrands value
            return createFile(numStrands, length, [[j] for j in braid_gens])
        
        smaller_braids = braidsNoRepeats(numStrands, length - 1) # gets the smaller braids with a recursive call
        new_braids = [ s+[j] for s in smaller_braids for j in braid_gens ] # fast way to append generators
        reduced_braids = elimBraids(numStrands, new_braids)
        return createFile(numStrands, length, reduced_braids)