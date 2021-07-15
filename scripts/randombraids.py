import pandas as pd
from snappy import *
from cytoolz import *
from braidgenerator import *
import spherogram as s
import multiprocessing as m

def genBraids(startingBraid:list[int]=[1,2,-2,-1], numStrands:int=8, numBraids:int=1000, maxLen:int=10, numSteps:int=10) -> pd.DataFrame:
    try:
        assert (numStrands > 2) and maxLen > 3
    except:
        print("invalid parameters.")
    data = dict()
    for i in range(3,maxLen+1):
        x = MarkovChain(braidword=[1,2,-2-1], maxgen=numStrands, maxlen=i)
        res = None #Loop until it works. Random algorithms are weird!
        while res is None:
            try:
                x.model(num_braidreps=numBraids, msteps=numSteps)
                res = True
            except:
                pass
        data[i] = pd.Series(x.braidreps()).map(lambda b: b.word)
    bs = ( pd.DataFrame([(k, v) for k in data.keys() for v in data[k]], columns=["length", "braid"])
         .assign(braid = lambda df: df.braid.map(lambda v: tuple(filter(lambda z: z!=0, v)))) #removes trivial letters 0 = id and convers to tuples, which are hashable
         .drop_duplicates('braid')  #Drop duplicate entries.
         .assign(braid = lambda df: df.braid.map(list)) #convert back to lists (ie words)
         .assign(braid = lambda df: df.braid.replace(to_replace=[],value=pd.NA)) #replace empty braids with NA
         .dropna() # drop empty braids
         .sort_values(by="length", ascending=False) #sort by lengthof braid, descending
         .reset_index(drop=True) #reset the indexing to be nice.
         )
    return bs