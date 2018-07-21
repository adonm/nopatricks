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
        # print("lmove")
        # print(path[j] - path[i])
        # print(path[k] - path[j])
        bot.lmove(path[j] - path[i], path[k] - path[j])
        return k
    elif i+1<len(path):
        # print("smove")
        # print(path[i+1] - path[i])
        bot.smove(path[i+1] - path[i])
        return i+1
    else:
        return i+1

def compress(st, bot, path):
    i = 0
    while i < len(path):
        i = next_move(st, bot, path)
        path = path[i:]
        # print(path)
        i = 0

def smove_path(st, bot, path):
    for i in range(1, len(path)):
        bot.smove(path[i] - path[i-1])

def shortest_path(st, bot, c):
    if bot.pos == c:
        return []
    seen = set()
    stack = []

    seen.add(bot.pos)
    stack.append(bot.pos)

    table = {}

    found = False
    while not found and len(stack)>0:
        p = stack.pop()
        for n in p.adjacent(st.R):
            if n not in seen and st.matrix[n].is_void():
                table[n] = p
                seen.add(n)
                stack.insert(0, n)
                if n == c:
                    found = True

    if not found:
        return None

    path = []
    x = c
    while x != bot.pos:
        path.append(x)
        x = table[x]
    path.append(bot.pos)
    return list(reversed(path))

def back_to_base(st, bot):
    compress(st, bot, shortest_path(st, bot, Coord(0,0,0)))
    
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
    return below, belowp

def old_algo(st):
    bot = st.bots[0]
    bot.smove(UP)
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
                    elif st.matrix.would_be_grounded(belowp) and len(st.matrix.ungrounded) == 0 and st.harmonics == True:
                        bot.flip()
                    bot.fill(DOWN)
            bot.smove(LEFT.mul(xdir))
            zdir *= -1
        bot.smove(UP)
        xdir *= -1

def shortest_path_algo(st):
    bot = st.bots[0]
    bot.smove(UP)
    
    pts = list(st.matrix.keys())
    minPt = 0

    while not st.is_model_finished():
        j = None
        while st.matrix[pts[minPt]].is_full() or not st.matrix[pts[minPt]].is_model():
            minPt += 1

        for i in range(minPt, len(pts)):
            if st.matrix[pts[i]].is_void() and st.matrix[pts[i]].is_model() and st.matrix.would_be_grounded(pts[i]):
                j = i
                break
        if j is None:
            break

        # print(pts[j])
        pt = pts[j]
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
        
    data = commands.export_nbt( st.trace )
    with open("submission/LA"+str(problem).zfill(3)+".nbt", "wb") as file:
        file.write(data)

    
