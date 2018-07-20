#!/usr/bin/env python3
from dataclasses import dataclass, astuple
from coord import Coord

@dataclass
class Voxel(object):
    coord: Coord
    full: bool
    grounded: bool

@dataclass
class Matrix(object):
    size: int
    voxels: list

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

