import sys
import os.path
import json
from cube_step import Position, Voxel, cube_step

RANGE = 1

faces: list[tuple[int, int, int]] = []
vertex_to_idx: dict[Position, int] = {}

def store_trig(trig: list[Position]):
    idxs = []
    for vertex in trig:
        if vertex not in vertex_to_idx:
            vertex_to_idx[vertex] = len(vertex_to_idx.keys()) + 1
        idxs.append(vertex_to_idx[vertex])
    return idxs


def neighbors(start, stop):
  for i in range(start, stop - 1):
    yield (i, i+1)

if __name__ == "__main__":
    name = os.path.splitext(sys.argv[1])[0]
    isomax = 1.0
    isomin = 0.001
    if len(sys.argv) > 2:
        isomax = sys.argv[2]
    if len(sys.argv) > 3:
        isomin = sys.argv[3]

    with open(sys.argv[1]) as file, open(name+'.obj', 'w') as out:
        injson = json.load(file)
        lenx, leny, lenz, list3d = injson['lenx'], injson['leny'], injson['lenz'], injson['data']
        total_chunks = (lenx-1)*(leny-1)*(lenz-1)
        i = 1

        print()
        for x0, x1 in neighbors(0, lenx):
            for y0, y1 in neighbors(0, leny):
                for z0, z1 in neighbors(0, lenz):
                    v0 = Voxel(Position(RANGE*x0/(lenx-1), RANGE*y0/(leny-1), RANGE*z0/(lenz-1)), list3d[x0][y0][z0]) # 000
                    v1 = Voxel(Position(RANGE*x1/(lenx-1), RANGE*y0/(leny-1), RANGE*z0/(lenz-1)), list3d[x1][y0][z0]) # 100
                    v2 = Voxel(Position(RANGE*x1/(lenx-1), RANGE*y1/(leny-1), RANGE*z0/(lenz-1)), list3d[x1][y1][z0]) # 110
                    v3 = Voxel(Position(RANGE*x0/(lenx-1), RANGE*y1/(leny-1), RANGE*z0/(lenz-1)), list3d[x0][y1][z0]) # 010
                    v4 = Voxel(Position(RANGE*x0/(lenx-1), RANGE*y0/(leny-1), RANGE*z1/(lenz-1)), list3d[x0][y0][z1]) # 001
                    v5 = Voxel(Position(RANGE*x1/(lenx-1), RANGE*y0/(leny-1), RANGE*z1/(lenz-1)), list3d[x1][y0][z1]) # 101
                    v6 = Voxel(Position(RANGE*x1/(lenx-1), RANGE*y1/(leny-1), RANGE*z1/(lenz-1)), list3d[x1][y1][z1]) # 111
                    v7 = Voxel(Position(RANGE*x0/(lenx-1), RANGE*y1/(leny-1), RANGE*z1/(lenz-1)), list3d[x0][y1][z1]) # 011
                    chunk = [v0, v1, v2, v3, v4, v5, v6, v7]
                    print(f'Processing chunk {i}/{total_chunks}\u001b[1A')
                    triangles = cube_step(chunk, isomin, isomax)
                    for trig in triangles:
                        vidxs = store_trig(trig)
                        faces.append(vidxs)
                    i += 1

        out.write(f'o {name}\n')
        for v in vertex_to_idx.keys():
            out.write(f'v {v}\n')
        for f in faces:
            out.write(f'f {f[0]} {f[1]} {f[2]}\n')
