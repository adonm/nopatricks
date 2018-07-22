#!/usr/bin/env python3
from coord import Coord
import commands

from mrcrowbar.utils import to_uint64_le, unpack_bits
from collections.abc import Mapping
from textwrap import wrap
import os
import math
from dataclasses import dataclass, field
import numpy as np
from enum import Enum

class Voxel:
    """ Voxel represents mutable location information """

    # current implementation is a bitmask held in an int
    # the first few bits are the filled state
    VOID = 0
    FULL = 1 << 0
    GROUNDED = 1 << 1
    # the model bit is on if this location forms part of the target model
    MODEL = 1 << 2
    # the bot bit is on if this location has a bot at it
    BOT = 1 << 3


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
        return not (self.is_full() or self.is_bot())

    def is_full(self):
        return self.val & Voxel.FULL

    def is_grounded(self):
        return self.val & Voxel.GROUNDED

    def is_bot(self):
        return self.val & Voxel.BOT

    def is_model(self):
        return self.val & Voxel.MODEL

    def __repr__(self):
        return repr(self.val)


class Matrix(Mapping):
    _nfull = None
    _nmodel = None
    _ngrounded = None
    """ Matrix(size=R) initialises an empty matrix
        Matrix(problem=N) loads problem N
        Matrix(filename="foo.mdl") loads model file"""

    def __init__(self, **kwargs):
        self.ungrounded = set()
        self.model_pts = None
        if 'size' in kwargs:
            self.size = kwargs['size']
            self._ndarray.flat = np.zeros(shape=(size, size, size), dtype=np.dtype('u1'))
        elif 'filename' in kwargs:
            self.size, self._ndarray = Matrix._load_file(kwargs['filename'])
        else:
            self.size, self._ndarray = Matrix._load_prob(kwargs.get('problem', 1))
        
    @property
    def nfull(self):
        if not self._nfull:
            self._nfull = np.count_nonzero(self._ndarray & Voxel.FULL)
        return self._nfull

    @property
    def nmodel(self):
        if not self._nmodel:
            self._nmodel = np.count_nonzero(self._ndarray & Voxel.MODEL)
        return self._nmodel

    @property
    def ngrounded(self):
        if not self._ngrounded:
            self._ngrounded = np.count_nonzero(self._ndarray & Voxel.GROUNDED)
        return self._ngrounded

    @staticmethod
    def _load_prob(num):
        return Matrix._load_file("problemsF/FA%03d_tgt.mdl" % num)

    @staticmethod
    def _load_file(filename):
        with open(filename, 'rb') as fb:
            bytedata = fb.read()
            size = int(bytedata[0])
            ndarray = np.zeros(shape=(size, size, size), dtype=np.dtype('u1'))
            index = 0
            for byte in bytedata[1:]:
                for bit in to_uint64_le( unpack_bits( byte ) ):
                    ndarray.flat[index] = Voxel.empty(bit).val
                    index += 1
            return size, ndarray

    def is_valid_point(self, coord):
        return (0 <= coord.x < self.size) and (0 <= coord.y < self.size) and (0 <= coord.z < self.size)

    def coord_index(self, coord):
        if not isinstance(coord, Coord):
            raise TypeError()
        assert self.is_valid_point(coord)
        return (coord.x, coord.y, coord.z)

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
        return Voxel(self._ndarray[self.coord_index(key)])

    def __setitem__(self, key, voxel):
        self._ndarray[self.coord_index(key)] = voxel.val

    def ground_adjacent(self, gc):
        stack = [gc]
        while len(stack) > 0:
            g = stack.pop()
            for v in [x for x in g.adjacent(self.size) if self[x].is_full() and not self[x].is_grounded()]:
                self.set_grounded(v)
                if v in self.ungrounded:
                    self.ungrounded.remove(v)
                stack.append(v)
    
    def toggle_bot(self, c):
        self._ndarray[(c.x, c.y, c.z)] ^= Voxel.BOT

    def set_grounded(self, c):
        self._ndarray[(c.x, c.y, c.z)] |= Voxel.GROUNDED
        self._ngrounded = None # invalidate cache

    def set_full(self, c1, c2=None):
        # fill a voxel or a region
        if not c2:
            assert not (self._ndarray[(c1.x, c1.y, c1.z)] & Voxel.FULL)
            self._ndarray[(c1.x, c1.y, c1.z)] |= Voxel.FULL
        else:
            pass # todo fill region
        self._nfull = None # invalidate cache

    def would_be_grounded(self, p):
        return p.y == 0 or len([n for n in p.adjacent(self.size) if self._ndarray[(n.x,n.y,n.z)] & Voxel.GROUNDED]) > 0

    def to_fill(self):
        return [Coord(int(x), int(y), int(z)) for x,y,z in np.transpose(np.where(self._ndarray == Voxel.MODEL))]
        
    def fill_next(self, nearc=None): # ordered list of next coord that model wants filled that would be grounded
        coords = self.to_fill()
        if nearc: # sort coords by distance from nearc
            coords.sort(key=lambda c: (c-nearc).mlen() + self.size * abs(c.y - nearc.y))
        x, y = None, None
        zcoords = []
        for c in coords:
            if x and c.x != x and c.y != y:
                continue
            if self.would_be_grounded(c):
                x, y = c.x, c.y
                zcoords.append(c)
        return zcoords

    def yplane(self, y):
        """ Returns a view into this matrix at a constant y """
        return MatrixYPlane(self, y=y)

    def __repr__(self):
        return "size: {}, model/full/grounded: {}/{}/{}".format(self.size, self.nmodel, self.nfull, self.ngrounded)


