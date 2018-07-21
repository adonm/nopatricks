#!/usr/bin/env python3
import state
import commands
from coord import Coord, diff, UP, DOWN, LEFT, RIGHT, FORWARD, BACK
trace = []

import sys

def fill(bot, st): # find all lower coords in model, and fill them, else just return false
    print(bot)
    for c in bot.pos.adjacent(st.matrix.size):
        if c.y != bot.pos.y -1:
            continue
        if not st.matrix[c].is_full() and st.matrix[c].is_model():
            bot.fill(bot.pos - c)
            break
    else:
        return False

def move(bot, st):
    if bot.pos.y == 0:
        bot.smove(UP)
        return True
    plane = st.matrix.yplane(bot.pos.y - 1)
    target, distance = False, False
    count = 0
    for c in plane:
        if plane[c].is_model() and not plane[c].is_full():
            count += 1
            coord = plane.keygen(c)
            coord.y = coord.y + 1
            curdis = (coord - bot.pos).mlen()
            if not distance or distance > curdis:
                target, distance = coord, curdis
    if count == 0:
        bot.smove(UP)
        return True
    movedir = target - bot.pos
    if movedir.dx > movedir.dz:
        bot.smove(diff(dx=movedir.dx % 15, dy=0, dz=0))
    else:
        bot.smove(diff(dz=movedir.dz % 15, dx=0, dy=0))
    return True

if __name__ == '__main__':
    st = state.State.create(problem=1)
    while st.matrix.ngrounded < st.matrix.nmodel:
        for bot in st.bots:
            while fill(bot, st): pass # fill completely
            move(bot, st) # then move each bot once
    
    data = commands.export_nbt( st.trace )
    with open("testcell01.nbt", "wb") as file:
        file.write(data)

