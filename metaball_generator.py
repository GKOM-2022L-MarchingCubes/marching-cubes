import json
import math
import sys
import numpy as np

def generate(size: int, inverted: bool) -> list[list[list[float]]]:
    metaball = np.zeros((size, size, size), dtype=np.float32)
    half_size = size / 2
    dist_center_squared = lambda value: (half_size - value)**2
    for x in range(size):
        for y in range(size):
            for z in range(size):
                divisor = math.sqrt(sum(map(dist_center_squared, [x, y, z])))
                metaball[x][y][z] = 1.0 / divisor if divisor != 0.0 else 1.0
    return metaball.tolist()

if __name__ == '__main__':
    if not 2 <= len(sys.argv) <= 3:
        print(f'Usage: {sys.argv[0]} [--inverted] size', file=sys.stderr)
        exit(-1)
    inverted = len(sys.argv) == 3
    size = int(sys.argv[-1])
    print(json.dumps({"lenx": size, "leny": size, "lenz": size, 'data': generate(size, inverted)}))
