#!/usr/bin/env python3
import state
import commands
from coord import Coord, diff, UP, DOWN, LEFT, RIGHT, FORWARD, BACK
import sys
import math
import queue as Q
import heapq

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
        print("next_mvoe lmove")
        print(path[j] - path[i])
        print(path[k] - path[j])
        bot.lmove(path[j] - path[i], path[k] - path[j])
        return k
    elif i+1<len(path):
        print("next_mvoe smove")
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

class PriorityCoord(object):
    def __init__(self, priority, coord):
        self.priority = priority
        self.coord = coord
    def __lt__(self, other):
        return self.priority < other.priority
    def __str__(self):
        return str(self.coord)
    def __repr__(self):
        return str(self.coord)

def pointcost(st, src, dest):
    distance = (dest - src).mlen()
    danger = 0
    # for bot in st.bots:
    #     danger -= (dest - bot.pos).mlen()
    return distance - danger    
    
def shortest_path(st, bot, c):
    if bot.pos == c:
        return []
    assert st.matrix[c].is_void()
    seen = set()
    q = Q.PriorityQueue()

    seen.add(bot.pos)
    q.put(PriorityCoord(pointcost(st, bot.pos, c), bot.pos))

    table = {}
    # print("searching short")
    # print(bot.pos)
    # print(c)
    found = False
    while not found and not q.empty():
        # print("while")
        p = q.get().coord
        # print(p)
        for n in p.adjacent(st.R):
            if n not in seen and st.matrix[n].is_void():
                table[n] = p
                seen.add(n)
                q.put(PriorityCoord(pointcost(st, n, c), n))
                if n == c:
                    found = True

    if not found:
        return None

    path = []
    x = c
    while x != bot.pos:
        assert st.matrix[x].is_void()
        path.append(x)
        x = table[x]
    path.append(bot.pos)
    return list(reversed(path))

def back_to_base(st, bot):
    path = shortest_path(st, bot, Coord(0,0,0))
    if path is not None:
        compress(st, bot, path)
    
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

def old_algo(st):
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

if __name__ == '__main__':
    problem = int(sys.argv[1])
    st = state.State.create(problem=problem)
    old_algo(st)
    if st.harmonics is True:
        st.bots[0].flip()
    back_to_base(st, st.bots[0])
    st.bots[0].halt()
    st.step()
        
    print( st )
    filename = "submission/LA"+str(problem).zfill(3)+".nbt"
    sys.stderr.write('{}: {}\n'.format(filename, st.score) )
    print( 'energy: {}, default: {}, score: {:0.3f}/{:0.3f}'.format( st.energy, st.default_energy, st.score, st.score_max ) )
    data = commands.export_nbt( st.trace )
    with open(filename, "wb") as file:
        file.write(data)

    
