from tables import edgeTable, triTable, verticesOfEdge

# 1, 2, 4, ..., 128
BITS = [2**i for i in range(8)]
# ditto for up to 2048
BIGBITS = [2**i for i in range(12)]
# floating point equality test epsilon
EPSILON = 1e-5

# types
class Position:
    def __init__(self, x, y, z) -> None:
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Position(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        return Position(self.x * other.x, self.y * other.y, self.z * other.z)

    def __div__(self, other):
        return Position(self.x / other.x, self.y / other.y, self.z / other.z)
    
    def __str__(self):
        return f'{self.x} {self.y} {self.z}'

    def __repr__(self):
        return f'{self.x} {self.y} {self.z}'
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __hash__(self):
        return hash((self.x, self.y, self.z))


class Voxel:
    def __init__(self, position, density) -> None:
        self.position = position
        self.density = density


Triangle = tuple[Position, Position, Position]


def cube_step(voxels: list[list[Voxel]], isomin: float = 0.001, isomax: float = 1.0) -> list[list[Position]]:
    # check which voxel is between the min and max, apply bitflag
    # cubeIdx will be between 0 and 255
    cubeIdx = 0
    for sample, bit in zip(voxels, BITS):
        if (isomin <= sample.density <= isomax):
            cubeIdx |= bit

    # then look up which edges are intersecting with our isosurface
    # if there's no intersection, quit
    edgesBits = edgeTable[cubeIdx]
    if (edgesBits == 0):
        return []
    vertexPositions: list[Position] = [None] * 12
    for i, bit in zip(range(12), BIGBITS):
        # find vertices of edge, interpolate position
        if edgesBits & bit:
            v1, v2 = verticesOfEdge[i]
            vertexPositions[i] = interpolate(isomax, voxels[v1], voxels[v2])

    # Make as many triangles as necessary
    triangles: list[list[Position]] = []
    for i in range(0, 15, 3):
        if triTable[cubeIdx][i] == -1:
            break
        # Make a triangle out of three vertices
        triangle: list[Position] = []
        triangle.append(vertexPositions[triTable[cubeIdx][i]])
        triangle.append(vertexPositions[triTable[cubeIdx][i+1]])
        triangle.append(vertexPositions[triTable[cubeIdx][i+2]])
        triangles.append(triangle)
    return triangles


# Calculate the exact point of intersection in an edge based on density
# p = p1 + (p2 - p1) * ( (isomax - v1) / (v2 - v1) )
def interpolate(isomax: float, v1: Voxel, v2: Voxel) -> Position:
    if (abs(isomax - v1.density) < EPSILON):
        return v1.position
    if (abs(isomax - v2.density) < EPSILON):
        return v2.position
    if (abs(v1.density - v2.density) < EPSILON):
        return v1.position
    #x: float = (isomax - v1.density) * abs(v2.density - v1.density)
    x: float = 0.5
    return v1.position + Position(x, x, x) * (v2.position - v1.position)
