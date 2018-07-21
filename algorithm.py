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

def next_move(st, bot, path):
    i = 0
    j = 1
    while j<len(path) and (path[j] - path[i]).is_manhatten():
        j += 1
    j -= 1

    k = j+1
    while k<len(path) and (path[k] - path[j]).is_manhatten():
        k += 1
    k -= 1
    
    if i!=j and k!=j:
        bot.lmove(path[j] - path[i], path[k] - path[j])
        return k + 1
    else: 
        bot.smove(path[i+1] - path[i])
        return i+2

def compress(st, bot, path):
    i = 0
    print(bot.pos)
    print(path)
    while i < len(path):
        i = next_move(st, bot, path)
        st.step()
        path = path[i:]
        i = 0

def smove_path(st, bot, path):
    for i in range(1, len(path)):
        bot.smove(path[i] - path[i-1])
        st.step()

def shortest_path(st, bot, c):
    if bot.pos == c:
        return []
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
    compress(st, st.bots[0], shortest_path(st, bot, Coord(0,0,0)))
    
def skip(bot, st, diff):
    jump = 1
    while jump < 16:
        belowp = bot.pos + DOWN
        for i in range(jump):
            belowp = belowp + diff
        below = st.matrix[belowp]
        if below.is_model():
            break
        if belowp.z > st.R-2 or belowp.x > st.R-2:
            break
        if belowp.z < 1 or belowp.x < 1:
            break
        jump += 1
    bot.smove(belowp - (bot.pos + DOWN))
    st.step()
    return below, belowp

if __name__ == '__main__':
    problem = int(sys.argv[1])
    st = state.State.create(problem=problem)
    bot = st.bots[0]
    bot.smove(UP)
    st.step()
    zdir = 1
    xdir = 1
    bounds = convex_hull(st)
    while bot.pos.y < st.R-1 and not st.is_model_finished():
        while (xdir == 1 and bot.pos.x <= bounds["maxx"]) or (xdir == -1 and bot.pos.x >= bounds["minx"]):
            while (zdir == 1 and bot.pos.z <= bounds["maxz"]) or (zdir==-1 and bot.pos.z >= bounds["minz"]):
                below, belowp = skip(bot, st, FORWARD.mul(zdir))
                if below.is_model() and below.is_void():
                    if not st.matrix.would_be_grounded(belowp) and st.harmonics == False:
                        bot.flip()
                        st.step()
                    elif st.matrix.would_be_grounded(belowp) and len(st.matrix.ungrounded) == 0 and st.harmonics == True:
                        bot.flip()
                        st.step()
                    bot.fill(DOWN)
                    st.step()
            bot.smove(LEFT.mul(xdir))
            st.step()
            zdir *= -1
        bot.smove(UP)
        st.step()
        xdir *= -1
    
    back_to_base(st)
    bot.halt()
    st.step()
        
    print( st )
    print( 'energy: {}, default: {}, score: {:0.3f}/{:0.3f}'.format( st.energy, st.default_energy, st.score, st.score_max ) )
    data = commands.export_nbt( st.trace )
    with open("submission/LA"+str(problem).zfill(3)+".nbt", "wb") as file:
        file.write(data)

    
