# SUBDIVIDE IN 4
from math import sqrt
from LSH import lsh
import numpy as np
import pandas as pd
import time

class Point():  #asci prwto gramma kai award + id
    def __init__(self, x, y,id): 
        self.x = x
        self.y = y
        self.id = id
        self.education = "no"

    def distancefrom(self, point):
        return sqrt((self.x - point.x)**2 + (self.y - point.y)**2)

class Rectangle():
    def __init__(self, x0, y0, w, h):
        # (x0, y0) center of the rectangle
        #width, height HALF length
        self.x0 = x0
        self.y0 = y0
        self.w = w
        self.h = h

    def contains(self, point):
        return (point.x >= self.x0 - self.w and point.x <= self.x0 + self.w and point.y >= self.y0 - self.h and point.y <= self.y0 + self.h)

    def intersects(self, range):
        # range is a rectangle
        return not (range.x0 + range.w < self.x0 - self.w or range.x0 - range.w > self.x0 + self.w or range.y0 + range.h < self.y0 - self.h or range.y0 - range.h > self.y0 + self.h)

    
class QuadTree:
   
    def __init__(self, boundary):
        self.boundary = boundary  # borders
        self.points = []
        self.divided = False
        self.capacity = 4
        # subdivided quadtrees for this quadtree:
        self.nw = None
        self.ne = None
        self.sw = None
        self.se = None

              
    def subdivide(self):
        x = self.boundary.x0
        y = self.boundary.y0
        w = self.boundary.w / 2
        h = self.boundary.h / 2

        nw = Rectangle(x - w, y + h, w, h)
        self.nw = QuadTree(nw)
        ne = Rectangle(x + w, y + h, w, h)        
        self.ne = QuadTree(ne)

        sw = Rectangle(x - w, y - h, w, h)
        self.sw = QuadTree(sw)
        se = Rectangle(x + w, y - h, w, h)
        self.se = QuadTree(se)        
        self.divided = True


    def insert(self, point):

        if not self.boundary.contains(point):
            return
        
        if self.divided:
            self.nw.insert(point)
            self.ne.insert(point)
            self.sw.insert(point)
            self.se.insert(point)
            return

        if len(self.points) < self.capacity:
            self.points.append(point)
            return
        
        #if not divided
        self.subdivide()

        self.nw.insert(point)
        self.ne.insert(point)
        self.sw.insert(point)
        self.se.insert(point)
        for p in self.points:
            self.nw.insert(p)
            self.ne.insert(p)
            self.sw.insert(p)
            self.se.insert(p)
        self.points = []


    def query(self, range):
        found = []
        if not self.boundary.intersects(range):
            return found

        if self.divided:
            found += self.nw.query(range)
            found += self.ne.query(range)
            found += self.sw.query(range)
            found += self.se.query(range)
            return found

        else:
            for p in self.points:
                if range.contains(p):
                    found.append(p)
            return found


    def print_qtree(self):
        print()
        print(self.boundary.x0, self.boundary.y0, self.boundary.w,self.boundary.h  )
        
        if self.divided:
            self.nw.print_qtree()
            self.ne.print_qtree()
            self.sw.print_qtree()
            self.se.print_qtree()
        else:
            for p in self.points:
                print(f"({p.x}, {p.y})", end = " ")

#df = pd.read_csv("data.csv")
df = pd.read_csv("fake.csv")
dfres = df.copy()
df=df.drop(df.columns[[1]],axis=1)
df['SURNAME'] = df['SURNAME'].apply(lambda x: ord(x[0].lower()))
df=df.drop('EDUCATION',axis=1)

min_x,max_x = df["SURNAME"].agg(['min','max'])
min_y,max_y = df["AWARDS"].agg(['min','max'])


points = []

for index, row in df.iterrows():
    points.append(Point(row['SURNAME'], row['AWARDS'], index))


qboundary = Rectangle((max_x - min_x)/2 + min_x, (max_y-min_y)/2 + min_y, (max_x - min_x)/2, (max_y - min_y)/2)

creationTime = time.time()
qtree = QuadTree(qboundary)

for p in points:
    qtree.insert(p)

creationTime = time.time()-creationTime

print("The creation time for the tree is",creationTime)




results = []

xmin = ord(input("Give first letter: ").lower())
xmax = ord(input("Give second letter: ").lower())

amin = int(input("Give minimum awards: "))


queryTime = time.time()
qrange = Rectangle ((xmax - xmin)/2 + xmin, (max_y-amin)/2 + amin, (xmax - xmin)/2, (max_y - amin)/2)
results = qtree.query(qrange) 
queryTime = time.time() - queryTime

print("The query time for the tree is",queryTime)

#for p in results:
#    print(f"({p.x}, {p.y}, {p.id})", end = " ")

idlist = list()
for x in results:
    idlist.append(x.id)

dfres=dfres[dfres.index.isin(idlist)]

print(dfres)
lsh(dfres)