class MatrixYPlane(Mapping):
    def __init__(self, matrix, y):
        self.matrix = matrix
        self.y = y

    def keygen(self, tup):
        return Coord(tup[0], self.y, tup[1])

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

    def __repr__(self):
        return repr(self.matrix._ndarray[:,self.y,:])

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
    default_energy: int = 1
    enable_trace: bool = True

    @property
    def R(self):
        return self.matrix.size

    @property
    def score(self):
        return max(0, self.score_max*(self.default_energy-self.energy)/self.default_energy)

    @property
    def score_max(self):
        return math.log2(self.R)*1000

    @classmethod
    def create(cls, problem=1):
        self = cls(Matrix(problem=problem))
        bot = Bot(state=self)
        self.matrix.toggle_bot(bot.pos) # enter voxel
        self.bots.append(bot)
        test = 'dfltEnergy/LA{:03d}'.format(problem)
        if os.path.isfile(test):
            self.default_energy = int(open(test, 'r').read(), 0)
        return self

    def is_model_finished(self):
        return self.matrix.nfull == self.matrix.nmodel

    def find_bot(self, bid):
        for b in self.bots:
            if b.bid == bid:
                return b

    def step(self):

        for bot in self.bots:
            if len(bot.actions)>0:
                bot.actions.pop()()
            else:
                return

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
                    self.matrix.toggle_bot(sec_bot.pos) # leave voxel
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
    return list(range(2,41))

class Actions(Enum):
    HALT = 0

