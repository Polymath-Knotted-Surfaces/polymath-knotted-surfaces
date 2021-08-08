from queue import Queue

# braid: BraidGroup element
# cap: cap diagram represented as a list of pairs
# -> returns the permutation induced by the braid
#    and cap diagram on the base points
def permutation(braid, cap):
    return braid.permutation() * Permutation(cap) * braid.permutation().inverse()

# tangle: pair (braid, cap) where
#   braid: BraidGroup element
#   cap: cap diagram represented as a list of pairs
# -> returns the permutation induced by the braid
#    and cap diagram on the base points
def permutation(tangle):
    return permutation(tangle[0], tangle[1])

# braid: BraidGroup element
# -> returns the number of crossings in the braid
def crossings(braid) -> int:
    return sum(abs(s[1]) for s in braid.syllables())

# braid1, braid2: BraidGroup elements
# cap1, cap2: cap diagrams represented as lists of pairs
# -> returns the number of components in the link formed from
#    reflecting tangle2 and placing it under tangle1
def link_components(braid1, cap1, braid2, cap2) -> int:
    if not braid1.strands() == braid2.strands():
        raise ValueError('All braids must have the same number of strands')
    if braid1.strands() % 2 != 0:
        raise ValueError('Braids must have an even number of strands')
    P1 = permutation(braid1, cap1)
    P2 = permutation(braid2, cap2)
    return len((P1 * P2).cycle_type())

# tangle1, tangle2: pairs (braid1, cap1) and (braid2, cap2) where
#   braid1, braid2: BraidGroup elements
#   cap1, cap2: cap diagrams represented as a list of pairs
# -> returns the number of components in the link formed from
#    reflecting tangle2 and placing it under tangle1
def link_components(tangle1, tangle2) -> int:
    return link_components(tangle1[0], tangle1[1], tangle2[0], tangle2[1])

class Triplane:
    # braid1, braid2, braid3: elements of a BraidGroup
    # cap1, cap2, cap3: cap diagrams represented as lists of pairs
    # -> initializes triplane diagram object formed by using braids
    #    and cap diagrams to create three tangles
    def __init__(self, braid1, cap1, braid2, cap2, braid3, cap3):
        if not (braid1.strands() == braid2.strands() and
                braid2.strands() == braid3.strands()):
            raise ValueError('All braids must have the same number of strands')
        if braid1.strands() % 2 != 0:
            raise ValueError('Braids must have an even number of strands')
        
        self.T1 = (braid1, cap1)
        self.T2 = (braid2, cap2)
        self.T3 = (braid3, cap3)

        self._P1 = permutation(self.T1)
        self._P2 = permutation(self.T2)
        self._P3 = permutation(self.T3)

        self.bridge_number = braid1.strands() / 2
        self.b = self.strands
        self.crossings = crossings(braid1) + crossings(braid2) + crossings(braid3)
    
    # string representation
    def __str__(self) -> str:
        return f'''Triplane Diagram:
        Tangle 1: {self.T1[0]}, {self.T1[1]}
        Tangle 2: {self.T2[0]}, {self.T2[1]}
        Tangle 3: {self.T3[0]}, {self.T3[1]}'''

    # returns True if and only if self is orientable as a triplane diagram
    def orientable(self) -> bool:
        L = [1] + (2*self.b - 1) * [0]

        # BFS for orientation
        Q = Queue()
        Q.put(1)
        while 0 in L:
            if Q.empty():
                Q.put(L.index(0) + 1)
            curr = Q.get()
            new = set([self._P1(curr), self._P2(curr), self._P3(curr)])

            # updates
            for n in new:
                # if L[n - 1] hasn't been reached yet
                if L[n - 1] == 0:
                    L[n - 1] = -L[curr - 1]
                    Q.put(n)
                # elif there's a conflict
                elif L[n - 1] == L[curr - 1]:
                    return False
                # else L[n - 1] is already correct
        
        # if False has not already been returned,
        # an orientation was successfully found
        return True

    # alias for orientable()
    def o(self) -> bool:
        return self.orientable()

    # returns the Euler characteristic of triplane diagram
    def euler_characteristic(self) -> int:
        return (self.b
                + link_components(self.T1, self.T2)
                + link_components(self.T2, self.T3)
                + link_components(self.T3, self.T1))
    
    # alias for euler_characteristic()
    def chi(self) -> int:
        return self.euler_characteristic()
