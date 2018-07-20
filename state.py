#!/usr/bin/env python3
from dataclasses import dataclass, astuple, field
from coord import Coord
from mrcrowbar.utils import to_uint64_be, unpack_bits

@dataclass
class Matrix(object):
    VOID = 0
    FILLED = 1
    GROUNDED = 2
    size: int = 0
    state: list = field(default_factory=list)
    # 0 = empty, 1 = filled, 2 = filled and grounded

    def coord_index(self, coord):
        return coord.x * self.size * self.size + coord.y * self.size + coord.z

    def __getitem__(self, key):
        return self.state[self.coord_index(key)]

    def __setitem__(self, key, value):
        self.state[self.coord_index(key)] = value

    def load(self, filename="problemsL/LA001_tgt.mdl"):
        bytedata = open(filename, 'rb').read()
        self.size = int(bytedata[0])
        for byte in bytedata[1:]:
            self.state.extend( to_uint64_be( unpack_bits( byte ) ) )

    def ground_adjacent(self, gc):
        for c in gc.adjacent(self.size):
            if self[c] == Matrix.FILLED:
                self[c] = Matrix.GROUNDED
                self.ground_adjacent(c)

    def calc_grounded(self):
        for x in range(0, self.size - 1):
            for z in range(0, self.size - 1):
                c = Coord(x,0,z)
                if self[c] == Matrix.FILLED:
                    self[c] = Matrix.GROUNDED
                    self.ground_adjacent(c)

@dataclass
class Bot(object): # nanobot
    bid: int
    pos: Coord
    seeds: list

@dataclass
class State(object):
    energy: int
    harmonics: bool # True == High, False == Low
    matrix: Matrix
    bots: list


def step(S, R):
    if S.harmonics == True:
        S.energy += 30 * R * R * R
    else:
        S.energy += 3 * R * R * R
    
    S.energy += 20 * len(S.bots)

def halt(S):
    if len(S.bots) > 1:
        raise Exception("Can't halt with more than one bot")

def wait(S):
    pass

def flip(S):
    S.harmonics = not S.harmonics

def find_bot(S, bid):
    for b in S.bots:
        if b.bid == bid:
            return b

def smove(S, bid, diff):
    b = find_bot(S, bid)
    b.pos += diff
    S.energy += 2 * diff.mlen()

def lmove(S, bid, diff1, diff2):
    b = find_bot(S, bid)
    b.pos += diff
    S.energy += 2 * (diff1.mlen() + 2 + diff2.mlen())

def fission(S, bid, nd, m):
    b = find_bot(s, bid)
    f = Bot(b.seeds[0], b.coord + nd, b.seeds[1:m+2])
    b.seeds = b.seeds[m+2:]
    S.bots.append(f)
    S.energy += 24

def is_grounded(S, p):
    return len([x for x in p.adjacent(S.matrix.size) if S.matrix[x]==2]) > 0

def fill(S, bid, nd):
    p = bid.coord + nd
    if S.matrix[p] == 0:
        S.matrix[p] = 2 if is_grounded(S, p) else 1
        S.energy += 12
    else:
        S.energy += 6

def fusion(S, prim, sec):
    S.bots = [b for b in S.bots if b.bid!=sec.bid]
    prim.seeds = prim.seeds + sec.seeds
    S.energy -= 24