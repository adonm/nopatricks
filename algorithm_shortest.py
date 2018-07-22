#!/usr/bin/env python3
import state
import commands
from coord import Coord, diff, UP, DOWN, LEFT, RIGHT, FORWARD, BACK
import sys, os
import math
from algorithm import *
import numpy as np
from math import floor, ceil
import cProfile

def next_best_point(st, bot=None):
    minX = bot.region["minX"]
    maxX = bot.region["maxX"]
    minZ = bot.region["minZ"]
    maxZ = bot.region["maxZ"]
    # print(bot.region)

    for y, x, z in np.transpose(np.where(np.transpose(st.matrix._ndarray, (1, 0, 2)) == state.Voxel.MODEL)):
        if minX <= x < maxX and minZ <= z < maxZ:
            coord = Coord(int(x), int(y), int(z))
            if st.matrix.would_be_grounded(coord):
                # print(coord)
                return coord
    return None

zcoords = []
def closest_best_point(st, bot):
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
        if st.matrix.is_valid_point(pt) and st.matrix.would_be_grounded(pt) and st.matrix._ndarray[pt.x, pt.y, pt.z] == state.Voxel.MODEL and (pt - bot.pos).mlen()==1:
            bot.fill(pt - bot.pos)

def solve(st):
    n = 0
    while not st.is_model_finished():

        for bot in st.bots:
            # print(bot)
            # n+=1
            # if n>600:
            #     return
            pt = next_best_point(st, bot)
            if pt is not None:
                if (pt - bot.pos).mlen() == 1:
                    fill(st, bot, pt - bot.pos)
                else:
                    for a in pt.adjacent(st.R):
                        if st.matrix[a].is_void():
                            path = shortest_path(st, bot, a)
                            # if len(path) > 10:
                            #     print(path)
                            # print("path")
                            # print([b.pos for b in st.bots])
                            # print(path)
                            if path is not None:
                                # print("got path")
                                compress(st, bot, path)
                            elif len(bot.actions)==0:
                                fill(st, bot, pt - a)
                            break
            else:
                # print("back to base")
                back_to_base(st, bot)

        while any(len(bot.actions)>0 for bot in st.bots):
            # for bot in st.bots:
            #     print(bot.pos)
                # if len(bot.actions)>0:
                #     print(bot.actions[0])
            # print("stepping")
            st.step()


def shortest_path_algo(st):
    bot = st.bots[0]
    bot.smove(UP)

    minX, maxX, minY, maxY, minZ, maxZ = st.matrix.bounds
    depth = maxZ - minZ
    split = 3
    nbots = ceil(depth / split)
    region = []
    for i in range(nbots):
        region.append({
            "minX": minX,
            "maxX": maxX,
            "minY": minY,
            "maxY": maxY,
            "minZ": minZ + i * split,
            "maxZ": min([maxZ, minZ + (i+1) * split])+1
        })
    print(region)
    print(convex_hull(st))
    print(st.matrix.bounds)
    st.step_all()

    for i in range(1, nbots):
        print(st.bots[0].seeds)
        st.bots[0].fission(FORWARD, 1)
        st.step_all()
        for j in range(region[nbots-i]["minZ"]):
            st.bots[i].smove(FORWARD)
        st.step_all()
    for i in range(nbots):
        st.bots[i].region = region[i]

    solve(st)
    print("finished solve")

    st.step_all()

    for bot2 in st.bots[1:]:
        for a in bot.pos.adjacent(st.R):
            if st.matrix[a].is_void():
                path = shortest_path(st, bot2, a)
                if path is not None:
                    print("found path")
                    compress(st, bot2, path)
                    break
        st.step_all()
        bot.fusionp(bot2.pos - bot.pos)
        bot2.fusions(bot.pos - bot2.pos)
        st.step_all()

if __name__ == '__main__':
    problem = int(sys.argv[1])
    st = state.State.create(problem=problem)
    # cProfile.run("shortest_path_algo(st)", sort="cumulative")
    shortest_path_algo(st)
    bot = st.bots[0]
    back_to_base(st, bot)
    bot.halt()

    while st.step():
        pass

    print( st )
    print( 'energy: {}, default: {}, score: {:0.3f}/{:0.3f}'.format( st.energy, st.default_energy, st.score, st.score_max ) )
    data = commands.export_nbt( st.trace )
    with open("submission/FA"+str(problem).zfill(3)+".nbt", "wb") as file:
        file.write(data)
