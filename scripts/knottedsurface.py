import snappy
import spherogram as s
from spherogram.links.tangles import join_strands
import sys
import random
from cytoolz.curried import *
from snappy import Link
sys.setrecursionlimit(1000000)


# process of putting each section of strands as a stack from top to bottom
def horizontal_amalgam(tangles):
    assert len(tangles) > 0
    ans = tangles[0]
    for T in tangles[1:]:
        ans = ans | T
    return ans


# creates each specific section of the tangle
def sigma(k, n, q):
    C = s.RationalTangle(q)
    Id = s.IdentityBraid(1)

    tangles = k*[Id] + [C] + (n - k - 2)*[Id]

    return horizontal_amalgam(tangles)

# converts a word in Artin generators of braid group
# to a tangle corresponding to the braid
#  - word is represented as a list of integers
#  - n is the number of strands
def word_to_braid(word, n):
    T = horizontal_amalgam(n*[ s.IdentityBraid(1) ])
    for k in word:
        r = 1 if k > 0 else -1
        T = sigma(abs(k) - 1, n, r) * T
    return T

# converts list of pairs to cap diagram as a Tangle
#  - pairs should be of the form (i,j) [1 <= i, j <= 2n] and represent a cap diagram
def pairs_to_cap(pairs):
    T = horizontal_amalgam((2*len(pairs))*[s.IdentityBraid(1)]) # create 2n strands
    for p in pairs:
        join_strands(T.adjacent[T.n + p[0] - 1], T.adjacent[T.n + p[1] - 1])
    return T

# attaches cap diagram (usually from pairs_to_cap) to the top of a tangle
'''def add_cap(T, cap):
    if T.n != cap.n:
        raise ValueError("The braid and cap must have the same number of strands")
    return T * cap'''

# attaches a cap diagram in the form of a list[list[int]] to the top of a tangle 
def add_cap(tang: s.Tangle, cap):
    if tang.n != 2 * len(cap):
        raise ValueError("The braid and cap must have the same number of strands")
    for l in cap:
        join_strands(tang.adjacent[l[0]+tang.n-1], tang.adjacent[l[1]+tang.n-1])
    return s.Tangle(n = tang.n, crossings = tang.crossings, entry_points = tang.adjacent[:tang.n])

# attaches two tangles in the right way to check tri plane diagrams
# returns a Link
# implementation mimics implementation of __mul__ in Tangle class
def attach(T1, T2):
    if T1.n != T2.n:
        raise ValueError("Both tangles must have the same number of strands")
    A, B = T1.copy(), T2.copy()
    a, b = A.adjacent, B.adjacent
    n = A.n
    for i in range(n):
        join_strands(a[i], b[i])
    return s.Link(A.crossings + B.crossings, check_planarity=False)


def unlink(n: int) -> Link:
    return Link(braid_closure=list(interleave((range(1,n),range(-1,-n,-1)))))

@curry
def checkCovers(maxmod: int, L:Link) -> bool:
    # returns true if Ext(L) has the same torsion numbers
    # as the exterior of the same number of components as L for k = 3, ..., maxmod
    n = len(L.link_components)
    if n == 0:
        return True #return true for trivial links and skip the below computation.
    else:
        U = unlink(n)
        Uhom = {k: U.exterior().covers(k, cover_type='cyclic')[0].homology() for k in range(3,maxmod+1)}
        Lhom = {k: L.exterior().covers(k, cover_type='cyclic')[0].homology() for k in range(3,maxmod+1)}
        return Uhom==Lhom


# returns True if and only if the link is an unlink
def is_unlink(L, maxmod:int=17, tol:float=10**-4):
    # issue: it is UNDECIDABLE (in the sense of Turing) to determine whether a given presentation is trivial. This might miss some.
    # we can check if the n-component unlink has the same invariants as L. 
    # An n-compoent unlink can be given as unlink = lambda n: Link(braid_closure=list(interleave((range(1,n),range(-1,-n,-1)))))
    # L2 = unlink(2)
    return L.exterior().fundamental_group().relators() == [] or checkCovers(maxmod, L) or abs(L.exterior.volume()) <= tol

# returns True if and only if the three tangles form a triplane diagram
def is_triplane(T1, T2, T3):
    L12 = attach(T1, T2)
    L23 = attach(T2, T3)
    L31 = attach(T3, T1)
    return is_unlink(L12) and is_unlink(L23) and is_unlink(L31)


#######################################################################


# creates the rainbow tangle where the end of the braid is put together in a rainbow effect
def rainbow_tangle(n):

    place = n-1
    round = (n/2)-1
    bow = s.IdentityBraid(n)
    i = 1

    while (i <= round):
        j = 2
        while (j <= place):
            k = n - j
            next_bow = sigma(k, n, 1)
            bow = bow * next_bow
            j += 1
        place -= 2
        i += 1
    return bow


# creates the smiley tangle where the end of the outside strands are put together
# and the inside strands are put together side by side
def smiley_tangle(n):

    place = n-1
    j = 2
    smile = s.IdentityBraid(n)

    while(j <= place):
        k = n - j
        grin = sigma(k, n, 1)
        smile = smile * grin
        j += 1
    return smile


# random knot generator
# input number of strands as n and number of sections as k
# use def extra_fancy(args) without * when using random_knot function
def random_tangle(n, k):

    linkcomps = [0]*(2*k+1)
    linkcomps[0] = n
    i = 1

    while i < 2*k+1:
        place = random.randint(0, n-2)
        cross = 2*random.randint(0, 1)-1
        linkcomps[i] = place

        linkcomps[i+1] = cross
        i += 2
    print(linkcomps)
    return extra_fancy(linkcomps)


# checks for the number of components in link passed through
def unlink_check(link):

    group = link.exterior().fundamental_group().relators()

    if (group == []):
        state = True
    else:
        state = False
    return state


# this function passes through link, strand number, and and tangle section
# through to see if it is a surface or not, hence the name
# you can return identify or smiley if you want to view the tangle
def surface_or_not(knot, tang, i):

    if unlink_check(knot) == True:
        identify = tang*smiley_tangle(i)
        smiley = identify.bridge_closure()
        if unlink_check(smiley) == True:
            print("surface")
        else:
            print("not surface")
    else:
        print("not surface")
    # return identify
    # return smiley
    return


# builds our extra_fancy link using smiley_tangle
# also calls the unlink_check to determine whether it is an unlink or not
# def extra_fancy(*args):
# * should be used to insert arguments of any length
# Test: trefoil should be extra_fancy(4,1,1,0,-1,1,1)


# def extra_fancy(*args):
def extra_fancy(args):
    assert len(args) > 2
    length = len(args)
    i = args[0]
    t = args[1]
    a = args[2]
    tang = sigma(t, i, a)
    pos = []
    slope = []
    y = 3
    q = 4
    while (y <= length-2):  # create loop for pos that runs through args after index 3 until it ends
        num1 = args[y]
        pos += [num1]
        y += 2
    while (q <= length-1):  # create loop for slope that runs through args after index 4 until it ends
        num2 = args[q]
        slope += [num2]
        q += 2
    r = len(slope)
    for x in range(0, r):
        k = pos[x]
        s = slope[x]
        tang = tang * sigma(k, i, s)    # k is position, s is the tangle
    knot = tang.bridge_closure()
    surface_or_not(knot, tang, i)
    return