@dataclass
class BotOld(object): # nanobot
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
        if self.state.enable_trace:
            self.state.trace.append( commands.Flip() )

    def smove(self, diff):
        dest = self.pos + diff
        if not self.state.matrix[dest].is_void():
            raise RuntimeError('tried to move to occupied point {} at time {}'.format(dest, self.state.step_id))
        self.state.matrix.toggle_bot(self.pos) # leave voxel
        self.state.matrix.toggle_bot(dest) # enter voxel
        self.pos = dest
        self.state.energy += 2 * diff.mlen()
        if self.state.enable_trace:
            self.state.trace.append( commands.SMove().set_lld( diff.dx, diff.dy, diff.dz ) )

    def lmove(self, diff1, diff2):
        dest = self.pos + diff1 + diff2
        if not self.state.matrix[dest].is_void():
            raise RuntimeError('tried to move to occupied point {} at time {}'.format(dest, self.state.step_id))
        self.state.matrix.toggle_bot(self.pos) # leave voxel
        self.state.matrix.toggle_bot(dest) # enter voxel
        self.pos = dest
        self.state.energy += 2 * (diff1.mlen() + 2 + diff2.mlen())
        if self.state.enable_trace:
            self.state.trace.append( commands.LMove().set_sld1( diff1.dx, diff1.dy, diff1.dz ).set_sld2( diff2.dx, diff2.dy, diff2.dz ) )

    def fission(self, nd, m):
        f = Bot(self.state, self.seeds[0], self.pos + nd, self.seeds[1:m+2])
        self.state.matrix.toggle_bot(self.pos + nd) # enter voxel
        self.seeds = self.seeds[m+2:]
        self.state.bots_to_add.append(f)
        self.state.energy += 24
        if self.state.enable_trace:
            self.state.trace.append( commands.Fission().set_nd( nd.dx, nd.dy, nd.dz ).set_m( m ) )

    def fusionp(self, nd):
        # note: energy accounted for in State.step
        self.primary_fuse_bots.append((self, self.pos+nd))
        if self.state.enable_trace:
            self.state.trace.append( commands.FusionP().set_nd( nd.dx, nd.dy, nd.dz ) )

    def fusions(self, nd):
        # note: energy accounted for in State.step
        self.secondary_fuse_bots.append((self, self.pos+nd))
        if self.state.enable_trace:
            self.state.trace.append( commands.FusionS().set_nd( nd.dx, nd.dy, nd.dz ) )

    def fill(self, nd):
        p = self.pos + nd
        matrix = self.state.matrix
        if matrix[p].is_void():
            if matrix.would_be_grounded(p):
                self.state.matrix.set_grounded(p)
                matrix.ground_adjacent(p)
            elif self.state.harmonics:
                matrix.ungrounded.add(p)
            else:
                raise RuntimeError('tried to fill ungrounded point {} at time {}'.format(p, self.state.step_id))
            matrix.set_full(p)
            
            self.state.energy += 12
        else:
            self.state.energy += 6
        if self.state.enable_trace:
            self.state.trace.append( commands.Fill().set_nd( nd.dx, nd.dy, nd.dz ) )

    def void(self, nd):
        print('FIXME: Bot.void()')
        if self.state.enable_trace:
            self.state.trace.append( commands.Void().set_nd( nd.dx, nd.dy, nd.dz ) )

    def gfill(self, nd, fd):
        print('FIXME: Bot.gfill()')
        if self.state.enable_trace:
            self.state.trace.append( commands.GFill().set_nd( nd.dx, nd.dy, nd.dz ).set_fd( fd.dx, fd.dy, fd.dz ) )

    def gvoid(self, nd, fd):
        print('FIXME: Bot.gvoid()')
        if self.state.enable_trace:
            self.state.trace.append( commands.GVoid().set_nd( nd.dx, nd.dy, nd.dz ).set_fd( fd.dx, fd.dy, fd.dz ) )

    def __repr__(self):
        return "Bot: {}, Seeds: {}\n\n{}".format(self.bid, self.seeds, repr(self.state.matrix._ndarray[:, self.pos.y, :]))


