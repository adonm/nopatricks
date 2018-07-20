#!/usr/bin/env python3
from dataclasses import dataclass, astuple, field
from coord import Coord
from mrcrowbar.utils import to_uint64_be, unpack_bits

@dataclass
class Matrix(object):
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

