#!/usr/bin/env python3
import attr

@attr.s
class Matrix(object):
    pass

@attr.s
class Coord(object):
    x = attr.ib(default=0)
    y = attr.ib(default=0)
    z = attr.ib(default=0)

@attr.s
class Bot(object): # nanobot
    bid = attr.ib()
    pos = attr.ib(factory=Coord)
    seeds = attr.ib(factory=list)

@attr.s
class State(object):
    energy = attr.ib(default=0)
    harmonics = attr.ib(default=False) # True == High, False == Low
    matrix = attr.ib(factory=Matrix)
    bots = attr.ib(factory=list)





