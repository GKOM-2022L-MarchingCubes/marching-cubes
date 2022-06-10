from tables import edgeTable, triTable, verticesOfEdge
from typing import Optional

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
        if type(other) is Position:
            return Position(self.x + other.x, self.y + other.y, self.z + other.z)
        return Position(self.x + other, self.y + other, self.z + other)
    
    def __sub__(self, other):
        if type(other) is Position:
            return Position(self.x - other.x, self.y - other.y, self.z - other.z)
        return Position(self.x - other, self.y - other, self.z - other)

    def __mul__(self, other):
        if type(other) is Position:
            return Position(self.x * other.x, self.y * other.y, self.z * other.z)
        return Position(self.x * other, self.y * other, self.z * other)

    def __truediv__(self, other):
        if type(other) is Position:
            return Position(self.x / other.x, self.y / other.y, self.z / other.z)
        return Position(self.x / other, self.y / other, self.z / other)

    def __neg__(self):
        return Position(-self.x, -self.y, -self.z)
    
    def __str__(self):
        return f'{self.x} {self.y} {self.z}'

    def __repr__(self):
        return f'{self.x} {self.y} {self.z}'
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __hash__(self):
        return hash((self.x, self.y, self.z))


class Voxel:
    def __init__(self, position: Position, density: float, gradient: Position) -> None:
        self.position = position
        self.density = density
        self.gradient = gradient

    def __repr__(self):
        return f'Voxel(position: {self.position}, density: {self.density}, gradient: {self.gradient})'


Triangle = tuple[Position, Position, Position]


def cube_step(voxels: list[Voxel], isomin: float = 0.001, isomax: float = 1.0) -> list[list[tuple[Position, Position]]]:
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
    vertexData: list[Optional[tuple[Position, Position]]] = [None] * 12
    for i, bit in zip(range(12), BIGBITS):
        # find vertices of edge, interpolate position
        if edgesBits & bit:
            v1, v2 = verticesOfEdge[i]
            vertexData[i] = (interpolate(isomax, voxels[v1], voxels[v2]), interpolateGradient(isomax, voxels[v1], voxels[v2]))

    # Make as many triangles as necessary
    triangles: list[list[tuple[Position, Position]]] = []
    for i in range(0, 15, 3):
        if triTable[cubeIdx][i] == -1:
            break
        # Make a triangle out of three vertices
        triangle: list[tuple[Position, Position]] = []
        triangle.append(vertexData[triTable[cubeIdx][i]])
        triangle.append(vertexData[triTable[cubeIdx][i+1]])
        triangle.append(vertexData[triTable[cubeIdx][i+2]])
        triangles.append(triangle)
    return triangles


# Calculate the exact point of intersection in an edge based on density
# p = p1 + (p2 - p1) * ( (isomax - v1) / (v2 - v1) )
def interpolate(isomax: float, v1: Voxel, v2: Voxel) -> Position:
    assert abs(v1.density - v2.density) >= EPSILON
    if (abs(isomax - v1.density) < EPSILON):
        return v1.position
    if (abs(isomax - v2.density) < EPSILON):
        return v2.position
    m1 = abs(isomax - v2.density) / abs(v2.density - v1.density)
    m2 = abs(isomax - v1.density) / abs(v2.density - v1.density)
    return v1.position * m1 + v2.position * m2


# Calculate the gradient interpolated between two points based on density and then normalized
# (essentialy a vertex normal in the point of intersection)
def interpolateGradient(isomax: float, v1: Voxel, v2: Voxel) -> Position:
    assert abs(v1.density - v2.density) >= EPSILON
    m1 = abs(isomax - v2.density) / abs(v2.density - v1.density)
    m2 = abs(isomax - v1.density) / abs(v2.density - v1.density)
    interpolated = -(v1.gradient * m1 + v2.gradient * m2)
    length = (interpolated.x ** 2 + interpolated.y ** 2 + interpolated.z ** 2) ** 0.5
    if length > 0:
        interpolated = interpolated / length
    return interpolated
