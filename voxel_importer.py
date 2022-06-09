import sys
import os.path
import numpy as np
import json
from cube_step import Position, Voxel, cube_step

RANGE = 1
# clockwise check, bottom first
NEIGHS = [(1,1,1),(1,-1,1),(-1,-1,1),(-1,1,1),
        (1,1,-1),(1,-1,-1),(-1,-1,-1),(-1,1,-1)]
SUBPOS = (3, 0, 1, 2, 7, 4, 5, 6)
ADJUST_LEFT = (1, 2, 5, 6)
ADJUST_RIGHT = (0, 3, 4, 7)
ADJUST_FOR = (2, 3, 6, 7)
ADJUST_BACK = (0, 1, 4, 5)
ADJUST_UP = (0, 1, 2, 3)
ADJUST_DOWN = (4, 5, 6, 7)

if __name__ == "__main__":
    for path in sys.argv[1:]:
        with open(path) as file:
            injson = json.load(file)
            lenx, leny, lenz, list3d = injson['lenx'], injson['leny'], injson['lenz'], injson['data']
            
            chunk_amount = int((lenx-1)*(leny-1)*(lenz-1))
            voxel_chunks: list[list[Voxel]] = np.empty((chunk_amount, 8)).tolist()
            for z, list2d in enumerate(list3d):
                for y, list1d in enumerate(list2d):
                    for x, density in enumerate(list1d):
                        vxl = Voxel(Position(RANGE*x/lenx, RANGE*y/leny, RANGE*z/lenz), density)
                        # magic, TODO explain later
                        
                        for offs, sub_chunk_pos in zip(NEIGHS, SUBPOS):
                            xoff, yoff, zoff = offs
                            if not (0 <= x + xoff <= lenx-1) or not (0 <= y + yoff <= leny-1) or not (0 <= z + zoff <= lenz-1):
                                continue

                            # grid snapped
                            vxl_chunk = 2*(x//2) + 2*(lenx//2)*(y//2) + 2*(lenx//2)*(leny//2)*(z//2)

                            # x adjust
                            vxl_chunk += 1 if x%2 == 1 and sub_chunk_pos in ADJUST_RIGHT else 0
                            vxl_chunk -= 1 if x%2 == 0 and sub_chunk_pos in ADJUST_LEFT else 0
                            # y adjust
                            vxl_chunk += (lenx//2) if y%2 == 1 and sub_chunk_pos in ADJUST_FOR else 0
                            vxl_chunk -= (lenx//2) if y%2 == 0 and sub_chunk_pos in ADJUST_BACK else 0
                            #z adjust
                            vxl_chunk += (lenx//2)*(leny//2) if z%2 == 1 and sub_chunk_pos in ADJUST_UP else 0
                            vxl_chunk -= (lenx//2)*(leny//2) if z%2 == 0 and sub_chunk_pos in ADJUST_DOWN else 0

                            voxel_chunks[vxl_chunk][sub_chunk_pos] = vxl
                            print(x,y,z)
                            print(vxl_chunk, sub_chunk_pos)
                        print()
            
            # march through chunks
            for i, chunk in enumerate(voxel_chunks):
                triangles = cube_step(chunk, i)
