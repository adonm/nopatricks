#!/usr/bin/env python3
import state
import commands
from coord import Coord, diff
trace = []

def player():
    pass

UP = diff(0, 1, 0)
DOWN = diff(0, -1, 0)
LEFT = diff(1, 0, 0)
RIGHT = diff(-1, -1, 0)
FORWARD = diff(0, 0, 1)
BACK = diff(0, 0, -1)


if __name__ == '__main__':
    st = state.State(problem=1)
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
    