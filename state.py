#!/usr/bin/env python3
from dataclasses import dataclass, astuple
from coord import Coord
from mrcrowbar.utils import to_uint64_be, unpack_bits


@dataclass
class Voxel(object):
    coord: Coord
    full: bool
    grounded: bool

@dataclass
class Matrix(object):
    size: int
    coords: list
    filled_coords: list
    voxels: list

    def load(self, filename):
        bytedata = open("problemsL/LA001_tgt.mdl", 'rb').read()
        self.size = int(bytedata[0])
        for byte in bytedata[1:]:
            self.filled_coords.extend( to_uint64_be( unpack_bits( byte ) ) )

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

