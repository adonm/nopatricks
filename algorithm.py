#!/usr/bin/env python3
import state
import commands
from coord import Coord, diff, UP, DOWN, LEFT, RIGHT, FORWARD, BACK
trace = []

import sys


if __name__ == '__main__':
    st = state.State.create(problem=1)
    bot = st.bots[0]
    bot.smove(UP)
    zdir = 1
    xdir = 1
    while bot.pos.y < st.R-1:
        while bot.pos.x < st.R-1:
            while bot.pos.z < st.R-1:
                bot.smove(FORWARD.mul(zdir))
                below = st.matrix[bot.pos + DOWN]
                if below.is_model() and below.is_void():
                    bot.fill(DOWN)
            bot.smove(LEFT.mul(xdir))
            zdir *= -1
        bot.smove(UP)
        xdir *= -1
    
    
    data = commands.export_nbt( st.trace )
    with open("test01.nbt", "wb") as file:
        file.write(data)

    
