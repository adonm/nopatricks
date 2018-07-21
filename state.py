#!/usr/bin/env python3
from dataclasses import dataclass, astuple, field
from coord import Coord
from mrcrowbar.utils import to_uint64_le, unpack_bits
from collections.abc import Mapping
import commands
from textwrap import wrap

class Voxel:
    """ Voxel represents mutable location information """

    # current implementation is a bitmask held in an int
    # the first few bits are the filled state
    VOID = 0
    FULL = 1 << 0
    GROUNDED = 1 << 1
    # the model bit is on if this location forms part of the target model
    MODEL = 1 << 2


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

    def __repr__(self):
        return hex(self.val)[2] # just display first 4 bits in mask as hex


class Matrix(Mapping):
    """ Matrix(size=R) initialises an empty matrix
        Matrix(problem=N) loads problem N
        Matrix(filename="foo.mdl") loads model file"""

    def __init__(self, **kwargs):
        self.ungrounded = set()
        self.ngrounded = 0
        self.nfull = 0
        if 'size' in kwargs:
            self.size = kwargs['size']
            self.state = [Voxel.empty() for i in range(self.size ** 3)]
        elif 'filename' in kwargs:
            self.size, self.state = Matrix._load_file(kwargs['filename'])
        else:
            self.size, self.state = Matrix._load_prob(kwargs.get('problem', 1))
        
        self.nmodel = len([v for v in self.state if v.is_model()])

    @property
    def num_modelled(self):
        return len([v for v in self.state if v.is_model()])

    @staticmethod
    def _load_prob(num):
        return Matrix._load_file("problemsL/LA%03d_tgt.mdl" % num)

    @staticmethod
    def _load_file(filename):
        with open(filename, 'rb') as fb:
            bytedata = fb.read()
            size = int(bytedata[0])
            state = []
            for byte in bytedata[1:]:
                for bit in to_uint64_le( unpack_bits( byte ) ):
                    state.append(Voxel.empty(bit))
            return size, state

    def coord_index(self, coord):
        if not isinstance(coord, Coord):
            raise TypeError()
        return coord.x * self.size * self.size + coord.y * self.size + coord.z

    def in_range(self, val):
        if isinstance(val, int):
            return val >= 0 and val < self.size
        elif isinstance(val, Coord):
            return self.in_range(val.x) and self.in_range(val.y) and self.in_range(val.z)
        raise TypeError()

    def keys(self):
        # loop over y last so we ascend by default
        for y in range(self.size):
            for x in range(self.size):
                for z in range(self.size):
                    yield Coord(x, y, z)

    def __iter__(self):
        return self.keys()

    def __len__(self):
        return self.size ** 3

    def __getitem__(self, key):
        return self.state[self.coord_index(key)]

    def __setitem__(self, key, value):
        self.state[self.coord_index(key)] = value

    def ground_adjacent(self, gc):
        stack = [gc]
        while len(stack) > 0:
            g = stack.pop()
            for v in [x for x in g.adjacent(self.size) if self[x].is_full() and not self[x].is_grounded()]:
                self.set_grounded(v)
                if v in self.ungrounded:
                    self.ungrounded.remove(v)
                stack.append(v)
    
    def set_grounded(self, c):
        v = self[c]
        assert v.val & Voxel.FULL
        v.val |= Voxel.GROUNDED
        self.ngrounded += 1

    def set_full(self, c):
        v = self[c]
        assert not (v.val & Voxel.FULL)
        v.val |= Voxel.FULL
        self.nfull += 1

    def would_be_grounded(self, p):
        return p.y == 0 or len([x for x in p.adjacent(self.size) if self[x].is_grounded()]) > 0

    def yplane(self, y):
        """ Returns a view into this matrix at a constant y """
        return MatrixPlane(self, y=y)

    def __repr__(self):
        return "size: {}, model/full/grounded: {}/{}/{}".format(self.size, self.num_modelled, self.num_full, self.num_grounded)


class MatrixPlane(Mapping):
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

    def keys(self):
        for u in range(self.matrix.size):
            for v in range(self.matrix.size):
                yield (u, v)

    def __iter__(self):
        return self.keys()

    def __len__(self):
        return self.matrix.size ** 2

    def __getitem__(self, key):
        return self.matrix[self.keygen(key)]

    def __setitem__(self, key, value):
        self.matrix[self.keygen(key)] = value

    def asciigrid(self):
        grid = wrap("".join([repr(self[k]) for k in self]), self.matrix.size)
        grid.reverse() # display bottom left as x=0,z=0
        return grid

    def __repr__(self):
        return("\n".join(self.asciigrid()))

    def adjacent(self, key):
        deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        candidates = [(key[0] + d[0], key[1] + d[1]) for d in deltas]
        return [n for n in candidates if self.matrix.in_range(self.keygen(n))]

