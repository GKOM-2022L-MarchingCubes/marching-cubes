from io import TextIOWrapper
import numpy as np
import sys
import os.path
import json

def readlines(file: TextIOWrapper):
    templist = []
    for _ in range(11):
        file.readline()
    for line in file.readlines():
        x, y, z, c, _, _ = line.split()
        templist.append((int(x), int(y), int(z), int(c)))
    return templist


def convert(listv):
    numpylist = np.array(listv)
    minx, miny = np.min(numpylist[:,0], axis=0), np.min(numpylist[:,1], axis=0)
    maxx, maxy, maxz = np.max(numpylist[:,0], axis=0), np.max(numpylist[:,1], axis=0), np.max(numpylist[:,2], axis=0)
    offsets = (-minx, -miny)
    list3d = [[[0.0] * (1+maxz)] * (1+maxy-miny)] * (1+maxx-minx)
    for x, y, z, c in listv:
        list3d[x+offsets[0]][y+offsets[1]][z] = c / 256
    return list3d


for path in sys.argv[1:]:
    with open(path) as file:
        templist = readlines(file)
        list3d = convert(templist)
        with open(os.path.splitext(path)[0]+'.json', 'w') as out:
            json.dump(list3d, out)
