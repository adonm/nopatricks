#!/usr/bin/env python3
import state
import commands
from coord import Coord, diff, UP, DOWN, LEFT, RIGHT, FORWARD, BACK
import sys
import math
from algorithm import *

def shortest_path_algo(st):
    bot = st.bots[0]
    bot.smove(UP)
    
    pts = list(st.matrix.keys())
    minPt = 0

    while not st.is_model_finished():
        pt = st.matrix.to_fill
        for a in pt.adjacent(st.R):
            # print(a)
            path = shortest_path(st, st.bots[0], a)
            # print(path)
            if path is not None:
                compress(st, st.bots[0], path)
                # print(st.bots[0].pos)
                bot.fill(pt - a)
                break
        # break

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
    with open("submission/LA"+str(problem).zfill(3)+".nbt", "wb") as file:
        file.write(data)

    
