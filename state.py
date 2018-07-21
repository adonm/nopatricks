#!/usr/bin/env python3
from dataclasses import dataclass, astuple, field
from coord import Coord
from mrcrowbar.utils import to_uint64_le, unpack_bits
import commands

class Voxel:
    """ Voxel represents mutable location information """

    # current implementation is a bitmask held in an int
    # the first few bits are the filled state
    VOID = 0
    FULL = 1
    GROUNDED = 2

    # the model bit is on if this location forms part of the target model
    MODEL = 1 << 7

    def __init__(self, val):
        self.val = val

    @staticmethod
    def empty(is_model=False):
        """ Initialises an empty voxel which is part of the model or not. """
        if is_model:
            return Voxel(Voxel.MODEL)
        return Voxel(Voxel.VOID)

    # access to state is via functions so the implementation is free to change
    def is_void(self):
        return not self.val & Voxel.FULL

    def is_full(self):
        return self.val & Voxel.FULL

    def is_grounded(self):
        return self.val & Voxel.GROUNDED

    def is_model(self):
        return self.val & Voxel.MODEL

    def set_grounded(self):
        assert self.val & Voxel.FULL
        self.val |= Voxel.GROUNDED

    def set_full(self):
        assert not (self.val & Voxel.FULL)
        self.val |= Voxel.FULL

    def __repr__(self):
        c1 = "_" if self.is_void() else "Ö" if self.is_grounded() else "O"
        c2 = "+" if self.is_model() else "_"
        return c1 + c2


class Matrix(object):
    """ Matrix(size=R) initialises an empty matrix
        Matrix(problem=N) loads problem N
        Matrix(filename="foo.mdl") loads model file"""

    def __init__(self, **kwargs):
        self.ungrounded = set()
        if 'size' in kwargs:
            self.size = kwargs['size']
            self.state = [Voxel.empty() for i in range(self.size ** 3)]
        elif 'filename' in kwargs:
            self.size, self.state = Matrix._load_file(kwargs['filename'])
        else:
            self.size, self.state = Matrix._load_prob(kwargs.get('problem', 1))

    @staticmethod
    def _load_prob(num):
        return Matrix._load_file("problemsL/LA%03d_tgt.mdl" % num)

    @staticmethod
    def _load_file(filename):
        bytedata = open(filename, 'rb').read()
        size = int(bytedata[0])
        state = []
        for byte in bytedata[1:]:
            for bit in to_uint64_le( unpack_bits( byte ) ):
                state.append(Voxel.empty(bit))
        return size, state

    def coord_index(self, coord):
        return coord.x * self.size * self.size + coord.y * self.size + coord.z

    def __getitem__(self, key):
        return self.state[self.coord_index(key)]

    def __setitem__(self, key, value):
        self.state[self.coord_index(key)] = value

    def ground_adjacent(self, gc):
        stack = [gc]
        while len(stack) > 0:
            g = stack.pop()
            for v in [x for x in g.adjacent(self.size) if self[x].is_full()]:
                self[v].set_grounded()
                ungrounded.remove(v)
                stack.push(v)
        
    def calc_grounded(self):
        stack = []
        for x in range(0, self.size - 1):
            for z in range(0, self.size - 1):
                c = Coord(x,0,z)
                if self[c].is_full():
                    self[c].set_grounded()
                    self.ground_adjacent(c)

    def would_be_grounded(self, p):
        return len([x for x in p.adjacent(self.size) if self[x].is_grounded()]) > 0

    def yplane(self, y):
        """ Returns a view into this matrix at a constant y """
        return MatrixPlane(self, y=y)


class MatrixPlane:
    def __init__(self, matrix, **kwargs):
        self.matrix = matrix
        if 'x' in kwargs:
            self.keygen = lambda tup : Coord(kwargs['x'], tup[0], tup[1])
        elif 'y' in kwargs:
            self.keygen = lambda tup : Coord(tup[0], kwargs['y'], tup[1])
        elif 'z' in kwargs:
            self.keygen = lambda tup : Coord(tup[0], tup[1], kwargs['z'])
        else:
            raise ValueError("invalid plane")

    def __getitem__(self, key):
        return self.matrix[self.keygen(key)]

    def __setitem__(self, key, value):
        self.matrix[self.keygen(key)] = value


@dataclass
class State(object):
    energy: int
    harmonics: bool # True == High, False == Low
    matrix: Matrix
    bots: list
    commands: list = field(default_factory=list)

    def find_bot(self, bid):
        for b in self.bots:
            if b.bid == bid:
                return b

    def step(self, R):
        if self.harmonics == True:
            self.energy += 30 * R * R * R
        else:
            self.energy += 3 * R * R * R
        
        self.energy += 20 * len(self.bots)


@dataclass
class Bot(object): # nanobot
    bid: int
    pos: Coord
    seeds: list
    state: State

    def halt(self):
        if len(self.state.bots) > 1:
            raise Exception("Can't halt with more than one bot")
        self.state.commands.append( commands.Halt() )

    def wait(self):
        self.state.commands.append( commands.Wait() )
        pass

    def flip(self):
        self.state.harmonics = not self.state.harmonics
        self.state.commands.append( commands.Flip() )

    def smove(self, diff):
        self.pos += diff
        self.state.energy += 2 * diff.mlen()
        self.state.commands.append( commands.SMove().set_lld( diff.dx, diff.dy, diff.dz ) )

    def lmove(self, diff1, diff2):
        self.pos += diff
        self.state.energy += 2 * (diff1.mlen() + 2 + diff2.mlen())
        self.state.commands.append( commands.LMove().set_sld1( diff1.dx, diff1.dy, diff1.dz ).set_sld2( diff2.dx, diff2.dy, diff2.dz ) )

    def fission(self, nd, m):
        f = Bot(self.seeds[0], self.coord + nd, self.seeds[1:m+2])
        self.seeds = self.seeds[m+2:]
        self.state.bots.append(f)
        self.state.energy += 24
        self.state.commands.append( commands.Fission().set_nd( nd.dx, nd.dy, nd.dz ).set_m( m ) )

    def fusionp(self, nd):
        self.state.commands.append( commands.FusionP().set_nd( nd.dx, nd.dy, nd.dz ) )

    def fusions(self, nd):
        self.state.commands.append( commands.FusionS().set_nd( nd.dx, nd.dy, nd.dz ) )

    def fill(self, nd):
        p = self.coord + nd
        if self.state.matrix[p].is_void():
            self.state.matrix[p].set_full()
            if would_be_grounded(self.state, p):
                self.state.matrix[p].set_grounded()
                self.state.ground_adjacent(p)
            else:
                ungrounded.add(p)
            
            self.state.energy += 12
        else:
            self.state.energy += 6
        self.state.commands.append( commands.Fill().set_nd( nd.dx, nd.dy, nd.dz ) )

