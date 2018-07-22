#!/usr/bin/env python3
import state
import commands
from coord import Coord, diff, UP, DOWN, LEFT, RIGHT, FORWARD, BACK
import sys, os
import math
from algorithm import *
import numpy as np

def next_best_point(st):
    for y, x, z in np.transpose(np.where(np.transpose(st.matrix._ndarray, (1, 0, 2)) == state.Voxel.MODEL)):
        coord = Coord(int(x), int(y), int(z))
        if st.matrix.would_be_grounded(coord):
            return coord

zcoords = []
def closest_best_point(st):
    bot = st.bots[0]
    global zcoords
    if len(zcoords) == 0:
        zcoords = st.matrix.fill_next(bot.pos + DOWN)
        zcoords.reverse()
    pt = zcoords.pop()
    return pt

def fill(st, bot, dir):
    pts = [
        bot.pos + dir,
        bot.pos + dir + FORWARD,
        bot.pos + dir + BACK
    ]
    for pt in pts:
        if st.matrix.is_valid_point(pt) and st.matrix.would_be_grounded(pt) and st.matrix._ndarray[pt.x, pt.y, pt.z] == state.Voxel.MODEL:
            bot.fill(pt - bot.pos)


def shortest_path_algo(st):
    bot = st.bots[0]
    bot.smove(UP)
    
    while not st.is_model_finished():
        pt = next_best_point(st)
        for a in pt.adjacent(st.R):
            if st.matrix[a].is_void():
                path = shortest_path(st, bot, a)
                if path is not None:
                    compress(st, bot, path)
                fill(st, bot, pt - a)
                break
                
        while len(st.bots[0].actions) > 0:
            st.step()

if __name__ == '__main__':
    problem = int(sys.argv[1])
    st = state.State.create(problem=problem)
    shortest_path_algo(st)
    back_to_base(st, st.bots[0])
    st.bots[0].halt()
    st.step()
        
    print( st )
    print( 'energy: {}, default: {}, score: {:0.3f}/{:0.3f}'.format( st.energy, st.default_energy, st.score, st.score_max ) )
    data = commands.export_nbt( st.trace )
    with open("submission/FA"+str(problem).zfill(3)+".nbt", "wb") as file:
        file.write(data)

    
