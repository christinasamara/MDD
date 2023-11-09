from LSH import lsh
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time


from collections import namedtuple
from operator import itemgetter
from pprint import pformat

class Node(namedtuple("Node", ["location","left_child","right_child","ytree"])):
    def __repr__(self):
        return pformat(tuple(self))

def myFunc1(e):
  return e[1]
def myFunc2(e):
  return e[2]

def binaryTreeX(point_list):
    if not point_list:
        return None
    # Sort point list by axis and choose median as pivot element
    point_list.sort(key=myFunc1)
    median = len(point_list) // 2
    #print("sorted on 1"+str(point_list))
    #print("median"+str(point_list[median])+"left_child"+str(point_list[:median])+"right_child"+str(point_list[median + 1 :]))
    # Create node and construct subtrees
    #print(point_list)
    return Node(
        ytree=binaryTreeY(point_list[:]),
        location=point_list[median],
        left_child=binaryTreeX(point_list[:median]),
        right_child=binaryTreeX(point_list[median + 1 :]),       
        
    )

def binaryTreeY(point_list2):
    if not point_list2:
        return None
    # Sort point list by axis and choose median as pivot element
    point_list2.sort(key=myFunc2)    
    median2 = len(point_list2) // 2
    #print("sorted on 2"+str(point_list))
    # print(point_list[:median])
    # print(point_list[median])
    # print(point_list[median + 1 :])
    #print("median"+str(point_list[median])+"left_child"+str(point_list[:median])+"right_child"+str(point_list[median + 1 :]))
    # Create node and construct subtrees
    return Node(
        ytree=None,
        location=point_list2[median2],
        left_child=binaryTreeY(point_list2[:median2]),
        right_child=binaryTreeY(point_list2[median2 + 1 :]),
        
    )




def printTree(tree, level=0):
    print ('\t' * level + str(tree.location))
    if (tree.left_child):
        printTree(tree.left_child,level+1)
    if (tree.right_child):
        printTree(tree.right_child,level+1)
    
def search_range(root, minimum, maximum,awards):
    nodes = []
    def recursive_searchY(node):        
        if node is None:
            return None

        #print(node.location)
        if (minimum <= node.location[1] <= maximum) and node.location[2] >= awards:
            nodes.append(node.location)

        if node.location[2] >= awards:
            recursive_searchY(node.left_child)        
        recursive_searchY(node.right_child)

    def findSplitNode(node):        
        if node is None:
            return None

        #print(node.location)
        if (minimum <= node.location[1] <= maximum):
            if node.location[2] >= awards:
                nodes.append(node.location)

            recursive_searchXmin(node.left_child)
            recursive_searchXmax(node.right_child)
        else:    
            if node.location[1] >= minimum:
                findSplitNode(node.left_child)
            if node.location[1] <= maximum:
                findSplitNode(node.right_child)

    def recursive_searchXmin(node):        
        if node is None:
            return None

        if (minimum <= node.location[1] <= maximum) and node.location[2] >= awards:
            nodes.append(node.location)

        if (minimum <= node.location[1]):
            recursive_searchXmin(node.left_child)
            if node.right_child != None:
                recursive_searchY(node.right_child.ytree)
        else:    
            recursive_searchXmin(node.right_child)

    def recursive_searchXmax(node):        
        if node is None:
            return None

        if (minimum <= node.location[1] <= maximum) and node.location[2] >= awards:
            nodes.append(node.location)

        if (maximum >= node.location[1]):
            recursive_searchXmax(node.right_child)
            if node.left_child != None:
                recursive_searchY(node.left_child.ytree)
        else:    
            recursive_searchXmax(node.left_child)    

    findSplitNode(root)
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
tree = binaryTreeX(test)
creationTime = time.time()-creationTime

print("The creation time for the tree is",creationTime)

queryTime = time.time()

result = (search_range(tree,ord("a"),ord("c"),0))
queryTime = time.time() - queryTime

print("The query time for the tree is",queryTime)

print(result)
idlist = list()
for x in result:
    idlist.append(x[0])

dfres=dfres[dfres.index.isin(idlist)]
print((dfres))
lsh(dfres)
