#!/usr/bin/env python3
import state
import commands
from coord import Coord, diff, UP, DOWN, LEFT, RIGHT, FORWARD, BACK
import sys
import math


def back_to_base(st):
    bot = st.bots[0]
    while bot.pos.z != 0:
        bot.smove(BACK)
    while bot.pos.x != 0:
        bot.smove(RIGHT)
    while bot.pos.y != 0:
        bot.smove(DOWN)
    
def convex_hull(st):
    minx = st.R-1
    maxx = 0
    minz = st.R-1
    maxz = 0
    for y in range(st.R):
        for x in range(st.R):
            for z in range(st.R):
                if st.matrix[Coord(x, y, z)].is_model():
                    if x < minx:
                        minx = x
                    if x > maxx:
                        maxx = x
                    if z < minz:
                        minz = z
                    if z > maxz:
                        maxz = z
    return {
        "minx": minx,
        "maxx": maxx,
        "minz": minz,
        "maxz": maxz,
    }

if __name__ == '__main__':
    problem = int(sys.argv[1])
    st = state.State.create(problem=problem)
    bot = st.bots[0]
    bot.smove(UP)
    zdir = 1
    xdir = 1
    bounds = convex_hull(st)
    for i in range(10):
        while bot.pos.y < st.R-1 and not st.is_model_finished():
            while (xdir == 1 and bot.pos.x <= bounds["maxx"]) or (xdir == -1 and bot.pos.x >= bounds["minx"]):
                while (zdir == 1 and bot.pos.z <= bounds["maxz"]) or (zdir==-1 and bot.pos.z >= bounds["minz"]):
                    bot.smove(FORWARD.mul(zdir))
                    below = st.matrix[bot.pos + DOWN]
                    belowp = bot.pos + DOWN
                    if below.is_model() and below.is_void():
                        if st.matrix.would_be_grounded(belowp):
                            bot.fill(DOWN)
                bot.smove(LEFT.mul(xdir))
                zdir *= -1
            bot.smove(UP)
            xdir *= -1
        back_to_base(st)
    print(st)
    bot.halt()
        
    data = commands.export_nbt( st.trace )
    with open("submission/LA"+str(problem).zfill(3)+".nbt", "wb") as file:
        file.write(data)

    
