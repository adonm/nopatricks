#!/usr/bin/env python3
import unittest
from coord import Coord
from state import *
from algorithm import compress
class TestAlgo(unittest.TestCase):

    def test_compress(self):
        state = State(matrix=[])
        bot = Bot(state, "asdf", Coord(0,0,0), [])
        compress(state, bot, [Coord(0,0,0), Coord(0,1,0), Coord(0,1,1)])

if __name__ == '__main__':
    unittest.main()
