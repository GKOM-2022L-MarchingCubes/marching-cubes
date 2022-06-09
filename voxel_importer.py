import sys
import os.path
import numpy as np
import json
from cube_step import Position, Voxel, cube_step

RANGE = 1


def neighbors(start, stop):
  for i in range(start, stop - 1):
    yield (i, i+1)

if __name__ == "__main__":
    for path in sys.argv[1:]:
        with open(path) as file:
            injson = json.load(file)
            lenx, leny, lenz, list3d = injson['lenx'], injson['leny'], injson['lenz'], injson['data']

            for x0, x1 in neighbors(0, lenx):
                for y0, y1 in neighbors(0, leny):
                    for z0, z1 in neighbors(0, lenz):
                        v0 = Voxel(Position(RANGE*x0/lenx, RANGE*y0/leny, RANGE*z0/lenz), list3d[x0][y0][z0])
                        v1 = Voxel(Position(RANGE*x0/lenx, RANGE*y0/leny, RANGE*z1/lenz), list3d[x0][y0][z1])
                        v2 = Voxel(Position(RANGE*x0/lenx, RANGE*y1/leny, RANGE*z0/lenz), list3d[x0][y1][z0])
                        v3 = Voxel(Position(RANGE*x0/lenx, RANGE*y1/leny, RANGE*z1/lenz), list3d[x0][y1][z1])
                        v4 = Voxel(Position(RANGE*x1/lenx, RANGE*y0/leny, RANGE*z0/lenz), list3d[x1][y0][z0])
                        v5 = Voxel(Position(RANGE*x1/lenx, RANGE*y0/leny, RANGE*z1/lenz), list3d[x1][y0][z1])
                        v6 = Voxel(Position(RANGE*x1/lenx, RANGE*y1/leny, RANGE*z0/lenz), list3d[x1][y1][z0])
                        v7 = Voxel(Position(RANGE*x1/lenx, RANGE*y1/leny, RANGE*z1/lenz), list3d[x1][y1][z1])
                        chunk = [v0, v1, v2, v3, v4, v5, v6, v7]

                        triangles = cube_step(chunk)
                        print(triangles)
