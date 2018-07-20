#!/usr/bin/env python3
from dataclasses import dataclass, astuple
from coord import Coord

@dataclass
class Matrix(object):
    size: int
    coords: list

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

