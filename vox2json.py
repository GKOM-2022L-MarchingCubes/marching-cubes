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
        x, y, z, density, _, _ = line.split()
        templist.append((int(x), int(y), int(z), int(density)))
    return templist


def convert(listv):
    numpylist = np.array(listv)
    minx, miny = np.min(numpylist[:,0], axis=0), np.min(numpylist[:,1], axis=0)
    maxx, maxy, maxz = np.max(numpylist[:,0], axis=0), np.max(numpylist[:,1], axis=0), np.max(numpylist[:,2], axis=0)
    lenx, leny, lenz = int(1+maxx-minx), int(1+maxy-miny), int(1+maxz)
    offsets = (-minx, -miny)
    list3d = np.empty((lenx, leny, lenz)).tolist()
    for x, y, z, density in listv:
        list3d[x+offsets[0]][y+offsets[1]][z] = density / 256
    return {'lenx': lenx, 'leny': leny, 'lenz': lenz, 'data': list3d}


if __name__ == "__main__":
    for path in sys.argv[1:]:
        with open(path) as file:
            templist = readlines(file)
            outjson = convert(templist)
            with open(os.path.splitext(path)[0]+'.json', 'w') as out:
                json.dump(outjson, out)
