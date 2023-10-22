
from LSH import lsh
import numpy as np
import pandas as pd

class Point:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y


class Rectangle:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)

    def area(self):
        return (self.x2 - self.x1) * (self.y2 - self.y1)

    def contains(self, point):
        return (point.x >= self.x1 and point.x <= self.x2 and point.y >= self.y1 and point.y <= self.y2)


    def intersects(self, range):
        return (self.x1 <= range.x2 and self.x2 >= range.x1 and self.y1 <= range.y2 and self.y2 >= range.y1)


class RTreeNode:
    def __init__(self, children, points):
        self.is_leaf = True
        self.children = children or []
        self.points = points or []
        x1 = min(point.x for point in self.points)
        y1 = min(point.y for point in self.points)
        x2 = max(point.x for point in self.points)
        y2 = max(point.y for point in self.points)
        self.rect = Rectangle(x1, y1, x2, y2)
        self.parentnode = None

    def area(self):
        return (self.rect.x2 - self.rect.x1) * (self.rect.y2 - self.rect.y1)

    def calculate_enlargement(self, point):
        new_area = (max(self.rect.x1 ,point.x) - min(self.rect.x2, point.x)) * ( max(self.rect.y1, point.y) - min(self.rect.y2, point.y))
        return new_area - self.area()

    def update_bounds(self):
        if not self.children:
            if self.points:
                x_coords = [point.x for point in self.points]
                y_coords = [point.y for point in self.points]
                self.rect.x1, self.rect.y1, self.rect.x2, self.rect.y2 = min(x_coords), min(y_coords), max(x_coords), max(y_coords)
            else:
                self.rect = None
        else:
            x1, y1, x2, y2 = self.children[0].rect.x1, self.children[0].rect.y1, self.children[0].rect.x2, self.children[0].rect.y2
            for child in self.children[1:]:
                x1, y1, x2, y2 = (min(x1, child.rect.x1), min(y1, child.rect.y1), max(x2, child.rect.x2), max(y2, child.rect.y2))
            self.rect.x1, self.rect.y1, self.rect.x2, self.rect.y2 = x1, y1, x2, y2

        if self.parentnode:
            self.parentnode.update_bounds()


    def search_rtree(self, range):
        results = []

        if not self.rect.intersects(range):
            return results

        if self.children:
            for c in self.children:
                results += c.search_rtree(range)
        else:
            for p in self.points:
                if range.contains(p):
                    results.append(p)

        return results


class RTree:
    def __init__(self, min_child=2, max_child=6):
        self.root = None
        self.min_child = min_child
        self.max_child = max_child

    def insert(self, point):
        
        if not self.root:
            self.root = RTreeNode(children=[], points=[point])
            return

        leaf_node = self._find_leaf_node(self.root, point)
        leaf_node.points.append(point)
        leaf_node.update_bounds()

        if len(leaf_node.points) > self.max_child:
            self.split_node(leaf_node)
            
    def _find_leaf_node(self, node, point):
        if node.is_leaf:
            return node
        index= self.find_best_child(node, point)
        return self._find_leaf_node(node.children[index], point)

    def split_node(self, node):
        if len(node.points) <= 6:
            return

        points = node.points
        points.sort(key=lambda point: point.x)
        median = len(points) // 2
        left = points[:median]
        right = points[median:]

        node1 = RTreeNode([], left)
        node2 = RTreeNode([], right)
        node1.parentnode = node
        node2.parentnode = node
        
        node.is_leaf = False
        node.children.append(node1)
        node.children.append(node2)

        node.points = []
        node.update_bounds()
        node1.update_bounds()
        node2.update_bounds()


    def find_best_child(self, node, point):
        if node.is_leaf:
            return node
        best_child = None
        min_enlargement = float("inf")
        for i, child in enumerate(node.children):
            enlargement = child.calculate_enlargement(point)
            if enlargement < min_enlargement:
                best_child = i
                min_enlargement = enlargement
        return best_child


def print_rtree(node, level=0):
    print(" " * level + "node, x1: {}, y1: {}, x2: {}, y2: {}".format(node.rect.x1, node.rect.y1, node.rect.x2, node.rect.y2))
    if node.is_leaf:
        for child in node.points:
            print(" " * (level + 2) + "Point id: {}, x: {}, y: {}".format(child.id, child.x, child.y))
    else:
        for child in node.children:
            print_rtree(child, level + 2)



df = pd.read_csv("data.csv")
dfres = df.copy()
df=df.drop(df.columns[[1]],axis=1)
df['SURNAME'] = df['SURNAME'].apply(lambda x: ord(x[0].lower()))
df=df.drop('EDUCATION',axis=1)

min_x,max_x = df["SURNAME"].agg(['min','max'])
min_y,max_y = df["AWARDS"].agg(['min','max'])

#print(min_x, min_y, max_x, max_y)

points = []
for index, row in df.iterrows():
    points.append(Point(index, row['SURNAME'], row['AWARDS']))

rtree = RTree(min_child=2, max_child=6)

for p in points:
    rtree.insert(p)




results = []

#print_rtree(rtree.root)

xmin = ord(input("Give first letter: ").lower())
xmax = ord(input("Give second letter: ").lower())

amin = int(input("Give minimum awards: "))
r = Rectangle(xmin, amin, xmax, max_y)
results = rtree.root.search_rtree(r)
print()
idlist = list()
for x in results:
    idlist.append(x.id)

dfres=dfres[dfres.index.isin(idlist)]

print(dfres)
lsh(dfres)

