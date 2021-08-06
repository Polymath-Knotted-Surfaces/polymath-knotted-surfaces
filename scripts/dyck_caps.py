from itertools import product
from collections import deque
from functools import cache
from typing import NewType, List, Tuple, Dict, Generator


# Generate all Dyck words of length 2*num, recursively
# A Dyck word is a word like "(())()(()())"
@cache
def dyck(num: int, rcache: Dict[int, List[str]]={0: ['']}) -> List[str]:
    if num not in rcache:
        rcache[num] = [f'({t[0]}){str().join(t[1:])}' for i in range(1, num + 1)
			for t in product(dyck(i - 1), dyck(num - i))]
    return rcache[num]

def paren_idx_match(s:str, i:int, start: str='(', stop: str=')') -> int:
	# given a string and a starting index (and start character)
	# returns the index of the matching stop character 
    # If input is invalid.
    if s[i] != start:
        return -1
  
    # Create a deque to use it as a stack.
    d = deque()
 
    # Traverse through all elements
    # starting from i.
    for k in range(i, len(s)):
        # Pop a starting bracket
        # for every closing bracket
        if s[k] == stop:
            d.popleft()
        # Push all starting brackets
        elif s[k] == start:
            d.append(s[i])
        # If deque becomes empty
        if not d:
            return k
  
    return -1 #error return value
	
	
def dyck_to_caps(x: str) -> List[Tuple[int,...]]:
	# x is a dyck word of matched parthenteses.
	# returns the corresponding cap diagram to the dyck word.
	return [(i+1, paren_idx_match(x, i)+1) for i, s in enumerate(x) if s == "("]

def gen_caps(bridge:int) -> Generator[List[Tuple[int,...]], None, None]:
    return map(dyck_to_caps, dyck(bridge))