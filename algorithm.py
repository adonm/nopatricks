#!/usr/bin/env python3
import state
import commands
from coord import Coord, diff, UP, DOWN, LEFT, RIGHT, FORWARD, BACK
import sys

def back_to_base(st):
    bot = st.bots[0]
    while bot.pos.z != 0:
        bot.smove(BACK)
    while bot.pos.x != 0:
        bot.smove(RIGHT)
    while bot.pos.y != 0:
        bot.smove(DOWN)
    

if __name__ == '__main__':
    problem = int(sys.argv[1])
    st = state.State.create(problem=problem)
    bot = st.bots[0]
    bot.smove(UP)
    zdir = 1
    xdir = 1
    while bot.pos.y < st.R-1 and not st.is_model_finished():
        while (xdir == 1 and bot.pos.x < st.R-1) or (xdir == -1 and bot.pos.x > 0):
            while (zdir == 1 and bot.pos.z < st.R-1) or (zdir==-1 and bot.pos.z > 0):
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

    
