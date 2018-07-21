#!/usr/bin/env python3
import unittest
from coord import Coord
from state import *
from algorithm import compress, shortest_path
class TestAlgo(unittest.TestCase):

    def test_shortest(self):
        st = State.create(problem=86)
        st.bots[0].pos = Coord(38, 40, 38)
        path = shortest_path(st, st.bots[0], Coord(37, 40, 38))
        print(path)

    def test_compress(self):
        state = State(matrix=[])
        bot = Bot(state, "asdf", Coord(0,0,0), [])
        compress(state, bot, [Coord(0,0,0), Coord(0,1,0), Coord(0,1,1)])

if __name__ == '__main__':
    unittest.main()
