from LSH import lsh
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time


from collections import namedtuple
from operator import itemgetter
from pprint import pformat

class Node(namedtuple("Node", ["location","left_child","right_child"])):
    def __repr__(self):
        return pformat(tuple(self))

def kdtree(point_list, depth: int = 0):
    if not point_list:
        return None

    k = 2
    axis = depth % k +1

    # Sort point list by axis and choose median as pivot element
    point_list.sort(key=itemgetter(axis))
    median = len(point_list) // 2

    #print("median"+str(point_list[median])+"left_child"+str(point_list[:median])+"right_child"+str(point_list[median + 1 :]))
    # Create node and construct subtrees
    return Node(
        location=point_list[median],
        left_child=kdtree(point_list[:median], depth + 1),
        right_child=kdtree(point_list[median + 1 :], depth + 1),
    )

nodeList=list()

def search_range(root, minimum, maximum,awards):
    nodes = []

    def recursive_search(node,axis):
        
        if node is None:
            return None
        #print(node.location)
        if (minimum <= node.location[1] <= maximum) and node.location[2] >= awards:
                nodes.append(node.location)
        if axis==0:
            if node.location[1] >= minimum:
                recursive_search(node.left_child,1)
            if node.location[1] <= maximum:
                recursive_search(node.right_child,1)
        else:
            
            if node.location[2] >= awards:
               recursive_search(node.left_child,0)
               recursive_search(node.right_child,0)
            else:
                recursive_search(node.right_child,0)

    recursive_search(root,0)
    return nodes


        



# point_list = [(7, 2), (7, 2), (9, 6), (4, 7), (8, 1), (2, 3)]
# tree = kdtree(point_list)
#df = pd.read_csv("data.csv")
df = pd.read_csv("fake.csv")
dfres = df.copy()
df=df.drop(df.columns[[1]],axis=1)
df['SURNAME'] = df['SURNAME'].apply(lambda x: ord(x[0].lower()))
df=df.drop('EDUCATION',axis=1)

test= list(df.itertuples(index=True,name=None))

creationTime = time.time()
tree = kdtree(test)
creationTime = time.time()-creationTime

print("The creation time for the tree is",creationTime)

queryTime = time.time()
result = (search_range(tree,ord("a"),ord("z"),7))
queryTime = time.time() - queryTime

print("The query time for the tree is",queryTime)

#print((result))
idlist = list()
for x in result:
    idlist.append(x[0])

dfres=dfres[dfres.index.isin(idlist)]
#print(dfres)
lsh(dfres)
