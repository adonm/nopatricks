#!/usr/bin/env python3
import state
import commands
from coord import Coord, diff, UP, DOWN, LEFT, RIGHT, FORWARD, BACK
import sys
import math

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

def shortest_path(st, bot, c):
    seen = set()
    stack = []

    seen.add(bot.pos)
    stack.append(bot.pos)

    table = {}

    found = False
    while not found:
        p = stack.pop()
        for n in p.adjacent(st.R):
            if n not in seen and st.matrix[n].is_void():
                table[n] = p
                seen.add(n)
                stack.insert(0, n)
                if n == c:
                    found = True

    path = []
    x = c
    while x != bot.pos:
        path.append(x)
        x = table[x]
    path.append(bot.pos)
    return list(reversed(path))

def back_to_base(st):
    path = shortest_path(st, st.bots[0], Coord(0,0,0))
    for i in range(1, len(path)):
        bot.smove(path[i] - path[i-1])
    
if __name__ == '__main__':
    problem = int(sys.argv[1])
    st = state.State.create(problem=problem)
    bot = st.bots[0]
    bot.smove(UP)
    zdir = 1
    xdir = 1
    bounds = convex_hull(st)
    while bot.pos.y < st.R-1 and not st.is_model_finished():
        while (xdir == 1 and bot.pos.x <= bounds["maxx"]) or (xdir == -1 and bot.pos.x >= bounds["minx"]):
            while (zdir == 1 and bot.pos.z <= bounds["maxz"]) or (zdir==-1 and bot.pos.z >= bounds["minz"]):
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

    
