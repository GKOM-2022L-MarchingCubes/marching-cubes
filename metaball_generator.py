import argparse
import json
import math
import sys
import numpy as np

def generate(size: int, inverted: bool) -> list[list[list[float]]]:
    metaball = np.zeros((size, size, size), dtype=np.float32)
    center = (size - 1) / 2
    dist_center_squared = lambda value: (center - value)**2
    for x in range(size):
        for y in range(size):
            for z in range(size):
                divisor = math.sqrt(sum(map(dist_center_squared, [x, y, z])))
                metaball[x][y][z] = 1.0 / divisor if divisor != 0.0 else 1.0
                if inverted:
                    metaball[x][y][z] = 1.0 - metaball[x][y][z]
    return metaball.tolist()


parser = argparse.ArgumentParser(description='Generator of 3D metaballs in a grid of given size.')
parser.add_argument('size', type=int,
    help='size of the output grid')
parser.add_argument('output', nargs='?', type=argparse.FileType('w'), default=sys.stdout,
    help='output file path')
parser.add_argument('--inverted', action='store_true',
    help='should the values be inverted (making density lower in the center)')

if __name__ == '__main__':
    args = parser.parse_args()
    args.output.write(json.dumps({"lenx": args.size, "leny": args.size, "lenz": args.size, 'data': generate(args.size, args.inverted)}))
