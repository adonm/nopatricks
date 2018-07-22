#!/usr/bin/env python3
from dataclasses import dataclass
from enum import Enum

class Axis(Enum):
    X = 1
    Y = 2
    Z = 3

    def get(self, obj):
        return (obj.x, obj.y, obj.z)[self.value - 1]

@dataclass
class Coord:
    x: int
    y: int
    z: int

    def __add__(self, diff):
        return Coord(self.x + diff.dx, self.y + diff.dy, self.z + diff.dz)

    def __multiply__(self, m):
        return Coord(self.x * m, self.y * m, self.z * m)

    def __sub__(self, other):
        if isinstance(other, Coord):
            return diff(self.x - other.x, self.y - other.y, self.z - other.z)
        elif isinstance(other, Diff):
            return self + -other

    def __len__(self):
        return 3

    def __getitem__(self, key):
        return (self.x, self.y, self.z)[key]

    def __repr__(self):
        return (self.x, self.y, self.z).__repr__()

    def __hash__(self):
        return hash((self.x, self.y, self.z))
    
    def adjacent(self, R):
        x,y,z = self.x,self.y,self.z
        adjs = [Coord(x+1,y,z), Coord(x-1,y,z), Coord(x,y+1,z), Coord(x,y-1,z), Coord(x,y,z+1), Coord(x,y,z-1)]
        if x>1 and y>1 and z>1 and x<R-1 and y<R-1 and z<R-1:
            return adjs
        else:
            return [a for a in adjs if a.x>=0 and a.y>=0 and a.z>=0 and a.x<R and a.y<R and a.z<R]
    
    def near(self, R):
        diffs = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                for z in range(-1, 2):
                    if x==0 and y==0 and z==0:
                        pass
                    elif abs(x)==1 and abs(y)==1 and abs(z)==1:
                        pass
                    else:
                        diffs.push(x, y, z)

def is_lcd(dx, dy, dz):
    idx = int(dx!=0)
    idy = int(dy!=0)
    idz = int(dz!=0)
    if idx + idy + idz == 1:
        if idx == 1:
            return Axis.X
        elif idy == 1:
            return Axis.Y
        else: # idz == 1
            return Axis.Z
    return None

def mlen(dx, dy, dz):
    return abs(dx) + abs(dy) + abs(dz)

def clen(dx, dy, dz):
    return max(abs(dx), abs(dy), abs(dz))


@dataclass
class Diff:
    dx: int
    dy: int
    dz: int

    def is_manhatten(self):
        n = 0
        if abs(self.dx)>5 or abs(self.dy)>5 or abs(self.dz)>5:
            return False
            
        if self.dx != 0:
            n+=1
        if self.dy != 0:
            n+=1
        if self.dz != 0:
            n+=1 
        return n==1

    def magnitude_sqrd(self):
        return self.dx*self.dx + self.dy*self.dy + self.dz*self.dz

    def mlen(self):
        return sum(map(abs, (self.dx, self.dy, self.dz)))

    def clen(self):
        return max(map(abs, (self.dx, self.dy, self.dz)))

    def __repr__(self):
        return f"<{self.dx}, {self.dy}, {self.dz}>"

# a linear coordinate difference has exactly one non-zero component
class LinearDiff(Diff):
    axis: Axis

    def __init__(self, dx, dy, dz):
        self.axis = is_lcd(dx, dy, dz)
        if self.axis is None:
            raise ValueError(f"invalid lcd: <{dx}, {dy}, {dz}>")
        super().__init__(dx, dy, dz)

    def __neg__(self):
        return LinearDiff(-self.dx, -self.dy, -self.dz)

# ShortDiff is a linear coordinate difference with 0 < mlen <= 5
class ShortDiff(LinearDiff):
    def __init__(self, dx, dy, dz):
        if mlen(dx, dy, dz) > 5:
            raise ValueError(f"invalid sld: <{dx}, {dy}, {dz}>")
        super().__init__(dx, dy, dz)

    def __add__(self, d):
        return diff(self.dx + d.dx, self.dy + d.dy, self.dz + d.dz)

    def __neg__(self):
        return ShortDiff(-self.dx, -self.dy, -self.dz)

# LongDiff is a linear coordinate difference with 5 < mlen <= 15
class LongDiff(LinearDiff):
    def __init__(self, dx, dy ,dz):
        if mlen(dx, dy, dz) > 15:
            raise ValueError(f"invalid lld: <{dx}, {dy}, {dz}>")
        super().__init__(dx, dy, dz)

    def __neg__(self):
        return LongDiff(-self.dx, -self.dy ,-self.dz)

# NearDiff is a coordinate difference with one or two axes having 1 or -1 and the other 0
class NearDiff(Diff):
    def __init__(self, dx, dy, dz):
        if clen(dx, dy, dz) > 1 or mlen(dx, dy, dz) > 2:
            raise ValueError(f"invalid nd: <{dx}, {dy}, {dz}>")
        self.dx = dx
        self.dy = dy
        self.dz = dz

    def __add__(self, d):
        return diff(self.dx + d.dx, self.dy + d.dy, self.dz + d.dz)

    def mul(self, m):
        return NearDiff(self.dx * m, self.dy * m, self.dz * m)

    def __neg__(self):
        return NearDiff(-self.dx, -self.dy, -self.dz)

@dataclass
class Line:
    c1: Coord
    c2: Coord
    axis: Axis

    def __init__(self, c1, c2):
        diff = c1 - c2
        if not isinstance(diff, LinearDiff):
            raise ValueError(f"invalid line: [{c1}, {c2}]")
        self.c1 = c1
        self.c2 = c2
        self.axis = diff.axis

    def __repr__(self):
        return f"[{self.c1}, {self.c2}]"

    def contains(self, coord):
        def within(axis):
            val = axis.get(coord)
            lower, upper = minmax(axis.get(self.c1), axis.get(self.c2))
            return lower <= val and val <= upper

        return within(Axis.X) and within(Axis.Y) and within(Axis.Z)


def minmax(a, b):
    if a > b:
        return b, a
    return a, b


# note: don't construct Diff objects directly; use diff() func to get correct subclass
def diff(dx, dy, dz):
    c = clen(dx, dy, dz)
    if c == 0:
        return Diff(0, 0, 0)
    elif c == 1:
        if mlen(dx, dy, dz) <= 2:
            return NearDiff(dx, dy, dz)
    elif is_lcd(dx, dy, dz):
        m = mlen(dx, dy, dz)
        if m <= 5:
            return ShortDiff(dx, dy, dz)
        elif m <= 15:
            return LongDiff(dx, dy, dz)
        return LinearDiff(dx, dy, dz)
    return Diff(dx, dy, dz)


UP = diff(0, 1, 0)
DOWN = diff(0, -1, 0)
LEFT = diff(1, 0, 0)
RIGHT = diff(-1, 0, 0)
FORWARD = diff(0, 0, 1)
BACK = diff(0, 0, -1)
