from queue import Queue

# braid: BraidGroup element
# cap: cap diagram represented as a list of pairs
# -> returns the permutation induced by the braid
#    and cap diagram on the base points
def permutation(braid, cap):
    return braid.permutation() * Permutation(cap) * braid.permutation().inverse()

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
    basepoints = set(range(1, braid1.strands() + 1))
    visited = set()
    curr = 1
    components = 1

    while visited != basepoints:
        if curr in visited:
            curr = min(basepoints.difference(visited))
            components += 1
        visited.add(curr)
        curr = P1(curr)
        visited.add(curr)
        curr = P2(curr)
    
    return components

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
        
        # tangles
        self.T1 = (braid1, cap1)
        self.T2 = (braid2, cap2)
        self.T3 = (braid3, cap3)

        # induced permutations from tangles
        self._P1 = permutation(braid1, cap1)
        self._P2 = permutation(braid2, cap2)
        self._P3 = permutation(braid3, cap3)

        # basic useful data
        self.bridge_number = braid1.strands() / 2
        self.b = self.bridge_number
        self.crossings = crossings(braid1) + crossings(braid2) + crossings(braid3)
        self.orientation = ([], [], []) # start with empty orientation; can update this with orient()
    
    # -> string representation of self
    def __str__(self) -> str:
        return f'''Triplane Diagram:
        Tangle 1: {self.T1[0]}, {self.T1[1]}
        Tangle 2: {self.T2[0]}, {self.T2[1]}
        Tangle 3: {self.T3[0]}, {self.T3[1]}'''
    
    # updates self.orientation:
    #   - if self is orientable, saves a valid orientation
    #   - if self is nonorientable, saves three lists of 0's
    # -> returns True if and only if self is orientable
    # NOTE: will always give the same permutation for the same Triplane diagram
    def orient(self) -> bool:
        # don't run algorithm if not necessary
        if self.orientation[0]:
            return self.o()
        
        # lists represent orientation on each tangle
        L1 = [1] + (2*self.b - 1) * [0]
        L2 = [1] + (2*self.b - 1) * [0]
        L3 = [1] + (2*self.b - 1) * [0]
        L  = [1] + (2*self.b - 1) * [0] # master list to check compatibility
        just_added = set([1])
        temp = set()

        while (0 in L1 or 0 in L2 or 0 in L3):
            # if no more inferences can be made, but there are
            # still things to orient, arbitrarily orient one of them
            if not just_added:
                if 0 in L1:
                    L1[L1.index(0)] = 1
                    just_added.add(L1.index(0))
                elif 0 in L2:
                    L2[L2.index(0)] = 1
                    just_added.add(L2.index(0))
                elif 0 in L3:
                    L3[L3.index(0)] = 1
                    just_added.add(L3.index(0))
            
            for n in just_added:
                n1 = self._P1(n)
                o1 = -L1[n - 1]
                # if n has not been oriented in T1 yet, orient according to master list
                if o1 == 0:
                    L1[n - 1] = L[n - 1]
                    # now, make inferences about position n1 = P1(n)
                    if L[n1 - 1] == 0: # if n1 hasn't been oriented anywhere
                        L[n1 - 1] = -L[n - 1]
                        L1[n1 - 1] = -L[n - 1]
                        temp.add(n1)
                    elif L[n1 - 1] == -L[n - 1]: # if the new orientation is compatible
                        L1[n1 - 1] = -L[n - 1]
                    else: # new orientation is incompatible ==> contradiction
                        self.orientation = ((2*self.b)*[0], (2*self.b)*[0], (2*self.b)*[0])
                        return False
                # elif n1 = P1(n) has not been oriented in any diagram yet, make inference from T1
                elif L[n1 - 1] == 0:
                    L1[n1 - 1] = o1
                    L[n1 - 1]  = o1
                    temp.add(n1)
                # now we know that L1[n - 1], L[n - 1], L[n1 - 1] all exist
                # elif inference from T1 would agree with previous inferences
                elif L[n1 - 1] == o1:
                    L1[n1 - 1] = o1
                # else new orientation is incompatible with existing ==> contradiction
                else:
                    self.orientation = ((2*self.b)*[0], (2*self.b)*[0], (2*self.b)*[0])
                    return False
                
                n2 = self._P2(n)
                o2 = -L2[n - 1]
                # if n has not been oriented in T2 yet, orient according to master list
                if o2 == 0:
                    L2[n - 1] = L[n - 1]
                    # now, make inferences about position n2 = P2(n)
                    if L[n2 - 1] == 0: # if n2 hasn't been oriented anywhere
                        L[n2 - 1] = -L[n - 1]
                        L2[n2 - 1] = -L[n - 1]
                        temp.add(n2)
                    elif L[n2 - 1] == -L[n - 1]: # if the new orientation is compatible
                        L2[n2 - 1] = -L[n - 1]
                    else: # new orientation is incompatible ==> contradiction
                        self.orientation = ((2*self.b)*[0], (2*self.b)*[0], (2*self.b)*[0])
                        return False
                # elif n2 = P2(n) has not been oriented in any diagram yet, make inference from T2
                elif L[n2 - 1] == 0:
                    L2[n2 - 1] = o2
                    L[n2 - 1]  = o2
                    temp.add(n2)
                # now we know that L2[n - 1], L[n - 1], L[n2 - 1] all exist
                # elif inference from T2 would agree with previous inferences
                elif L[n2 - 1] == o2:
                    L2[n2 - 1] = o2
                # else new orientation is incompatible with existing ==> contradiction
                else:
                    self.orientation = ((2*self.b)*[0], (2*self.b)*[0], (2*self.b)*[0])
                    return False
                
                n3 = self._P3(n)
                o3 = -L3[n - 1]
                # if n has not been oriented in T3 yet, orient according to master list
                if o3 == 0:
                    L3[n - 1] = L[n - 1]
                    # now, make inferences about position n3 = P3(n)
                    if L[n3 - 1] == 0: # if n3 hasn't been oriented anywhere
                        L[n3 - 1] = -L[n - 1]
                        L3[n3 - 1] = -L[n - 1]
                        temp.add(n3)
                    elif L[n3 - 1] == -L[n - 1]: # if the new orientation is compatible
                        L3[n3 - 1] = -L[n - 1]
                    else: # new orientation is incompatible ==> contradiction
                        self.orientation = ((2*self.b)*[0], (2*self.b)*[0], (2*self.b)*[0])
                        return False
                # elif n3 = P3(n) has not been oriented in any diagram yet, make inference from T3
                elif L[n3 - 1] == 0:
                    L3[n3 - 1] = o3
                    L[n3 - 1]  = o3
                    temp.add(n3)
                # now we know that L3[n - 1], L[n - 1], L[n3 - 1] all exist
                # elif inference from T3 would agree with previous inferences
                elif L[n3 - 1] == o3:
                    L2[n3 - 1] = o3
                # else new orientation is incompatible with existing ==> contradiction
                else:
                    self.orientation = ((2*self.b)*[0], (2*self.b)*[0], (2*self.b)*[0])
                    return False

            # update just_added to have new positions that were added in this iteration
            just_added.clear()
            just_added.update(temp)
            temp.clear()
        
        # now (L1, L2, L3) defines a coherent orientation of self
        self.orientation = (L1, L2, L3)
        return True

    # -> True if and only if self is orientable as a triplane diagram
    # NOTE: if needed, runs orient()
    def orientable(self) -> bool:
        if not self.orientation[0]: # if orientation has not been run yet,
            return self.orient()
        # checks if existing orientation is all zeros
        # all zeros ==> nonorientable
        return abs(self.orientation[0][0])

    # alias for orientable()
    def o(self) -> bool:
        return self.orientable()

    # -> the Euler characteristic of self
    def euler_characteristic(self) -> int:
        return (-self.b
                + link_components(self.T1[0], self.T1[1], self.T2[0], self.T2[1])
                + link_components(self.T2[0], self.T2[1], self.T3[0], self.T3[1])
                + link_components(self.T3[0], self.T3[1], self.T1[0], self.T1[1]))
    
    # alias for euler_characteristic()
    def chi(self) -> int:
        return self.euler_characteristic()
    
    # display the three tangles
    # currently only shows braids
    def show(self) -> None:
        self.T1[0].plot(color='red')
        self.T2[0].plot(color='blue')
        self.T3[0].plot(color='green')
