import argparse
from io import TextIOWrapper
import json
import os.path
import pathlib
import numpy as np

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
    list3d = np.zeros((lenx, leny, lenz)).tolist()
    for x, y, z, density in listv:
        list3d[x+offsets[0]][y+offsets[1]][z] = density / 256
    return {'lenx': lenx, 'leny': leny, 'lenz': lenz, 'data': list3d}


def main(inpath: str, outpath: str):
    with open(inpath) as file:
        templist = readlines(file)
    outjson = convert(templist)
    with open(os.path.splitext(outpath)[0]+'.json', 'w') as out:
        json.dump(outjson, out)


parser = argparse.ArgumentParser(description='Voxel format converter.')
parser.add_argument('input', type=pathlib.Path,
    help='path to voxel data (stored as a point cloud) in PLY format')
parser.add_argument('output', type=pathlib.Path, nargs='?',
    help='path where output voxel data (in internal JSON format) should be stored')

if __name__ == "__main__":
    args = parser.parse_args()
    if args.output is None:
        args.output = pathlib.Path('.'.join(str(args.input.absolute()).split('.')[:-1] + ['obj']))
    main(str(args.input.absolute()), str(args.output.absolute()))
