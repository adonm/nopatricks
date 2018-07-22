#!/usr/bin/env python3
import state
import commands
from coord import Coord, diff, UP, DOWN, LEFT, RIGHT, FORWARD, BACK
import sys, os
import math
from algorithm import *
import numpy as np

def next_best_point(st):
    for x, y, z in np.transpose(np.where(st.matrix._ndarray == state.Voxel.MODEL)):
        coord = Coord(int(x), int(y), int(z))
        if st.matrix.would_be_grounded(coord):
            return coord

zcoords = []
def closest_best_point(st):
    bot = st.bots[0]
    global zcoords
    print("closest best pt")
    if len(zcoords) == 0:
        zcoords = st.matrix.fill_next(bot.pos + DOWN)
        zcoords.reverse()
    pt = zcoords.pop()
    print("pt ofund")
    return pt

def fill_neighbours(st, bot):
    pts = [
        bot.pos + DOWN + LEFT,
        bot.pos + DOWN + RIGHT,
        bot.pos + DOWN + FORWARD,
        bot.pos + DOWN + BACK
    ]
    for pt in pts:
        
        if st.matrix.is_valid_point(pt) and st.matrix.would_be_grounded(pt) and st.matrix[pt].is_void() and st.matrix[pt].is_model():
            bot.fill(pt - bot.pos)

def shortest_path_algo(st):
    bot = st.bots[0]
    bot.smove(UP)
    
    while not st.is_model_finished():
        pt = next_best_point(st)
        for a in pt.adjacent(st.R):
            # print(a)
            if st.matrix[a].is_void():
                path = shortest_path(st, st.bots[0], a)
                # print(path)
                if path is not None:
                    compress(st, st.bots[0], path)
                    # print(st.bots[0].pos)
                    bot.fill(pt - st.bots[0].pos)
                    # fill_neighbours(st, st.bots[0])
                    break
            # print("done")
        # break

if __name__ == '__main__':
    problem = int(sys.argv[1])
    st = state.State.create(problem=problem)
    import cProfile
    cProfile.run('shortest_path_algo(st)', sort="calls")
    back_to_base(st, st.bots[0])
    st.bots[0].halt()
    st.step()
        
    print( st )
    print( 'energy: {}, default: {}, score: {:0.3f}/{:0.3f}'.format( st.energy, st.default_energy, st.score, st.score_max ) )
    data = commands.export_nbt( st.trace )
    with open("submission/FA"+str(problem).zfill(3)+".nbt", "wb") as file:
        file.write(data)

    
