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
    bounds = []
    for y in range(st.R):
        minx = math.inf
        maxx = -1
        minz = math.inf
        maxz = -1
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
        bounds.append({
            "minx": minx,
            "maxx": maxx,
            "minz": minz,
            "maxz": maxz,
        })
    return bounds

if __name__ == '__main__':
    problem = int(sys.argv[1])
    st = state.State.create(problem=problem)
    bot = st.bots[0]
    bot.smove(UP)
    zdir = 1
    xdir = 1
    bounds = convex_hull(st)
    while bot.pos.y < st.R-1 and not st.is_model_finished():
        while (xdir == 1 and bot.pos.x < bounds[y]["maxx"]) or (xdir == -1 and bot.pos.x > bounds[y]["minx"]):
            while (zdir == 1 and bot.pos.z < bounds[y]["maxz"]) or (zdir==-1 and bot.pos.z > bounds[y]["minz"]):
                bot.smove(FORWARD.mul(zdir))
                below = st.matrix[bot.pos + DOWN]
                belowp = bot.pos + DOWN
                if below.is_model() and below.is_void():
                    if not st.matrix.would_be_grounded(belowp) and st.harmonics == False:
                        bot.flip()
                    elif st.matrix.would_be_grounded(belowp) and len(st.matrix.ungrounded) == 0 and st.harmonics == True:
                        bot.flip()
                    bot.fill(DOWN)
            bot.smove(LEFT.mul(xdir))
            zdir *= -1
        bot.smove(UP)
        xdir *= -1
    
    back_to_base(st)
    bot.halt()
        
    data = commands.export_nbt( st.trace )
    with open("submission/LA"+str(problem).zfill(3)+".nbt", "wb") as file:
        file.write(data)

    