@dataclass
class State(object):
    matrix: Matrix
    bots: list = field(default_factory = list)
    trace: list = field(default_factory = list)
    energy: int = 0
    harmonics: bool = False # True == High, False == Low
    step_id: int = 0
    bots_to_add: list = field(default_factory = list)
    primary_fuse_bots: list = field(default_factory = list)
    secondary_fuse_bots: list = field(default_factory = list)

    @property
    def R(self):
        return self.matrix.size

    @classmethod
    def create(cls, problem=1):
        self = cls(Matrix(problem=problem))
        self.bots.append(Bot(state=self))
        return self

    def is_model_finished(self):
        return self.matrix.nfull == self.matrix.nmodel

    def find_bot(self, bid):
        for b in self.bots:
            if b.bid == bid:
                return b

    def step(self):
        if self.harmonics == True:
            self.energy += 30 * self.R * self.R * self.R
        else:
            self.energy += 3 * self.R * self.R * self.R
        
        self.energy += 20 * len(self.bots)
        self.step_id += 1

        for prim_bot, sec_pos in self.primary_fuse_bots:
            for i, (sec_bot, prim_pos) in enumerate(self.secondary_fuse_bots):
                if prim_bot.pos == prim_pos and sec_bot.pos == sec_pos:
                    self.secondary_fuse_bots.pop(i)
                    prim_bot.seeds.append(sec_bot.bid)
                    prim_bot.seeds.extend(sec_bot.seeds)
                    self.bots.remove(sec_bot)
                    self.energy -= 24
                    break
            raise ValueError( 'missing secondary fusion match for {}'.format(prim_bot.bid) )
        if self.secondary_fuse_bots:
            raise ValueError( 'missing primary fusion match for {}'.format(self.secondary_fuse_bots[0][0].bid) )
        self.primary_fuse_bots.clear()

        self.bots.extend(self.bots_to_add)
        self.bots_to_add.clear()


    def __repr__(self):
        return 'step_id: {}, bots: {}, energy: {}, matrix: {}'.format(self.step_id, len( self.bots ), self.energy, repr(self.matrix))


def default_seeds():
    return list(range(2,21))

@dataclass
class Bot(object): # nanobot
    state: State
    bid: int = 1
    pos: Coord = Coord(0,0,0)
    seeds: list = field(default_factory = default_seeds)

    def halt(self):
        if len(self.state.bots) > 1:
            raise Exception("Can't halt with more than one bot")
        self.state.trace.append( commands.Halt() )

    def wait(self):
        self.state.trace.append( commands.Wait() )
        pass

    def flip(self):
        self.state.harmonics = not self.state.harmonics
        self.state.trace.append( commands.Flip() )

    def smove(self, diff):
        self.pos += diff
        self.state.energy += 2 * diff.mlen()
        self.state.trace.append( commands.SMove().set_lld( diff.dx, diff.dy, diff.dz ) )

    def lmove(self, diff1, diff2):
        self.pos += diff
        self.state.energy += 2 * (diff1.mlen() + 2 + diff2.mlen())
        self.state.trace.append( commands.LMove().set_sld1( diff1.dx, diff1.dy, diff1.dz ).set_sld2( diff2.dx, diff2.dy, diff2.dz ) )

    def fission(self, nd, m):
        f = Bot(self.state, self.seeds[0], self.pos + nd, self.seeds[1:m+2])
        self.seeds = self.seeds[m+2:]
        self.state.bots_to_add.append(f)
        self.state.energy += 24
        self.state.trace.append( commands.Fission().set_nd( nd.dx, nd.dy, nd.dz ).set_m( m ) )

    def fusionp(self, nd):
        self.primary_fuse_bots.append((self, self.pos+nd))
        self.state.trace.append( commands.FusionP().set_nd( nd.dx, nd.dy, nd.dz ) )

    def fusions(self, nd):
        self.secondary_fuse_bots.append((self, self.pos+nd))
        self.state.trace.append( commands.FusionS().set_nd( nd.dx, nd.dy, nd.dz ) )

    def fill(self, nd):
        p = self.pos + nd
        matrix = self.state.matrix
        if matrix[p].is_void():
            matrix.set_full(p)
            if matrix.would_be_grounded(p):
                self.state.matrix.set_grounded(p)
                matrix.ground_adjacent(p)
            else:
                matrix.ungrounded.add(p)
            
            self.state.energy += 12
        else:
            self.state.energy += 6
        self.state.trace.append( commands.Fill().set_nd( nd.dx, nd.dy, nd.dz ) )

    def __repr__(self):
        output = self.state.matrix.yplane(self.pos.y).asciigrid()
        output.reverse()
        botrow = list(output[self.pos.x])
        botrow[self.pos.z] = "B"
        output[self.pos.x] = "".join(botrow)
        output.reverse()
        output = ["Bot: {}, Seeds: {}\n".format(self.bid, self.seeds)] + output
        return("\n".join(output))

        


