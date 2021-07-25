from sympy.combinatorics.free_groups import free_group
from sympy.combinatorics.fp_groups import FpGroup
import sympy.combinatorics.free_groups as scf
from itertools import product
from cytoolz import reduce, pipe, curry, flip, valfilter, get
from operator import mul, add, pow
import collections.abc as c
import csv
import os

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
    #the first comprehension generates the commutator relators; the second comprehension generates the adjacency relators
    return FpGroup(F, relations)

def braidGens(n:int) -> list[int]:
   return [i for i in range(-n+1,n) if i != 0] #this function generates the list -n+1, -n+2, ..., -1, 1, 2, ..., n-1

@curry
def words(a:list[str], k:int) -> c.Generator[list[str], None, None]: #generate all words on a of length k
   return product(a, repeat=k)

#words(A(n)) is a new function w whose input is k, an integer, and it spits out all words of length k on A.

@curry
def wordToBraid(group: FpGroup, word: list[int]) -> list[scf.FreeGroupElement]:
    # G = BraidGroup(n)
    gens = group.generators
    return reduce(mul, [gens[i-1] if i>=1 else gens[abs(i)-1]**(-1) for i in word]) #this returns the product (mul) of corresponding group.generators for each entry in word.



def genBraids(numStrands: int, length: int) -> c.Generator[list[int], None, None]:
    #G = BraidGroup(numStrands)
    return pipe(numStrands,
                braidGens, #generates the braids
                lambda s: words(s, length)#, #changes each tuple to a word
                #map(wordToBraid(G))
                )
                
def elimBraids(numStrands:int, braids: list[list[int]]) -> list[tuple[list[int], scf.FreeGroupElement]]:
    G = BraidGroup(numStrands)
    m = {i:wordToBraid(G, b) for i,b in enumerate(braids)} #generates a dictionary with integer keys and values words in G.
    mt = dictTranspose(m) #transposes m so that each braid word corresponds to a bunch of indices.
    r = {k[0]:m[k[0]] for v, k in mt.items()} #keep only one braid word for each braid type. here k is a list, so get the first entry.
    # return list(zip(get(list(m.keys()), braids, default=None), list(m.values())#return pairs of braid, braid_as_word
    return [(braids[k], v) for k, v in r.items()] #returns braid_as_tuple, braid_as_word

# creates a file with a standard way of naming and writes reduced_braids to it
# mainly just here to unclutter braidsNoRepeats()
def createFile(numStrands:int, length:int, reduced_braids:list[list[int]]) -> list[list[int]]:
    with open(f'../braid_lists/b{numStrands}_k{length}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(reduced_braids)
    return reduced_braids
    
def braidReader(file) -> list[list[int]]: #reads a file and returns the correctly formatted list of list of integers.
    reader = csv.reader(file, delimiter=',') #read the csv file, delimited by commas.
    return [[int(j) for j in row] for row in reader] #iterates row-by-row and cell-by-cell, converting everything to ints.

def braidsNoRepeats(numStrands:int, length:int, recalculate:bool=False) ->  list[list[int]]:
    if numStrands < 0 or numStrands % 2 != 0:
        raise ValueError('numStrands must be a positive even number')
    try:
        if recalculate:
            raise ValueError('recalculate = True') # go to the except block
        with open(f'../braid_lists/b{numStrands}_k{length}.csv', 'r', newline='') as file:
            # reader = csv.reader(file)
            # return list(reader) # if the desired list has already been created, returns it
            return braidReader(file) #returns original braids.
    except:
        # print('excepted') # for debugging
        if length == 0: # this 'if' instead of storing an empty file
            return [[]]
        
        braid_gens = braidGens(numStrands)
        
        if length == 1: # will only run the first time braidsNoRepeats is called for a specific numStrands value
            #reduced_braids = [[i] for i in range(-numStrands+1,numStrands) if i != 0] #no need for this line, we already have braid_gens that has this exact list.
            return createFile(numStrands, length, braid_gens)
        try: # if possible, reads from the file with length one less than desired
            smaller_braids = []
            with open(f'../braid_lists/b{numStrands}_k{length-1}.csv', 'r', newline='') as file:
                #reader = csv.reader(file, delimiter=',')
                smaller_braids = braidReader(file)
            # print('try', smaller_braids) # for debugging, seemingly working correctly
            new_braids = [s+[j] for s in smaller_braids for j in braid_gens] #this is much faster.
            # for i in smaller_braids: # **process of creating new_braids can probably be made more efficient**
                # for j in braid_gens:
                    # new_braids.append([i[0], j])
            # print('try', new_braids) # for debugging, seemingly working correctly
            with_elements = list(zip(*elimBraids(numStrands, new_braids)))
            reduced_braids = list(with_elements[0]) # because I think with_elements is a list(tuple(...)) at this point
            # print('try', reduced_braids)
            return createFile(numStrands, length, reduced_braids)
        except: # if the file with length one less than desired does not exist, create it with a recursive call
            smaller_braids = braidsNoRepeats(numStrands, length - 1) 
            new_braids = [s+[j] for s in smaller_braids for j in braid_gens] #this is much faster than two for loops.
            # for i in smaller_braids:
                # for j in braid_gens:
                    # new_braids.append([i[0], j])
            with_elements = list(zip(*elimBraids(numStrands, new_braids)))
            reduced_braids = list(with_elements[0]) # because I think with_elements is a list(tuple(...)) at this point
            return createFile(numStrands, length, reduced_braids)