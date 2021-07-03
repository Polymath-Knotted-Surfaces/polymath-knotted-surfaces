import snappy
import spherogram
from spherogram.links.tangles import join_strands
import sys
import random

sys.setrecursionlimit(1000000)


# process of putting each section of strands as a stack from top to bottom
def horizontal_amalgam(tangles):
    assert len(tangles) > 0
    ans = tangles[0]
    for T in tangles[1:]:
        ans = ans | T
    return ans


# creates each specific section of the tangle
def sigma(k, n, s):
    C = spherogram.RationalTangle(s)
    Id = spherogram.IdentityBraid(1)

    tangles = k*[Id] + [C] + (n - k - 2)*[Id]

    return horizontal_amalgam(tangles)


# creates the rainbow tangle where the end of the braid is put together in a rainbow effect
def rainbow_tangle(n):

    place = n-1
    round = (n/2)-1
    bow = spherogram.IdentityBraid(n)
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
    smile = spherogram.IdentityBraid(n)

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
    print linkcomps
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

