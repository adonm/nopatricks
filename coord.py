from dataclasses import dataclass, astuple

@dataclass
class Coord:
    x: int
    y: int
    z: int

    def __add__(self, diff):
        return Coord(self.x + diff.dx, self.y + diff.dy, self.z + diff.dz)

    def __repr__(self):
        return astuple(self).__repr__()

    def adjacent_coords(self):
        adjs = [
            Diff(1, 0, 0),
            Diff(-1, 0, 0),
            Diff(0, 1, 0),
            Diff(0, -1, 0),
            Diff(0, 0, 1),
            Diff(0, 0, -1),
        ]
        return [self.add(d) for d in adjs]

# note: don't construct Diff objects directly; use diff() func to get correct subclass
def diff(dx, dy, dz):
    if clen(dx, dy, dz) == 1:
        if mlen(dx, dy, dz) <= 2:
            return NearDiff(dx, dy, dz)
    elif is_lcd(dx, dy, dz):
        m = mlen(dx, dy, dz)
        if m <= 5:
            return ShortDiff(dx, dy, dz)
        elif m <= 15:
            return LongDiff(dx, dy, dz)
    return Diff(dx, dy, dz)


def is_lcd(dx, dy, dz):
    return int(dx!=0) + int(dy!=0) + int(dz!=0) == 1

def mlen(dx, dy, dz):
    return abs(dx) + abs(dy) + abs(dz)

def clen(dx, dy, dz):
    return max(abs(dx), abs(dy), abs(dz))


@dataclass
class Diff:
    dx: int
    dy: int
    dz: int

    def mlen(self):
        return sum(map(abs, astuple(self)))

    def clen(self):
        return max(map(abs, astuple(self)))

    def __repr__(self):
        return f"<{self.dx}, {self.dy}, {self.dz}>"

# a linear coordinate difference has exactly one non-zero component
class LinearDiff(Diff):
    def __init__(self, dx, dy, dz):
        if int(dx!=0) + int(dy!=0) + int(dz!=0) != 1:
            raise ValueError(f"invalid lcd: <{dx}, {dy}, {dz}>")
        self.dx = dx
        self.dy = dy
        self.dz = dz

# ShortDiff is a linear coordinate difference with 0 < mlen <= 5
class ShortDiff(LinearDiff):
    pass

# LongDiff is a linear coordinate difference with 5 < mlen <= 15
class LongDiff(LinearDiff):
    pass

# NearDiff is a coordinate difference with one or two axes having 1 or -1 and the other 0
class NearDiff(Diff):
    pass
