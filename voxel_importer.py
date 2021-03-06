import argparse
from io import TextIOWrapper
import json
import pathlib
from typing import Optional
import numpy as np
from .cube_step import Position, Voxel, cube_step


DEBUG = False

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
    if DEBUG:
        print()
    for x0, x1 in neighbors(0, LENX+2):
        for y0, y1 in neighbors(0, LENY+2):
            for z0, z1 in neighbors(0, LENZ+2):
                if DEBUG:
                    print(f'Polygonising chunk {i}/{TOTAL_CHUNKS}\u001b[1A')
                polygonise(x0, x1, y0, y1, z0, z1, _list)
                i += 1
    if DEBUG:
        print()
    TOTAL_VERTICES = len(VERTICES)


def save_obj(name: str, out: TextIOWrapper):
    out.write(f'o {name}\n')
    for v in VERTICES.keys():
        out.write(f'v {v}\n')
    for vn in VERTEX_NORMALS.keys():
        out.write(f'vn {vn}\n')
    for f in FACES:
        out.write(f'f {f[0][2]}//{f[1][2]} {f[0][1]}//{f[1][1]} {f[0][0]}//{f[1][0]}\n')


def main(infilepath: str, outfilepath: str, isomax: Optional[float] = None, isomin: Optional[float] = None):
    global ISOMAX, ISOMIN, LENX, LENY, LENZ, TOTAL_CHUNKS
    if isomax is not None:
        ISOMAX = isomax
    if isomin is not None:
        ISOMIN = isomin

    with open(infilepath) as f:
        injson = json.load(f)
    LENX, LENY, LENZ = injson['lenx'], injson['leny'], injson['lenz']
    TOTAL_CHUNKS = (LENX+1)*(LENY+1)*(LENZ+1)

    _list = pad_border(injson['data'])
    polygonise_all(_list)
    with open(outfilepath, 'w') as f:
        save_obj(outfilepath.split('/')[-1].split('\\')[-1], f)


parser = argparse.ArgumentParser(description='Voxel to triangles converter (using the marching cube algorithm).')
parser.add_argument('input', type=pathlib.Path,
    help='path to voxel data in internal JSON format')
parser.add_argument('output', type=pathlib.Path, nargs='?',
    help='path where output OBJ file should be stored')
parser.add_argument('--isomin', type=float, default=0.001,
    help='lower bound for the density of voxels visualized as an isosurface (default: %(default)s)')
parser.add_argument('--isomax', type=float, default=1.0,
    help='upper bound for the density of voxels visualized as an isosurface (default: %(default)s)')
parser.add_argument('--debug', type=bool, default=False,
    help='should chunk progress be printed out (default: %(default)s)')

if __name__ == "__main__":
    args = parser.parse_args()
    ISOMAX = args.isomax
    ISOMIN = args.isomin
    DEBUG = args.debug

    if args.output is None:
        args.output = pathlib.Path('.'.join(str(args.input.absolute()).split('.')[:-1] + ['obj']))
    main(str(args.input.absolute()), str(args.output.absolute()))
