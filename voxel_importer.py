from io import TextIOWrapper
import sys
import math
import os.path
import json
import numpy as np
from cube_step import Position, Voxel, cube_step
from typing import Optional


# constants
RANGE = 1
# globals
LENX = 0
LENY = 0
LENZ = 0
TOTAL_CHUNKS = 0
TOTAL_VERTICES = 0
ISOMAX = 1.0
ISOMIN = 0.001
#                vertices ids         vertex normals ids
FACES: list[tuple[tuple[int, int, int], tuple[int, int, int]]] = []
# vertices positions
VERTICES: dict[Position, int] = {}
# reverse map
RE_VERTICES: list[Optional[int]] = [None]
# vertex normals positions
VERTEX_NORMALS: dict[Position, int] = {}
# types
list3d = list[list[list[float]]]

def store_trig(trig: list[Position]) -> tuple[int, int, int]:
    global VERTICES
    idxs = []
    for vertex in trig:
        if vertex not in VERTICES:
            VERTICES[vertex] = len(VERTICES.keys()) + 1
            RE_VERTICES.append(VERTICES[vertex])
        idxs.append(VERTICES[vertex])
    return tuple(idxs)


def store_trig_normals(trig: list[Position]) -> tuple[int, int, int]:
    global VERTEX_NORMALS
    idxs = []
    for normal in trig:
        if normal not in VERTEX_NORMALS:
            VERTEX_NORMALS[normal] = len(VERTEX_NORMALS.keys()) + 1
        idxs.append(VERTEX_NORMALS[normal])
    return tuple(idxs)


def neighbors(start, stop):
  for i in range(start, stop - 1):
    yield (i, i+1)


def pad_border(_list: list3d) -> list3d:
    nump = np.zeros((LENX+2, LENY+2, LENZ+2))
    for x in range(1, LENX+1):
        for y in range(1, LENY+1):
            for z in range(1, LENZ+1):
                nump[x][y][z] = _list[x-1][y-1][z-1]
    return nump.tolist()


def make_voxel(x: int, y: int, z: int, _list: list3d):
    return Voxel(
        Position(RANGE*x/(LENX-1), RANGE*y/(LENY-1), RANGE*z/(LENZ-1)),
        _list[x][y][z],
        calc_gradient(x, y, z, _list)
    )

def calc_gradient(x: int, y: int, z: int, _list: list3d) -> Position:
    return Position(
        (_list[x + 1][y][z] if x < LENX + 1 else 0.0) - (_list[x - 1][y][z] if x > 0 else 0.0),
        (_list[x][y + 1][z] if y < LENY + 1 else 0.0) - (_list[x][y - 1][z] if y > 0 else 0.0),
        (_list[x][y][z + 1] if z < LENZ + 1 else 0.0) - (_list[x][y][z - 1] if z > 0 else 0.0)
    )

def polygonise(x0, x1, y0, y1, z0, z1, _list: list3d):
    global FACES
    v0 = make_voxel(x0, y0, z0, _list) # 000
    v1 = make_voxel(x1, y0, z0, _list) # 100
    v2 = make_voxel(x1, y1, z0, _list) # 110
    v3 = make_voxel(x0, y1, z0, _list) # 010
    v4 = make_voxel(x0, y0, z1, _list) # 001
    v5 = make_voxel(x1, y0, z1, _list) # 101
    v6 = make_voxel(x1, y1, z1, _list) # 111
    v7 = make_voxel(x0, y1, z1, _list) # 011
    chunk = [v0, v1, v2, v3, v4, v5, v6, v7]
    
    triangles = cube_step(chunk, ISOMIN, ISOMAX)
    for trig in triangles:
        vidxs = store_trig([x[0] for x in trig])
        nidxs = store_trig_normals([x[1] for x in trig])
        FACES.append((vidxs, nidxs))


def polygonise_all(_list: list3d):
    global TOTAL_VERTICES
    i = 1
    for x0, x1 in neighbors(0, LENX+2):
        for y0, y1 in neighbors(0, LENY+2):
            for z0, z1 in neighbors(0, LENZ+2):
                print(f'Polygonising chunk {i}/{TOTAL_CHUNKS}\u001b[1A')
                polygonise(x0, x1, y0, y1, z0, z1, _list)
                i += 1
    TOTAL_VERTICES = len(VERTICES)


def save_obj(out: TextIOWrapper):
    global VERTICES
    global FACES
    out.write(f'o {name}\n')
    for v in VERTICES.keys():
        out.write(f'v {v}\n')
    for vn in VERTEX_NORMALS.keys():
        out.write(f'vn {vn}\n')
    for f in FACES:
        out.write(f'f {f[0][2]}//{f[1][2]} {f[0][1]}//{f[1][1]} {f[0][0]}//{f[1][0]}\n')


if __name__ == "__main__":
    name = os.path.splitext(sys.argv[1])[0]
    if len(sys.argv) > 2:
        ISOMAX = float(sys.argv[2])
    if len(sys.argv) > 3:
        ISOMIN = float(sys.argv[3])

    with open(sys.argv[1]) as file, open(name+'.obj', 'w') as out:
        injson = json.load(file)
        _list: list3d
        LENX, LENY, LENZ = injson['lenx'], injson['leny'], injson['lenz']
        TOTAL_CHUNKS = (LENX+1)*(LENY+1)*(LENZ+1)
        _list = pad_border(injson['data'])

        print()
        polygonise_all(_list)
        save_obj(out)
