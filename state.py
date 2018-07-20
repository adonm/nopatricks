#!/usr/bin/env python3
from dataclasses import dataclass, astuple
from coord import Coord

@dataclass
class Matrix(object):
    size: int
    coords: list
    filled_coords: list

    def load(self, filename):
        bytedata = open("problemsL/LA001_tgt.mdl", 'rb').read()
        self.size = int(bytedata[0])
        for byte in bytedata[1:]:
            for digit in "{0:08b}".format(byte):
                self.filled_coords.append(digit)

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