@dataclass
class Bot(object): # nanobot
    state: State
    bid: int = 1
    pos: Coord = Coord(0,0,0)
    seeds: list = field(default_factory = default_seeds)
    actions: list = field(default_factory = list)

    def halt(self):
        self.actions.append(lambda : self._halt())
    
    def wait(self):
        self.actions.append(lambda : self._wait())

    def flip(self):
        self.actions.append(lambda : self._flip())

    def smove(self, diff):
        self.actions.append(lambda : self._smove(diff))

    def lmove(self, diff1, diff2):
        self.actions.append(lambda : self._lmove(diff1, diff2))
    
    def fission(self, nd, m):
        self.actions.append(lambda : self._fission(nd, m))

    def fusionp(self, nd):
        self.actions.append(lambda : self._fusionp(nd))

    def fusions(self, nd):
        self.actions.append(lambda : self._fusions(nd))

    def fill(self, nd):
        self.actions.append(lambda : self._fill(nd))

    def void(self, nd):
        self.actions.append(lambda : self._void(nd))

    def gfill(self, nd, m):
        self.actions.append(lambda : self._gfill(nd, m))

    def gvoid(self, nd, m):
        self.actions.append(lambda : self._gvoid(nd, m))

    def _halt(self):
        if len(self.state.bots) > 1:
            raise Exception("Can't halt with more than one bot")
        self.state.trace.append( commands.Halt() )

    def _wait(self):
        self.state.trace.append( commands.Wait() )
        pass

    def _flip(self):
        self.state.harmonics = not self.state.harmonics
        if self.state.enable_trace:
            self.state.trace.append( commands.Flip() )

    def _smove(self, diff):
        dest = self.pos + diff
        if not self.state.matrix[dest].is_void():
            raise RuntimeError('tried to move to occupied point {} at time {}'.format(dest, self.state.step_id))
        self.state.matrix.toggle_bot(self.pos) # leave voxel
        self.state.matrix.toggle_bot(dest) # enter voxel
        self.pos = dest
        self.state.energy += 2 * diff.mlen()
        if self.state.enable_trace:
            self.state.trace.append( commands.SMove().set_lld( diff.dx, diff.dy, diff.dz ) )

    def _lmove(self, diff1, diff2):
        dest = self.pos + diff1 + diff2
        if not self.state.matrix[dest].is_void():
            raise RuntimeError('tried to move to occupied point {} at time {}'.format(dest, self.state.step_id))
        self.state.matrix.toggle_bot(self.pos) # leave voxel
        self.state.matrix.toggle_bot(dest) # enter voxel
        self.pos = dest
        self.state.energy += 2 * (diff1.mlen() + 2 + diff2.mlen())
        if self.state.enable_trace:
            self.state.trace.append( commands.LMove().set_sld1( diff1.dx, diff1.dy, diff1.dz ).set_sld2( diff2.dx, diff2.dy, diff2.dz ) )

    def _fission(self, nd, m):
        f = Bot(self.state, self.seeds[0], self.pos + nd, self.seeds[1:m+2])
        self.state.matrix.toggle_bot(self.pos + nd) # enter voxel
        self.seeds = self.seeds[m+2:]
        self.state.bots_to_add.append(f)
        self.state.energy += 24
        if self.state.enable_trace:
            self.state.trace.append( commands.Fission().set_nd( nd.dx, nd.dy, nd.dz ).set_m( m ) )

    def _fusionp(self, nd):
        # note: energy accounted for in State.step
        self.primary_fuse_bots.append((self, self.pos+nd))
        if self.state.enable_trace:
            self.state.trace.append( commands.FusionP().set_nd( nd.dx, nd.dy, nd.dz ) )

    def _fusions(self, nd):
        # note: energy accounted for in State.step
        self.secondary_fuse_bots.append((self, self.pos+nd))
        if self.state.enable_trace:
            self.state.trace.append( commands.FusionS().set_nd( nd.dx, nd.dy, nd.dz ) )

    def _fill(self, nd):
        p = self.pos + nd
        matrix = self.state.matrix
        if matrix[p].is_void():
            if matrix.would_be_grounded(p):
                self.state.matrix.set_grounded(p)
                matrix.ground_adjacent(p)
            elif self.state.harmonics:
                matrix.ungrounded.add(p)
            else:
                raise RuntimeError('tried to fill ungrounded point {} at time {}'.format(p, self.state.step_id))
            matrix.set_full(p)
            
            self.state.energy += 12
        else:
            self.state.energy += 6
        if self.state.enable_trace:
            self.state.trace.append( commands.Fill().set_nd( nd.dx, nd.dy, nd.dz ) )

    def _void(self, nd):
        print('FIXME: Bot.void()')
        if self.state.enable_trace:
            self.state.trace.append( commands.Void().set_nd( nd.dx, nd.dy, nd.dz ) )

    def _gfill(self, nd, fd):
        print('FIXME: Bot.gfill()')
        if self.state.enable_trace:
            self.state.trace.append( commands.GFill().set_nd( nd.dx, nd.dy, nd.dz ).set_fd( fd.dx, fd.dy, fd.dz ) )

    def _gvoid(self, nd, fd):
        print('FIXME: Bot.gvoid()')
        if self.state.enable_trace:
            self.state.trace.append( commands.GVoid().set_nd( nd.dx, nd.dy, nd.dz ).set_fd( fd.dx, fd.dy, fd.dz ) )

    def __repr__(self):
        return "Bot: {}, Seeds: {}\n\n{}".format(self.bid, self.seeds, repr(self.state.matrix._ndarray[:, self.pos.y, :]))

        


