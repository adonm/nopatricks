#!/usr/bin/env python3
import state
import commands

def player():
    pass

if __name__ == '__main__':
    mat = state.Matrix()
    mat.load('problemsL/LA001_tgt.mdl')
    st = state.State(matrix=mat)
    cmd = commands.read_nbt_iter( open('dfltTracesL/LA001.nbt', 'rb').read() )
    
    for c in cmd:
        if type( c ) == commands.Halt:
            pass

