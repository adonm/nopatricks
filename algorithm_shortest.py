#!/usr/bin/env python3
import state
import commands
from coord import Coord, diff, UP, DOWN, LEFT, RIGHT, FORWARD, BACK
import sys, os
import math
from algorithm import *
import numpy as np
from math import floor

def next_best_point(st, bot=None):
    minX = bot.region["minX"]
    maxX = bot.region["maxX"]
    # print(bot.region)
        
    for y, x, z in np.transpose(np.where(np.transpose(st.matrix._ndarray, (1, 0, 2)) == state.Voxel.MODEL)):
        if minX <= x < maxX:
            coord = Coord(int(x), int(y), int(z))
            if st.matrix.would_be_grounded(coord):
                print(coord)
                return coord
    return None

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

def solve(st):
    n = 0
    while not st.is_model_finished():
        
        for bot in st.bots:
            # print(bot)
            # n+=1
            # if n>1000:
            #     return
            pt = next_best_point(st, bot)
            if pt is not None:
                if (pt - bot.pos).mlen() == 1:
                    fill(st, bot, pt - bot.pos)
                else:
                    for a in pt.adjacent(st.R):
                        if st.matrix[a].is_void():
                            path = shortest_path(st, bot, a)
                            print("path")
                            print([b.pos for b in st.bots])
                            print(path)
                            if path is not None:
                                # print("got path")
                                compress(st, bot, path)
                            elif len(bot.actions)==0:
                                fill(st, bot, pt - a)
                            break
            else:
                back_to_base(st, bot)

        while any(len(bot.actions)>0 for bot in st.bots):
            # for bot in st.bots:
            #     print(bot.pos)
                # if len(bot.actions)>0:
                #     print(bot.actions[0])
            print("stepping")
            st.step()
            
            



def shortest_path_algo(st):
    bot = st.bots[0]
    bot.smove(UP)
    st.step()
    bot.fission(LEFT, bot.seeds[0])
    while st.step():
        pass
    bot2 = st.bots[1]

    for i in range(int(st.R-2)):
        bot2.smove(LEFT)
    while st.step():
        pass


    bot.region = {
        "minX": 0,
        "maxX": floor(st.R/2),
        # minY: 0,
        # maxY: st.R,
        # minZ: 0,
        # maxZ: st.R,
    }
    st.bots[1].region = {
        "minX": floor(st.R/2),
        "maxX": st.R,
        # minY: 0,
        # maxY: st.R,
        # minZ: 0,
        # maxZ: st.R,
    }

    solve(st)
    print("finished solve")


    while len(bot.actions) > 0:
        st.step()
    for a in bot.pos.adjacent(st.R):
        if st.matrix[a].is_void():
            path = shortest_path(st, bot2, a)
            if path is not None:
                print("found path")
                compress(st, bot2, path)
                
                while len(bot2.actions) > 0:
                    st.step()

                break

    # print(bot.pos)
    # print(bot2.pos)
    bot.fusionp(bot2.pos - bot.pos)
    bot2.fusions(bot.pos - bot2.pos)
    
    # while st.step():
    #     pass

    
    # while not st.is_model_finished():
    #     pt = next_best_point(st)
    #     for a in pt.adjacent(st.R):
    #         if st.matrix[a].is_void():
    #             path = shortest_path(st, bot, a)
    #             if path is not None:
    #                 compress(st, bot, path)
    #             fill(st, bot, pt - a)
    #             break

    #     while len(st.bots[0].actions) > 0:
    #         st.step()

if __name__ == '__main__':
    problem = int(sys.argv[1])
    st = state.State.create(problem=problem)
    shortest_path_algo(st)
    for bot in st.bots:
        bot.halt()

    while st.step():
        pass
        
    print( st )
    print( 'energy: {}, default: {}, score: {:0.3f}/{:0.3f}'.format( st.energy, st.default_energy, st.score, st.score_max ) )
    data = commands.export_nbt( st.trace )
    with open("submission/FA"+str(problem).zfill(3)+".nbt", "wb") as file:
        file.write(data)

    
